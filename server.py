from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import json
import hashlib
import uuid
import re
import random
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

# Unified data file for both Web and Telegram
data_file = 'unified_users.json'
uploads_dir = 'uploads'

allowed_avatar_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}

# Helper function to load users data
def load_users():
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure proper structure
            if 'web_users' not in data:
                return {'web_users': data, 'tg_links': {}, 'clans': {}}
            return data
    return {'web_users': {}, 'tg_links': {}, 'clans': {}}

# Helper function to save users data
def save_users(users_data):
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

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

def _generate_learning_content_kz(topic: str, source_urls=None, level=1):
    # Level 1: Kazakh folk tales and legends
    if level == 1:
        folktales = {
            "Ертөстік": {
                "text_kz": "Ертөстік — қазақ ертегілерінің ең танымал батыры. Ол жер асты патшалығына түсіп, айдаһармен шайқасады. Оның аты — Шалқұйрық, ол иесіне әрқашан көмектеседі. Ертегіде достық, батылдық пен адалдық туралы айтылады.",
                "questions_kz": ["Ертөстіктің аты кім?", "Ол кіммен шайқасты?", "Ертөстіктің тұлпарының аты қандай?", "Бұл ертегі не туралы?", "Ертөстік қайда барды?"],
                "options_count": 2,
                "topic": "Ертөстік батыр",
                "level": 1
            },
            "Алдар Көсе": {
                "text_kz": "Алдар Көсе — қазақ ауыз әдебиетінің кейіпкері. Ол өте ақылды және қу адам болған. Ол байларды алдап, кедейлерге көмектескен. Оның тоны жыртық болса да, ол ешқашан мұңаймаған. Алдар Көсе халықтың сүйікті кейіпкері.",
                "questions_kz": ["Алдар Көсе қандай адам?", "Ол кімдерге көмектесті?", "Оның тоны қандай болды?", "Алдар Көсе несімен танымал?", "Халық оны жақсы көре ме?"],
                "options_count": 2,
                "topic": "Алдар Көсе хикаялары",
                "level": 1
            }
        }
        content = folktales.get(topic) or random.choice(list(folktales.values()))
        return content

    # Level 4: Official texts (long, hard)
    if level == 4:
        official_sources = {
            "Қазақ хандығының құрылуы (Ресми)": {
                "text_kz": "Қазақ хандығының құрылуы — Орталық Азия тарихындағы бетбұрысты кезең. XV ғасырдың ортасында (1465 ж.) Керей мен Жәнібек сұлтандар Әбілқайыр хандығынан бөлініп, Моғолстанның батысындағы Шу мен Қозыбасы өңіріне қоныс аударды. Бұл оқиға қазақ этносының бірігуіне және дербес мемлекеттілігінің қалыптасуына негіз болды. Тарихи деректерге сүйенсек, «қазақ» атауы еркіндікті сүйетін, өз алдына ел болғысы келетін халықтың рухын білдіреді. Хандық құрылғаннан кейін оның шекарасы кеңейіп, Сырдария бойындағы қалалар үшін күрес басталды. Бұл процесс бірнеше онжылдыққа созылып, Қасым ханның тұсында мемлекет қуатты державаға айналды.",
                "questions_kz": [
                    "Қазақ хандығының құрылуына қандай саяси жағдай түрткі болды?",
                    "Керей мен Жәнібек қай өңірге алғаш қоныс аударды?",
                    "«Қазақ» сөзінің тарихи контекстегі мағынасы қандай?",
                    "Хандықтың нығаюына қай ханның үлесі зор болды?",
                    "Әбілқайыр хандығынан бөлінудің басты себебі не?",
                    "XV ғасырдағы Моғолстанның рөлі қандай болды?",
                    "Хандық шекарасының кеңеюі қай бағытта жүрді?",
                    "Сырдария қалаларының стратегиялық маңызы неде?",
                    "Қазақ этносының қалыптасуы қай кезеңде аяқталды?",
                    "Мемлекеттің халықаралық деңгейдегі беделі қашан артты?",
                    "Хандық құрылымындағы ұлыстық жүйенің ерекшелігі?",
                    "Шу мен Қозбасы өңірлерінің таңдалу себебі?",
                    "Керей мен Жәнібектің Әбілқайырмен конфликтісінің сипаты?",
                    "Хандықтың туы мен рәміздері туралы деректер бар ма?",
                    "Қазақ хандығының Орта Азиядағы көршілерімен қарым-қатынасы?"
                ],
                "options_count": 4,
                "topic": "Қазақ хандығының құрылу тарихы",
                "level": 4
            }
        }
        content = official_sources.get(topic) or list(official_sources.values())[0]
        return content

    # Default / Other levels
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

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'BATYR BOL'})

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
        
        all_data = load_users()
        web_users = all_data.get('web_users', {})

        # Check in unified data
        if email in web_users:
            user = web_users[email]
            # Simple password check (in production use real hash)
            if user.get('password') == password or (email == 'test@batyrbol.kz' and password == 'batyr123'):
                return jsonify({'success': True, 'user': user})

        # Hardcoded test account fallback
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
        
        return jsonify({'success': False, 'message': 'Неверный email или пароль.'}), 401
        
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
        level = int(payload.get('level', 1))

        if not topic and level == 1:
            topic = random.choice(["Ертөстік", "Алдар Көсе"])
        elif not topic and level == 4:
            topic = "Қазақ хандығының құрылуы (Ресми)"

        if not topic:
            return jsonify({'success': False, 'message': 'Тақырып міндетті / Topic required'}), 400

        content = _generate_learning_content_kz(topic, source_urls=source_urls, level=level)
        return jsonify({'success': True, 'content': content})
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

@app.route('/api/clans/create', methods=['POST'])
def create_clan():
    try:
        data = request.get_json()
        email = data.get('email')
        clan_name = data.get('name')
        
        all_data = load_users()
        if clan_name in all_data['clans']:
            return jsonify({'success': False, 'message': 'Клан с таким именем уже существует'}), 400
            
        all_data['clans'][clan_name] = {
            'leader': email,
            'members': [email],
            'xp': 0
        }
        if email in all_data['web_users']:
            all_data['web_users'][email]['clan'] = clan_name
            
        save_users(all_data)
        return jsonify({'success': True, 'message': f'Клан {clan_name} создан'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clans/join', methods=['POST'])
def join_clan():
    try:
        data = request.get_json()
        email = data.get('email')
        clan_name = data.get('name')
        
        all_data = load_users()
        if clan_name not in all_data['clans']:
            return jsonify({'success': False, 'message': 'Клан не найден'}), 404
            
        if email not in all_data['clans'][clan_name]['members']:
            all_data['clans'][clan_name]['members'].append(email)
            if email in all_data['web_users']:
                all_data['web_users'][email]['clan'] = clan_name
                
        save_users(all_data)
        return jsonify({'success': True, 'message': f'Вы вступили в клан {clan_name}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clans/list', methods=['GET'])
def list_clans():
    all_data = load_users()
    return jsonify({'success': True, 'clans': all_data.get('clans', {})})

@app.route('/api/duels/challenge', methods=['POST'])
def challenge_duel():
    try:
        data = request.get_json()
        from_email = data.get('from')
        to_user = data.get('to') # can be email or name
        
        # Simple placeholder for duel initiation
        return jsonify({'success': True, 'message': f'Вызов брошен пользователю {to_user}!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print(f"🚀 [SERVER] Flask запущен на http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
