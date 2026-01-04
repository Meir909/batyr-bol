from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import json
import hashlib
import uuid
import re
from html.parser import HTMLParser
from urllib.parse import urlparse
import requests
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

data_file = 'users_data.json'
uploads_dir = 'uploads'

allowed_avatar_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}

# Helper function to load users data
def load_users():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Helper function to save users data
def save_users(users):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

app = Flask(__name__)

os.makedirs(uploads_dir, exist_ok=True)

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'noscript'}:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'noscript'} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        text = (data or '').strip()
        if text:
            self._chunks.append(text)

    def get_text(self):
        return ' '.join(self._chunks)


def _is_allowed_source_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {'http', 'https'}:
            return False
        host = (parsed.hostname or '').lower()
        allowed_domains = {
            'e-history.kz',
            'www.e-history.kz',
            'gov.kz',
            'www.gov.kz',
            'akorda.kz',
            'www.akorda.kz',
            'assembly.kz',
            'www.assembly.kz',
            'nationalmuseum.kz',
            'www.nationalmuseum.kz',
        }
        return host in allowed_domains
    except Exception:
        return False


def _fetch_official_texts(urls):
    texts = []
    used_urls = []
    for url in urls:
        if not _is_allowed_source_url(url):
            continue
        try:
            r = requests.get(url, timeout=15, headers={'User-Agent': 'BATYR-BOL/1.0'})
            if r.status_code != 200:
                continue
            parser = _HTMLTextExtractor()
            parser.feed(r.text)
            text = parser.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) < 400:
                continue
            texts.append(text)
            used_urls.append(url)
        except Exception:
            continue
    return texts, used_urls


def _generate_image_prompt(topic: str, text_kz: str):
    """Generate an image prompt based on the topic and text content."""
    prompt = (
        'Based on this Kazakh history topic and text, create a short English image prompt '
        'for generating an educational illustration. The prompt should describe a historical scene '
        'related to the topic. Keep it under 100 words. Only return the prompt text, nothing else.\n\n'
        f'Topic: {topic}\n'
        f'Text: {text_kz}\n'
    )
    return _gemini_generate(prompt).strip()


def _generate_image_url(image_prompt: str):
    """Generate image URL - returns None since Pollinations.ai is no longer available."""
    # Pollinations.ai has moved/changed, so we disable image generation for now
    # In the future, can integrate with other services like DALL-E, Stable Diffusion, etc.
    return None


def _gemini_generate(prompt: str):
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY not configured')

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    resp = requests.post(
        f'{url}?key={api_key}',
        json={
            'contents': [
                {
                    'parts': [{'text': prompt}]
                }
            ]
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f'Gemini API error: {resp.status_code}')
    data = resp.json()
    return data['candidates'][0]['content']['parts'][0]['text']


def _load_fallback_content():
    """Load pre-made missions from fallback_content.json"""
    fallback_file = os.path.join(os.path.dirname(__file__), 'fallback_content.json')
    if os.path.exists(fallback_file):
        with open(fallback_file, 'r', encoding='utf-8') as f:
            return json.load(f).get('missions', [])
    return []


def _get_fallback_mission(topic: str = None, level: int = None):
    """Get a fallback mission, optionally filtered by topic and level"""
    import random
    missions = _load_fallback_content()
    if not missions:
        return None
    
    # Filter by level if specified
    if level:
        level_missions = [m for m in missions if m.get('level', 2) == level]
        if level_missions:
            missions = level_missions
    
    if topic:
        matching = [m for m in missions if topic.lower() in m.get('topic', '').lower()]
        if matching:
            mission = random.choice(matching)
        else:
            mission = random.choice(missions)
    else:
        mission = random.choice(missions)
    
    # Generate image URL from prompt
    image_url = _generate_image_url(mission.get('image_prompt', ''))
    
    return {
        'text_kz': mission.get('text_kz', ''),
        'questions_kz': mission.get('questions_kz', []),
        'text_ru': mission.get('text_ru', ''),
        'questions_ru': mission.get('questions_ru', []),
        'sources': [],
        'image_url': image_url,
        'topic': mission.get('topic', ''),
        'level': mission.get('level', 2)
    }


def _generate_learning_content_kz(topic: str, source_urls=None):
    # First try to use fallback content (always works, no API needed)
    fallback = _get_fallback_mission(topic)
    if fallback:
        return fallback
    
    # If no fallback available, try Gemini API
    curated_sources = {
        'Қазақ хандығы': [
            'https://e-history.kz/kz',
        ],
        'Абылай хан': [
            'https://e-history.kz/kz',
        ],
        'Тәуке хан': [
            'https://e-history.kz/kz',
        ],
        'Қазақстан тәуелсіздігі': [
            'https://www.akorda.kz',
            'https://www.gov.kz',
        ],
    }

    urls = curated_sources.get(topic, ['https://e-history.kz/kz'])
    if isinstance(source_urls, list) and source_urls:
        urls = [u for u in source_urls if isinstance(u, str)]

    source_texts, used_urls = _fetch_official_texts(urls)
    
    if source_texts:
        materials = '\n\n'.join([t[:4000] for t in source_texts])
        prompt = (
            'Сен Қазақстан тарихы және мәдениеті бойынша оқу контентін жасайтын көмекшісің.\n'
            'Тек төмендегі ресми дереккөздерден берілген материалға сүйен.\n'
            'Ешқандай басқа білімді, Википедияны, жалпы білімді қолданба.\n\n'
            f'Тақырып: {topic}\n\n'
            'Материал (ресми сайттардан алынған үзінділер):\n'
            f'{materials}\n\n'
            'Тапсырма:\n'
            '1) Қазақ тілінде 5-6 сөйлемнен тұратын қысқа мәтін жаз.\n'
            '2) Осы мәтін бойынша ғана 5 сұрақ құр (сұрақтар мәтіндегі ақпаратпен ғана жауап берілетін болсын).\n'
            '3) Нәтижені JSON түрінде қайтар: {"text_kz": "...", "questions_kz": ["..."], "sources": ["..."]}.\n'
            '4) sources массивінде тек осы сұраныста берілген URL-дарды қолдан.\n'
        )
    else:
        prompt = (
            'Сен Қазақстан тарихы және мәдениеті бойынша оқу контентін жасайтын көмекшісің.\n'
            f'Тақырып: {topic}\n\n'
            'Тапсырма:\n'
            '1) Қазақ тілінде 5-6 сөйлемнен тұратын қысқа білім беру мәтінін жаз.\n'
            '2) Осы мәтін бойынша 5 сұрақ құр.\n'
            '3) Нәтижені JSON түрінде қайтар: {"text_kz": "...", "questions_kz": ["..."], "sources": []}.\n'
        )

    raw = _gemini_generate(prompt)
    m = re.search(r'\{[\s\S]*\}', raw)
    if not m:
        raise RuntimeError('Gemini response parse error')
    result = json.loads(m.group(0))
    text_kz = result.get('text_kz')
    questions_kz = result.get('questions_kz')
    if not isinstance(text_kz, str) or not text_kz.strip():
        raise RuntimeError('Invalid text_kz')
    if not isinstance(questions_kz, list) or not all(isinstance(q, str) for q in questions_kz):
        raise RuntimeError('Invalid questions_kz')
    result['sources'] = [u for u in used_urls if _is_allowed_source_url(u)]
    
    # Generate image based on the content
    try:
        image_prompt = _generate_image_prompt(topic, text_kz)
        result['image_url'] = _generate_image_url(image_prompt)
        result['image_prompt'] = image_prompt
    except Exception:
        result['image_url'] = None
        result['image_prompt'] = None
    
    return result


def _translate_kz_to_ru(text_kz: str):
    prompt = (
        'Қазақ тіліндегі мәтінді орыс тіліне дәл аудар.\n'
        'Мағынаны сақта, аттар мен даталарды өзгертпе.\n'
        'Тек аударманы қайтар, ешқандай түсіндірме қоспа.\n\n'
        f'{text_kz}'
    )
    return _gemini_generate(prompt).strip()


@app.route('/')
def index():
    return send_from_directory('.', 'intro.html')

# Страница игры
@app.route('/game')
def game():
    return send_from_directory('.', 'igra.html')

# API endpoint for user registration
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        avatar_url = data.get('avatarUrl')

        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'Все поля обязательны для заполнения'}), 400

        users = load_users()

        # Check if user already exists
        if email in users:
            return jsonify({'success': False, 'message': 'Пользователь с таким email уже существует'}), 400

        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Create new user
        user_id = f'user_{int(datetime.now().timestamp() * 1000)}'
        users[email] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'avatarUrl': avatar_url,
            'xp': 0,
            'level': 1,
            'language': 'kk',
            'completedMissions': [],
            'skillLevel': 'beginner',
            'historyAnswers': [],
            'voiceMissionsCompleted': 0,
            'streak': 1,
            'createdAt': datetime.now().isoformat(),
            'lastLogin': datetime.now().isoformat()
        }

        save_users(users)

        # Return user data without password
        user_data = users[email].copy()
        del user_data['password_hash']

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(uploads_dir, filename)

def _avatar_ext_from_filename(filename: str):
    _, ext = os.path.splitext(filename)
    ext = (ext or '').lower()
    if ext in allowed_avatar_extensions:
        return ext
    return None

@app.route('/api/profile/avatar', methods=['POST'])
def upload_avatar():
    try:
        email = request.form.get('email')
        file = request.files.get('avatar')

        if not email:
            return jsonify({'success': False, 'message': 'Email обязателен'}), 400
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'Файл аватара обязателен'}), 400

        users = load_users()
        if email not in users:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404

        ext = _avatar_ext_from_filename(file.filename)
        if not ext:
            return jsonify({'success': False, 'message': 'Неподдерживаемый формат аватара'}), 400

        safe_name = secure_filename(os.path.splitext(file.filename)[0]) or 'avatar'
        filename = f"{safe_name}_{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(uploads_dir, filename)
        file.save(save_path)

        users[email]['avatarUrl'] = f"/uploads/{filename}"
        save_users(users)

        user_data = users[email].copy()
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/profile/avatar/batyr', methods=['POST'])
def generate_batyr_avatar():
    try:
        data = request.get_json() or {}
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'Email обязателен'}), 400

        users = load_users()
        if email not in users:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404

        svg = _batyr_svg(email)
        filename = f"batyr_{uuid.uuid4().hex}.svg"
        save_path = os.path.join(uploads_dir, filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(svg)

        users[email]['avatarUrl'] = f"/uploads/{filename}"
        save_users(users)

        user_data = users[email].copy()
        if 'password_hash' in user_data:
            del user_data['password_hash']

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API endpoint for user login
@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email и пароль обязательны'}), 400

        users = load_users()

        # Check if user exists
        if email not in users:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404

        user = users[email]

        if 'avatarUrl' not in user:
            user['avatarUrl'] = None

        # Check password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user['password_hash']:
            return jsonify({'success': False, 'message': 'Неверный пароль'}), 401

        # Update last login
        user['lastLogin'] = datetime.now().isoformat()
        save_users(users)

        # Return user data without password
        user_data = user.copy()
        del user_data['password_hash']

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API endpoint for updating user profile
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        new_email = data.get('new_email')
        password = data.get('password')

        users = load_users()

        # Check if user exists
        if email not in users:
            return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404

        user = users[email]

        # Update fields
        if name:
            user['name'] = name

        if new_email and new_email != email:
            # Move user to new email key
            users[new_email] = user
            users[new_email]['email'] = new_email
            del users[email]
            email = new_email

        if password:
            # Hash new password
            user['password_hash'] = hashlib.sha256(password.encode()).hexdigest()

        # Save updated users
        save_users(users)

        # Return updated user data without password
        user_data = users[email].copy()
        del user_data['password_hash']

        if 'avatarUrl' not in user_data:
            user_data['avatarUrl'] = None

        return jsonify({'success': True, 'user': user_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/content/generate', methods=['POST'])
def generate_learning_content():
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip()
        source_urls = payload.get('source_urls')

        if not topic:
            return jsonify({'success': False, 'message': 'Тақырып міндетті / Topic required'}), 400

        return jsonify({'success': True, 'content': _generate_learning_content_kz(topic, source_urls=source_urls)})
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Gemini JSON decode error'}), 502
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/content/translate', methods=['POST'])
def translate_content():
    try:
        payload = request.get_json() or {}
        text_kz = (payload.get('text_kz') or '').strip()
        if not text_kz:
            return jsonify({'success': False, 'message': 'text_kz required'}), 400

        return jsonify({'success': True, 'text_ru': _translate_kz_to_ru(text_kz)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Статические файлы (CSS, JS, изображения)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

_bot_users = {}

async def _bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _bot_users[uid] = {'lang': 'kk'}
    await update.message.reply_text(
        '🇰🇿 BATYR BOL\n\n'
        'Командалар:\n'
        '/missions — миссия алу\n'
        '/kz — Қазақша\n'
        '/ru — Русский'
    )

async def _bot_set_kz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _bot_users.setdefault(uid, {})['lang'] = 'kk'
    await update.message.reply_text('✅ Қазақ тілі таңдалды')

async def _bot_set_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _bot_users.setdefault(uid, {})['lang'] = 'ru'
    await update.message.reply_text('✅ Русский язык выбран')

async def _bot_missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = _bot_users.get(uid, {}).get('lang', 'kk')
    topic = 'Абылай хан'
    if context.args:
        topic = ' '.join(context.args).strip()

    result = _generate_learning_content_kz(topic)
    text = result.get('text_kz', '')
    questions = result.get('questions_kz', [])

    if lang == 'ru':
        text = _translate_kz_to_ru(text)
        if questions:
            translated = _translate_kz_to_ru('\n'.join(questions))
            questions = [q.strip() for q in translated.split('\n') if q.strip()]

    msg = f"📖 {topic}\n\n{text}\n\n❓ Сұрақтар:\n"
    for i, q in enumerate(questions[:5], 1):
        msg += f"{i}. {q}\n"
    if result.get('sources'):
        msg += "\n🔗 Sources:\n" + "\n".join(result['sources'][:5])

    await update.message.reply_text(msg)

def _run_telegram_bot():
    import asyncio
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        return

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', _bot_start))
    application.add_handler(CommandHandler('kz', _bot_set_kz))
    application.add_handler(CommandHandler('ru', _bot_set_ru))
    application.add_handler(CommandHandler('missions', _bot_missions))
    
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Telegram bot error: {e}")

if __name__ == '__main__':
    # Get host and port from environment variables or use defaults
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    t = threading.Thread(target=_run_telegram_bot, daemon=True)
    t.start()

    print("🚀 Сервер запущен!")
    print(f"📖 Лендинг: http://{host}:{port}")
    print(f"🎮 Игра: http://{host}:{port}/game")
    print("🛑 Для остановки нажмите Ctrl+C")
    app.run(host=host, port=port, debug=debug)