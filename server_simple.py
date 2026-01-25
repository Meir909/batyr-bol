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
        if self._skip_depth == 0:
            self._chunks.append(data.strip())

    def get_text(self):
        return ' '.join(filter(None, self._chunks))

def _extract_text_from_html(html_content):
    parser = _HTMLTextExtractor()
    parser.feed(html_content)
    return parser.get_text()

def _is_allowed_source_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(allowed in domain for allowed in [
        'e-history.kz', 'akorda.kz', 'gov.kz', 
        'museum.kz', 'nationalmuseum.kz', 'edu.kz'
    ])

def _fetch_official_texts(urls):
    source_texts = []
    used_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in urls[:3]:
        if not _is_allowed_source_url(url):
            continue
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                text = _extract_text_from_html(response.text)
                if len(text) > 200:
                    source_texts.append(text)
                    used_urls.append(url)
        except Exception:
            continue
    
    return source_texts, used_urls

def _gemini_generate(prompt):
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY', '').strip()
        if not gemini_api_key:
            return json.dumps({
                "text_kz": "Қазақ хандығы - қазақ халқының мемлекеттігінің негізі қаланған тарихи оқиға. 1465 жылы Қазақ хандығы құрылды.",
                "questions_kz": [
                    "Қазақ хандығы қашан құрылды?",
                    "Қазақ хандығының негізін қалған хандар кімдер?",
                    "Қазақ хандығы қандай маңызға ие?"
                ],
                "sources": []
            })
        
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return json.dumps({
            "text_kz": "Қазақ хандығы - қазақ халқының мемлекеттігінің негізі қаланған тарихи оқиға. 1465 жылы Қазақ хандығы құрылды.",
            "questions_kz": [
                "Қазақ хандығы қашан құрылды?",
                "Қазақ хандығының негізін қалған хандар кімдер?",
                "Қазақ хандығы қандай маңызға ие?"
            ],
            "sources": []
        })

def _get_fallback_mission(topic):
    fallback_content = {
        'Қазақ хандығы': {
            'text_kz': 'Қазақ хандығы - қазақ халқының мемлекеттігінің негізі қаланған тарихи оқиға. 1465 жылы Қазақ хандығы құрылды. Керей мен Жәнібек хандар қазақ руларын біріктіріп, жаңа мемлекет құрды.',
            'questions_kz': [
                'Қазақ хандығы қашан құрылды?',
                'Қазақ хандығының негізін қалған хандар кімдер?',
                'Қазақ хандығы қандай маңызға ие?'
            ],
            'text_ru': 'Казахское ханство - историческое событие, положившее основу государственности казахского народа. В 1465 году было создано Казахское ханство. Хане Керей и Жанибек объединили казахские роды и создали новое государство.',
            'questions_ru': [
                'Когда было создано Казахское ханство?',
                'Кто основал Казахское ханство?',
                'Какое значение имеет Казахское ханство?'
            ],
            'topic': 'Қазақ хандығы',
            'level': 2,
            'image_prompt': 'Казахские ханы Керей и Жанибек на фоне степей, средневековый Казахстан'
        },
        'Абылай хан': {
            'text_kz': 'Абылай хан - қазақ халқының ұлы батыры, мемлекет қайраткері. Ол 18 ғасырда қазақ жүздерін біріктіріп, жоңғар шапқыншылығына қарсы күресті. Абылай хан - дана басшы, елдің бірлігіне көп еңбек сіңірген.',
            'questions_kz': [
                'Абылай хан қашан өмір сүрген?',
                'Абылай хан қандай қасиеттерге ие болды?',
                'Абылай ханның тарихи маңызы не?'
            ],
            'text_ru': 'Абылай хан - великий батыр и государственный деятель казахского народа. В 18 веке он объединил казахские жузы и боролся против джунгарских нашествий. Абылай хан - мудрый правитель, внесший большой вклад в единство народа.',
            'questions_ru': [
                'Когда жил Абылай хан?',
                'Какими качествами обладал Абылай хан?',
                'В чем историческое значение Абылай хана?'
            ],
            'topic': 'Абылай хан',
            'level': 3,
            'image_prompt': 'Абылай хан в батырских доспехах на фоне казахских степей, исторический портрет'
        }
    }
    
    return fallback_content.get(topic)

def _generate_image_url(prompt):
    return None

def _generate_image_prompt(topic, text):
    return f"Историческая иллюстрация: {topic}. Казахстан, средневековье."

def _generate_learning_content_kz(topic: str, source_urls=None):
    fallback = _get_fallback_mission(topic)
    if fallback:
        return fallback
    
    return {
        'text_kz': f'{topic} - қазақ халқының тарихындағы маңызды оқиға. Бұл тақырып Қазақстан тарихында зор орын алады.',
        'questions_kz': [
            f'{topic} туралы не білесіз?',
            f'{topic} қандай маңызға ие?',
            f'{topic} қашан болған?'
        ],
        'text_ru': f'{topic} - важное событие в истории казахского народа. Эта тема занимает большое место в истории Казахстана.',
        'questions_ru': [
            f'Что вы знаете о {topic}?',
            f'Какое значение имеет {topic}?',
            f'Когда произошло {topic}?'
        ],
        'sources': [],
        'topic': topic,
        'level': 2
    }

def _translate_kz_to_ru(text_kz: str):
    return f'Перевод: {text_kz}'

@app.route('/')
def index():
    return send_from_directory('.', 'intro.html')

@app.route('/game')
def game():
    return send_from_directory('.', 'igra.html')

# Simple login with test account only
@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Test account only
        if email == 'test@batyrbol.kz' and password == 'batyr123':
            user_data = {
                'id': 'test_user',
                'name': 'Батыр Бол',
                'email': 'test@batyrbol.kz',
                'xp': 100,
                'level': 5,
                'energy': 100,
                'streak': 7,
                'avatarUrl': None,
                'lastLogin': datetime.now().isoformat(),
                'completedMissions': [],
                'achievements': []
            }
            return jsonify({'success': True, 'user': user_data})
        
        return jsonify({'success': False, 'message': 'Неверный email или пароль. Используйте: test@batyrbol.kz / batyr123'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Disable registration
@app.route('/api/register', methods=['POST'])
def register_user():
    return jsonify({'success': False, 'message': 'Регистрация отключена. Используйте тестовый аккаунт: test@batyrbol.kz / batyr123'}), 403

@app.route('/api/content/generate', methods=['POST'])
def generate_learning_content():
    try:
        payload = request.get_json() or {}
        topic = (payload.get('topic') or '').strip()
        source_urls = payload.get('source_urls')

        if not topic:
            return jsonify({'success': False, 'message': 'Тақырып міндетті / Topic required'}), 400

        return jsonify({'success': True, 'content': _generate_learning_content_kz(topic, source_urls=source_urls)})
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

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# Telegram bot functions (simplified)
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

def _run_telegram_bot():
    import asyncio
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        return

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler('start', _bot_start))
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Telegram bot error: {e}")

if __name__ == '__main__':
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
