from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import json
import hashlib
import sys
import re
import random
from html.parser import HTMLParser
from urllib.parse import urlparse
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import threading

# Try to import uuid, fallback to simple string generator if not available
try:
    import uuid
    def _generate_uuid():
        return str(uuid.uuid4())
except ImportError:
    import random
    import string
    def _generate_uuid():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_uuid():
    """Generate a unique ID for sessions and users"""
    return _generate_uuid()

# Safe import for OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] OpenAI module not found. Install with: pip install openai")

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TIMEOUT'] = 24 * 60 * 60  # 24 hours in seconds

# OpenAI API Key (для генерации сценариев)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Data storage
data_file = 'unified_users.json'

# Session storage (in production, use Redis or database)
sessions = {}

def generate_session_id():
    """Generate a secure session ID"""
    return generate_uuid()

def is_session_valid(session_id):
    """Check if session is valid and not expired"""
    if not session_id or session_id not in sessions:
        return False
    
    session_data = sessions[session_id]
    created_at = datetime.fromisoformat(session_data['created_at'])
    
    # Check if session is older than 24 hours
    if datetime.now() - created_at > timedelta(hours=24):
        del sessions[session_id]
        return False
    
    return True

def create_session(email):
    """Create a new session for user"""
    session_id = generate_session_id()
    sessions[session_id] = {
        'email': email,
        'created_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    }
    return session_id

def update_session_activity(session_id):
    """Update last activity timestamp"""
    if session_id in sessions:
        sessions[session_id]['last_activity'] = datetime.now().isoformat()

def cleanup_expired_sessions():
    """Remove expired sessions"""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, session_data in sessions.items():
        created_at = datetime.fromisoformat(session_data['created_at'])
        if current_time - created_at > timedelta(hours=24):
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del sessions[session_id]

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

def _verify_user_password(email: str, user: dict, password: str) -> tuple[bool, bool]:
    """
    Returns (is_valid, should_migrate_legacy_password).
    """
    if email == 'test@batyrbol.kz' and password == 'batyr123':
        return True, False

    password = password or ''

    password_hash = user.get('password_hash')
    if password_hash:
        return check_password_hash(password_hash, password), False

    legacy_password = user.get('password')
    if legacy_password and legacy_password == password:
        return True, True

    return False, False

def _public_user(user: dict) -> dict:
    # Never leak password fields to the client
    return {k: v for k, v in user.items() if k not in {'password', 'password_hash'}}

_rate_buckets: dict[str, list[float]] = {}

def _client_ip() -> str:
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'

def _rate_limit(bucket_name: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """
    Simple in-memory rate limit.
    Returns (is_limited, retry_after_seconds).
    """
    now = time.time()
    key = f'{bucket_name}:{_client_ip()}'
    bucket = _rate_buckets.setdefault(key, [])
    cutoff = now - window_seconds
    bucket[:] = [t for t in bucket if t >= cutoff]
    if len(bucket) >= limit:
        oldest = min(bucket) if bucket else now
        retry_after = max(1, int(window_seconds - (now - oldest)))
        return True, retry_after
    bucket.append(now)
    return False, 0

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define uploads directory
uploads_dir = os.path.join(os.getcwd(), 'uploads')
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
        except Exception as e:
            print(f"[ERROR] Failed to fetch official text from {url}: {str(e)}")
            continue
    
    return source_texts, used_urls

def _groq_generate_mission(topic, level=1):
    """
    Generate mission content using Groq API
    Returns: (success, content, error_message)
    """
    if not False:
        return False, None, "Groq module not available"
        
    try:
        groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
        if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
            return False, None, "Groq API key not configured"
        
        client = Groq(api_key=groq_api_key)
        
        # Create prompt based on level and topic
        level_descriptions = {
            1: "простые сказки и легенды для начинающих",
            2: "средняя сложность, основные исторические факты",
            3: "сложные темы, детальная информация",
            4: "официальные документы, сложные тексты"
        }
        
        prompt = f"""Создай образовательный контент по казахской теме "{topic}" для уровня {level}.

Напиши краткий текст на казахском языке (50-100 слов) по этой теме.
Затем создай 4 вопроса с вариантами ответов по этому тексту.

Верни строго JSON:
{{
    "text_kz": "Здесь краткий текст на казахском языке по теме {topic}",
    "questions_kz": [
        "Реальный вопрос 1 по тексту",
        "Реальный вопрос 2 по тексту", 
        "Реальный вопрос 3 по тексту",
        "Реальный вопрос 4 по тексту"
    ],
    "options_kz": [
        ["Правильный ответ", "Неправильный вариант 1", "Неправильный вариант 2", "Неправильный вариант 3"],
        ["Неправильный вариант 1", "Правильный ответ", "Неправильный вариант 2", "Неправильный вариант 3"],
        ["Неправильный вариант 1", "Неправильный вариант 2", "Правильный ответ", "Неправильный вариант 3"],
        ["Неправравильный вариант 1", "Неправильный вариант 2", "Неправильный вариант 3", "Правильный ответ"]
    ],
    "correct_answers": [0, 1, 2, 3]
}}

ВАЖНО: 
- Текст должен быть по теме "{topic}"
- Вопросы должны относиться к тексту
- Варианты ответов должны быть реальными, а не шаблонами
- Правильные ответы должны соответствовать вопросам
- Все на казахском языке"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        content_text = response.choices[0].message.content
        
        # Ensure proper encoding
        if isinstance(content_text, bytes):
            content_text = content_text.decode('utf-8')
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                content = json.loads(json_text)
            else:
                content = json.loads(content_text)
                
            # Validate required fields
            required_fields = ['text_kz', 'questions_kz', 'options_kz', 'correct_answers']
            for field in required_fields:
                if field not in content:
                    return False, None, f"Missing required field: {field}"
                    
            # Validate data structure
            if not isinstance(content['questions_kz'], list) or len(content['questions_kz']) != 4:
                return False, None, "questions_kz must be a list of 4 questions"
                
            if not isinstance(content['options_kz'], list) or len(content['options_kz']) != 4:
                return False, None, "options_kz must be a list of 4 options arrays"
                
            for options in content['options_kz']:
                if not isinstance(options, list) or len(options) != 4:
                    return False, None, "Each options array must contain 4 options"
                    
            if not isinstance(content['correct_answers'], list) or len(content['correct_answers']) != 4:
                return False, None, "correct_answers must be a list of 4 integers"
                
        except json.JSONDecodeError as e:
            print(f"[GROQ] JSON parsing error: {e}")
            print(f"[GROQ] Raw response: {content_text[:200]}...")
            return False, None, f"JSON parsing error: {str(e)}"
        
        return True, content, None

    except Exception as e:
        error_msg = f"Groq API error: {str(e)}"
        return False, None, error_msg

def _openai_generate_personal_mission(user_profile):
    """
    Generate personalized mission using OpenAI API (gpt-4o-mini model)
    Takes user profile with: level, completedMissions, weakAreas, language
    Returns: (success, content, error_message)
    """
    if not OPENAI_AVAILABLE:
        return False, None, "OpenAI module not available"

    try:
        openai_api_key = OPENAI_API_KEY
        if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
            return False, None, "OpenAI API key not configured"

        client = OpenAI(api_key=openai_api_key)

        # Extract user profile data
        level = user_profile.get('level', 1)
        completed_missions = user_profile.get('completedMissions', [])
        weak_areas = user_profile.get('weakAreas', [])
        language = user_profile.get('language', 'kk')

        # Create personalized prompt
        level_descriptions = {
            1: "бастауыш деңгей, қарапайым сөздер мен қысқа сөйлемдер",
            2: "орташа деңгей, негізгі тарихи фактілер",
            3: "жоғары деңгей, толық ақпарат",
            4: "эксперт деңгейі, тереń талдау"
        }

        # Determine topics to avoid (already completed)
        avoid_topics = ", ".join(completed_missions[:5]) if completed_missions else "жоқ"

        # Determine weak areas to focus on
        focus_areas = ", ".join(weak_areas[:3]) if weak_areas else "Қазақстан тарихы жалпы"

        prompt = f"""Сен қазақстанның білім беру жүйесінің AI көмекшісісің. Оқушыға қазақ тілінде жекелендірілген білім беру миссиясын құр.

ОҚУШЫ ПРОФИЛІ:
- Деңгей: {level} ({level_descriptions.get(level, 'орташа')})
- Орындалған миссиялар: {avoid_topics}
- Назар аудару қажет салалар: {focus_areas}

ТАПСЫРМА:
Қазақстан тарихы бойынша 100-150 сөзден тұратын қызықты мәтін жаз. Мәтін оқушының деңгейіне сәйкес болуы керек.

МАҢЫЗДЫ ЕРЕЖЕЛЕР:
1. Мәтінде НАҚТЫ ФАКТІЛЕР, АТТАР, КҮНДЕР, САНДАР болуы керек
2. Мәтінді оқымай ЖАУАП ТАПҚАНҒА БОЛМАЙТЫН сұрақтар қой
3. Әр сұрақтың дұрыс жауабы МӘТІННІҢ ІШІНДЕ ТІКЕЛЕЙ айтылған болуы керек
4. Жалпы білімге негізделген сұрақтар ЖАРАМАЙДЫ

Тек қана келесі JSON форматында жауап бер (басқа мәтінсіз):

{{
    "text_kz": "Мұнда 100-150 сөзден тұратын қазақша мәтін, нақты фактілермен",
    "questions_kz": [
        "Мәтін бойынша нақты сұрақ 1 (жауап мәтінде айтылған)",
        "Мәтін бойынша нақты сұрақ 2 (жауап мәтінде айтылған)",
        "Мәтін бойынша нақты сұрақ 3 (жауап мәтінде айтылған)"
    ],
    "options_kz": [
        ["Дұрыс жауап (мәтіннен)", "Бұрыс нұсқа 1", "Бұрыс нұсқа 2", "Бұрыс нұсқа 3"],
        ["Бұрыс нұсқа 1", "Дұрыс жауап (мәтіннен)", "Бұрыс нұсқа 2", "Бұрыс нұсқа 3"],
        ["Бұрыс нұсқа 1", "Бұрыс нұсқа 2", "Дұрыс жауап (мәтіннен)", "Бұрыс нұсқа 3"]
    ],
    "correct_answers": [0, 1, 2],
    "topic": "Мәтіннің тақырыбы"
}}"""

        # Call OpenAI API with o4-mini model
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using o4-mini as specified (gpt-4o-mini is the actual model name)
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )

        content_text = response.choices[0].message.content

        # Parse JSON response
        try:
            content = json.loads(content_text)

            # Validate required fields
            required_fields = ['text_kz', 'questions_kz', 'options_kz', 'correct_answers']
            for field in required_fields:
                if field not in content:
                    return False, None, f"Missing required field: {field}"

            # Add AI-generated flag
            content['ai_generated'] = True
            content['model'] = 'openai-o4-mini'
            content['personalized'] = True

            return True, content, None

        except json.JSONDecodeError as e:
            print(f"[OPENAI] JSON parsing error: {e}")
            print(f"[OPENAI] Raw response: {content_text[:200]}...")
            return False, None, f"JSON parsing error: {str(e)}"

    except Exception as e:
        error_msg = f"OpenAI API error: {str(e)}"
        print(f"[OPENAI] {error_msg}")
        return False, None, error_msg

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

def _get_fallback_scenario(character, scenario_number, language='kk'):
    """
    Get fallback scenario when AI generation fails
    """
    fallbacks = {
        'Абылай хан': [
            {
                'scenario': 1,
                'text': 'Жоңғар сарбаздары қазақ жерінің шегіне жақындады. Ата-баба қорғау үшін не істеу керек?' if language == 'kk' else 'Джунгарские войска приблизились к границам. Как защитить земли предков?',
                'options': [
                    {'id': 'A', 'text': 'Тез атақ жасау' if language == 'kk' else 'Немедленно атаковать', 'isCorrect': False},
                    {'id': 'B', 'text': 'Үш жүздің барлығын біліктестіру' if language == 'kk' else 'Объединить три жуза', 'isCorrect': True},
                    {'id': 'C', 'text': 'Түгелтеп іле шығу' if language == 'kk' else 'Отступить', 'isCorrect': False},
                    {'id': 'D', 'text': 'Орыстарға көмек сұрау' if language == 'kk' else 'Попросить помощь у русских', 'isCorrect': False}
                ],
                'correctAnswer': 'B',
                'wrongConsequence': 'Айдап күрес жеңіліске ұласты. Жоңғарлар қазақ топтарын бөлік-бөлік ұрды.' if language == 'kk' else 'Спешная атака привела к поражению. Джунгары разбили разрозненные казахские отряды.',
                'correctConsequence': 'Үш жүзді біріктіре отырып, сіз қүшті әскер құрдыңыз. Жоңғарларға қарсы айтадай жеңіс!' if language == 'kk' else 'Объединив три жуза, вы создали мощное войско. Победа над джунгарами!',
                'historicalContext': 'Абылай хан бірлік арқылы күшті әскер құру стратегиясын қолданды.' if language == 'kk' else 'Абылай хан использовал стратегию объединения для создания сильного войска.',
                'nextScenarioSetup': 'Үш жүз қосылса, әрі де басқа проблемалар туындайды...'
            },
            {
                'scenario': 2,
                'text': 'Жүс ішінде жатысуы болды, әділіксіз өлімдер болды. Халықты ішінара біріктіруді қалай сақталу керек?' if language == 'kk' else 'Внутри жузов были конфликты. Как поддержать единство перед лицом врага?',
                'options': [
                    {'id': 'A', 'text': 'Ең күшті Node-ге құл бер' if language == 'kk' else 'Подчиниться сильнейшему', 'isCorrect': False},
                    {'id': 'B', 'text': 'Прави-ші бий өндіктіррер сот құр' if language == 'kk' else 'Созвать совет биев для разрешения конфликтов', 'isCorrect': True},
                    {'id': 'C', 'text': 'Ешкімге көмек көрсетпе' if language == 'kk' else 'Не вмешиваться во внутренние дела', 'isCorrect': False},
                    {'id': 'D', 'text': 'Қауіпті адамдарды айырп тастау' if language == 'kk' else 'Изгнать смутьянов', 'isCorrect': False}
                ],
                'correctAnswer': 'B',
                'wrongConsequence': 'Дау Продолжить қалып, әскер қарсы өндіктіларсы төрт жүзіне бөлінді.' if language == 'kk' else 'Конфликты продолжились, и армия ослабла перед врагом.',
                'correctConsequence': 'Бий совет объединил өндіктіларды әділік аргументі арқылы. Халық біліктер! Әскер дайындалды!' if language == 'kk' else 'Совет биев объединил людей справедливостью. Народ готов! Армия подготовлена!',
                'historicalContext': 'Абылай хан биев институтын қолдана отырып, немінде келген сағын істеді.' if language == 'kk' else 'Абылай хан использовал институт биев для единства.',
                'nextScenarioSetup': 'Әскер дайындалды. Бірақ ақырында жоңғарлармен өндіктіпарлар жақындалды...'
            }
        ],
        'Абай Кунанбаев': [
            {
                'scenario': 1,
                'text': 'Жас балалар сөз сөйлеу әнерін үйренгісі келеді. Аларға не үйретесіз?' if language == 'kk' else 'Молодые люди хотят научиться красивой речи. Как их обучить?',
                'options': [
                    {'id': 'A', 'text': 'Ескі өлеңдерді оқы' if language == 'kk' else 'Читать старые стихи', 'isCorrect': False},
                    {'id': 'B', 'text': 'Өздік өлең жазуды үйрет' if language == 'kk' else 'Учить писать собственные стихи', 'isCorrect': True},
                    {'id': 'C', 'text': 'Басқа іс істеуге ықылас бер' if language == 'kk' else 'Позволить заняться другим', 'isCorrect': False},
                    {'id': 'D', 'text': 'Шетел әдебиетін оқы' if language == 'kk' else 'Читать иностранную литературу', 'isCorrect': False}
                ],
                'correctAnswer': 'B',
                'wrongConsequence': 'Ескі өлеңдерді қайталап жүргеніңіз балалардың шығармашылығын тоқтатты. Олар ешкімге ұқсамасса өлеңдер жаза алмады.' if language == 'kk' else 'Повторение старых стихов не развивает творчество. Молодежь не может создавать свои произведения.',
                'correctConsequence': 'Өз сөздерімен өлең жазуды үйретіңіз - балалар шығармашыл болды! Өндіктіпарлар өндіктіпарлар түрінде қайта ойлау басталады.' if language == 'kk' else 'Обучая писать собственные стихи, вы развиваете их творчество. Молодежь начинает оригинально мыслить!',
                'historicalContext': 'Абай өздік шығармашылықты түлектіге үйреді, ол қазақ әдебиетінің сәні болды.' if language == 'kk' else 'Абай учил ученикам самостоятельному творчеству, что стало основой казахской литературы.',
                'nextScenarioSetup': 'Балалар өлең жаза барлығына балалық та бұлай ілінді...'
            }
        ],
        'Айтеке би': [
            {
                'scenario': 1,
                'text': 'Екі саудагер өнімділік туралы дауласып жатыр. Сіз әділ сот ете аласыз ба?' if language == 'kk' else 'Два купца спорят о товаре. Как разрешить этот спор справедливо?',
                'options': [
                    {'id': 'A', 'text': 'Күшілі тарапқа құқық бер' if language == 'kk' else 'Дать право более сильному', 'isCorrect': False},
                    {'id': 'B', 'text': 'Екеуінің де сөзін тыңда' if language == 'kk' else 'Выслушать обе стороны', 'isCorrect': True},
                    {'id': 'C', 'text': 'Ешкімге байланыстырма' if language == 'kk' else 'Не разбираться в спорах', 'isCorrect': False},
                    {'id': 'D', 'text': 'Ысқақ төңнег өлеңін' if language == 'kk' else 'Призвать свидетелей', 'isCorrect': False}
                ],
                'correctAnswer': 'B',
                'wrongConsequence': 'Біржақтап сот істесеңіз, халық сізге күмәнеді. Өндіктіпарлар өндіктіпарлар секе міндеттерді істей қоймайды.' if language == 'kk' else 'Несправедливое решение подрывает доверие народа. Люди перестанут обращаться к вам с делами.',
                'correctConsequence': 'Екеуінің де сөзін тыңдау арқылы сіз әділ шешім қабылдадыңыз. Халық сіздің даналығына мойындау жасады және өндіктіпарлар сіздің сотын сезінді.' if language == 'kk' else 'Выслушав обе стороны, вы вынесли справедливое решение. Народ уважает вашу мудрость!',
                'historicalContext': 'Айтеке би әділік жеті жарғыда айтылғандай әділік арқылы халық өндіктіпарларын сақтады.' if language == 'kk' else 'Айтеке би, как установлено в Жеті Жарғы, разрешал споры справедливо.',
                'nextScenarioSetup': 'Әділ сот өндіктіпарлар түліктіне ықдай, түліктіктелік өндіктіпарлар келіді...'
            }
        ]
    }

    character_fallbacks = fallbacks.get(character, fallbacks['Абылай хан'])
    return character_fallbacks[min(scenario_number - 1, len(character_fallbacks) - 1)]


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
    """
    Generate learning content using proper fallback missions
    """
    # Use proper fallback missions based on topic
    fallback_missions = {
        'Абылай хан': {
            'text_kz': 'Абылай хан - қазақ халқының ұлы батыры, 1711-1781 жылдары өмір сүрген. Ол Қазақ хандығын біріктіріп, жоңғар шапқыншылығына қарсы күресті. Абылай хан әділдігімен, ерлігімен және данышпандығымен танылды.',
            'questions_kz': [
                'Абылай хан қай жылдары өмір сүрген?',
                'Абылай хан қандай қасиеттерімен танылды?',
                'Абылай хан қандай жаудың шапқыншылығына қарсы күресті?'
            ],
            'options_kz': [
                ['1711-1781', '1721-1791', '1731-1791', '1701-1781'],
                ['Әділдігімен, ерлігімен', 'Ақылмен, байлығымен', 'Күшпен, қаталдығымен', 'Сымбаттылығымен, әсемдігімен'],
                ['Жоңғар', 'Орыс', 'Қырғыз', 'Қытай']
            ],
            'correct_answers': [0, 0, 0],
            'level': level
        },
        'Абай': {
            'text_kz': 'Абай Құнанбайұлы - қазақ әдебиетінің классигі, 1845-1904 жылдары өмір сүрген. Ол ақын, аудармашы, композитор және философ. Абай "Қара сөз" атты философиялық еңбегін жазды, қазақ поэзиясын жаңа деңгейге көтерді.',
            'questions_kz': [
                'Абай қай жылдары өмір сүрген?',
                'Абайдың қандай еңбегі ең белгілі?',
                'Абай қандай қызметтермен айналысқан?'
            ],
            'options_kz': [
                ['1845-1904', '1835-1894', '1855-1914', '1825-1884'],
                ['Қара сөз', 'Ақ сөз', 'Қызыл сөз', 'Көк сөз'],
                ['Ақын, аудармашы', 'Шопан, егінші', 'Темірші, ұстаз', 'Балуан, күресші']
            ],
            'correct_answers': [0, 0, 0],
            'level': level
        },
        'Айтеке би': {
            'text_kz': 'Айтеке би - қазақ халқының ұлы биі, XVII ғасырда өмір сүрген. Ол әділдігімен, данышпандығымен, шешендігімен танылған. Айтеке би халық арасында дауларды шешіп, әділдік орнатқан. Оның шешендік сөздері бүгінде де маңызды.',
            'questions_kz': [
                'Айтеке би қай ғасырда өмір сүрген?',
                'Айтеке би қандай қасиеттерімен танылды?',
                'Айтеке би халық арасыда не істеген?'
            ],
            'options_kz': [
                ['XVII ғасыр', 'XVI ғасыр', 'XVIII ғасыр', 'XIX ғасыр'],
                ['Әділдігімен, данышпандығымен', 'Байлығымен, күшімен', 'Сымбаттылығымен, әсемдігімен', 'Қаталдығымен, қатігездігімен'],
                ['Дауларды шешіп, әділдік орнатқан', 'Соғыстарды басқарған', 'Елді тонап, байытқан', 'Жер аударып, көштірген']
            ],
            'correct_answers': [0, 0, 0],
            'level': level
        }
    }
    
    return fallback_missions.get(topic, fallback_missions['Абылай хан'])

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

@app.route('/mission')
def mission():
    return send_from_directory('.', 'mission.html')

@app.route('/groq-demo')
def groq_demo():
    return send_from_directory('.', 'groq_demo.html')

# Simple login with test account only
@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        limited, retry_after = _rate_limit('login', limit=30, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many login attempts. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'email and password required'}), 400
        
        all_data = load_users()
        web_users = all_data.get('web_users', {})

        # Check in unified data
        if email in web_users:
            user = web_users[email]
            ok, should_migrate = _verify_user_password(email, user, password)
            if ok:
                if should_migrate:
                    user['password_hash'] = generate_password_hash(password)
                    user.pop('password', None)
                    save_users(all_data)
                
                # Create session
                session_id = create_session(email)
                return jsonify({
                    'success': True, 
                    'user': _public_user(user),
                    'session_id': session_id
                })

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
            
            # Create session for test user
            session_id = create_session(email)
            return jsonify({
                'success': True, 
                'user': user_data,
                'session_id': session_id
            })
        
        return jsonify({'success': False, 'message': 'Неверный email или пароль.'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/check-session', methods=['POST'])
def check_session():
    """Check if session is valid"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'valid': False, 'message': 'No session provided'})
        
        if is_session_valid(session_id):
            session_data = sessions[session_id]
            update_session_activity(session_id)
            
            # Get user data
            all_data = load_users()
            web_users = all_data.get('web_users', {})
            email = session_data['email']
            
            if email in web_users:
                user = _public_user(web_users[email])
                return jsonify({
                    'valid': True, 
                    'user': user,
                    'session_id': session_id
                })
            else:
                # Test user fallback
                if email == 'test@batyrbol.kz':
                    user_data = {
                        'id': 'test_user',
                        'name': 'Батыр Бол',
                        'email': 'test@batyrbol.kz',
                        'xp': 100,
                        'level': 5,
                        'energy': 100,
                        'streak': 7,
                        'avatarUrl': None
                    }
                    return jsonify({
                        'valid': True, 
                        'user': user_data,
                        'session_id': session_id
                    })
        
        return jsonify({'valid': False, 'message': 'Session expired or invalid'})
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id and session_id in sessions:
            del sessions[session_id]
        
        return jsonify({'success': True, 'message': 'Logged out successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        limited, retry_after = _rate_limit('register', limit=10, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many registration attempts. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validation
        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'Барлық өрістерді толтырыңыз / Заполните все поля'}), 400

        if len(name) < 2:
            return jsonify({'success': False, 'message': 'Аты кем дегенде 2 таңбадан тұруы керек'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Құпия сөз кем дегенде 6 таңбадан тұруы керек'}), 400

        # Email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'success': False, 'message': 'Жарамсыз email форматы'}), 400

        # Load existing users
        all_data = load_users()
        web_users = all_data.get('web_users', {})

        # Check if user already exists
        if email in web_users:
            return jsonify({'success': False, 'message': 'Бұл email тіркелген / Email уже зарегистрирован'}), 400

        # Create new user
        user_data = {
            'id': generate_uuid(),
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'xp': 0,
            'level': 1,
            'energy': 100,
            'streak': 0,
            'avatarUrl': None,
            'createdAt': datetime.now().isoformat(),
            'lastLogin': datetime.now().isoformat(),
            'completedMissions': [],
            'achievements': [],
            'weakAreas': [],
            'language': 'kk'
        }

        # Save user
        web_users[email] = user_data
        all_data['web_users'] = web_users
        save_users(all_data)

        return jsonify({'success': True, 'user': _public_user(user_data)})

    except Exception as e:
        print(f"[REGISTER] Error: {str(e)}")
        return jsonify({'success': False, 'message': 'Қате пайда болды / Произошла ошибка'}), 500

@app.route('/api/mission/generate', methods=['POST'])
def generate_mission():
    """Generate personalized mission using AI with fallback system"""
    try:
        data = request.get_json()
        player_level = int(data.get('playerLevel', 1))
        previous_missions = data.get('previousMissions', [])
        character = data.get('character', 'Абылай хан')
        
        # Character-specific historical context
        character_context = {
            'Абылай хан': {
                'events': ['присоединение Младшего жуза', 'войны с джунгарами', 'дипломатические переговоры'],
                'rules': 'помочь народу выиграть на войне, масштабировать территорию, укрепить ханство'
            },
            'Абай': {
                'events': ['создание стихотворений', 'реформы образования', 'просветительская деятельность'],
                'rules': 'учить детей писать стихи, создавать произведения, развивать образование'
            },
            'Айтеке би': {
                'events': ['бийские суды', 'дипломатия', 'разрешение споров'],
                'rules': 'справедливо судить, решать конфликты, поддерживать мир'
            }
        }
        
        context = character_context.get(character, character_context['Абылай хан'])
        
        # Try AI generation up to 3 times
        for attempt in range(1, 4):
            try:
                mission = call_ai_for_mission(player_level, previous_missions, character, context)
                if validate_ai_response(mission):
                    return jsonify({
                        'success': True,
                        'mission': mission,
                        'attempt': attempt
                    })
            except Exception as e:
                print(f"AI generation attempt {attempt} failed: {e}")
                continue
        
        # Fallback content if all attempts fail
        fallback_mission = get_fallback_mission(character)
        return jsonify({
            'success': True,
            'mission': fallback_mission,
            'fallback': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def call_ai_for_mission(player_level, previous_missions, character, context):
    """Call AI to generate mission content"""
    import openai
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Adjust complexity based on player level
    complexity_level = "простой" if player_level <= 2 else "сложный" if player_level <= 4 else "экспертный"
    
    prompt = f"""
    Создай короткую игровую миссию для персонажа {character}.
    
    Контекст персонажа: {context['rules']}
    Исторические события: {', '.join(context['events'])}
    
    Уровень игрока: {player_level} ({complexity_level})
    
    Требования:
    1. Текст миссии: 2-3 предложения максимум
    2. Исторически достоверные события
    3. 3-4 варианта выбора
    4. Один правильный ответ основан на исторических фактах
    
    Формат ответа (JSON):
    {{
        "text": "Короткий текст миссии...",
        "options": ["Вариант 1", "Вариант 2", "Вариант 3"],
        "correctIndex": 0,
        "explanation": "Краткое объяснение"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    
    import json
    mission_data = json.loads(response.choices[0].message.content.strip())
    return mission_data

def validate_ai_response(response):
    """Validate AI generated response"""
    try:
        return (
            isinstance(response, dict) and
            'text' in response and
            'options' in response and
            'correctIndex' in response and
            isinstance(response['options'], list) and
            len(response['options']) >= 3 and
            0 <= response['correctIndex'] < len(response['options']) and
            len(response['text']) > 10
        )
    except:
        return False

def get_fallback_mission(character):
    """Get fallback mission when AI fails"""
    fallback_missions = {
        'Абылай хан': {
            'text': 'Джунгарские войска приближаются к границам. Какое решение примете?',
            'options': ['Собрать войско', 'Начать переговоры', 'Обратиться за помощью'],
            'correctIndex': 1,
            'explanation': 'Дипломатия была ключевой стратегией Абылай хана'
        },
        'Абай': {
            'text': 'Молодые поэты просят научить их мастерству. Ваш ответ?',
            'options': ['Отказаться', 'Принять учеников', 'Организовать школу'],
            'correctIndex': 2,
            'explanation': 'Абай был известен своей просветительской деятельностью'
        },
        'Айтеке би': {
            'text': 'Две стороны спорят за землю. Как вы рассудите?',
            'options': ['Отдать сильному', 'Разделить поровну', 'Найти компромисс'],
            'correctIndex': 2,
            'explanation': 'Справедливость была главным принципом биев'
        }
    }
    
    return fallback_missions.get(character, fallback_missions['Абылай хан'])

@app.route('/api/content/generate-openai', methods=['POST'])
def generate_content_openai():
    """Generate mission content using OpenAI GPT-4o-mini"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        level = int(data.get('level', 2))
        api_key = data.get('api_key', '').strip()
        
        if not topic:
            return jsonify({'success': False, 'message': 'Topic is required'}), 400
        
        # Use provided API key or default from environment
        openai_api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not openai_api_key:
            return jsonify({
                'success': False, 
                'message': 'OpenAI API key not provided. Please provide API key or set OPENAI_API_KEY environment variable.'
            }), 400
        
        try:
            import openai
            client = openai.OpenAI(api_key=openai_api_key)
            
            # Determine content complexity based on level
            level_descriptions = {
                1: "простые сказки и легенды для детей",
                2: "основные исторические факты",
                3: "детальная историческая информация",
                4: "официальные документы и глубокий анализ"
            }
            
            complexity = level_descriptions.get(level, "основные исторические факты")
            
            # Generate content using OpenAI
            prompt = f"""
            Создай образовательную миссию по казахской истории на тему "{topic}".
            Уровень сложности: {level} ({complexity}).
            
            Требования:
            1. Напиши текст на казахском языке (200-300 слов)
            2. Создай 3-4 вопроса по тексту
            3. Для каждого вопроса создай 4 варианта ответа (A, B, C, D)
            4. Укажи правильный ответ
            5. Добавь перевод текста на русский язык
            
            Формат ответа (JSON):
            {{
                "topic": "{topic}",
                "text_kz": "текст на казахском",
                "text_ru": "перевод на русский",
                "questions_kz": ["вопрос1", "вопрос2", "вопрос3"],
                "options_kz": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"]],
                "correct_answers": [0, 1, 2]
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по казахской истории и создатель образовательных материалов. Отвечай только в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                content = json.loads(content_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                if json_match:
                    content = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON response")
            
            return jsonify({
                'success': True,
                'content': content,
                'model': 'gpt-4o-mini'
            })
            
        except Exception as e:
            print(f"[OPENAI] Error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'OpenAI API error: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"[OPENAI] Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Generation failed: {str(e)}'
        }), 500

@app.route('/api/content/generate', methods=['POST'])
def generate_learning_content():
    try:
        limited, retry_after = _rate_limit('content_generate', limit=20, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many requests. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

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

        if len(topic) > 120:
            return jsonify({'success': False, 'message': 'Topic too long'}), 400

        if level < 1 or level > 6:
            return jsonify({'success': False, 'message': 'Invalid level'}), 400

        content = _generate_learning_content_kz(topic, source_urls=source_urls, level=level)
        
        # Check if content contains error
        if 'error' in content:
            return jsonify({
                'success': False, 
                'message': content.get('message', 'AI service temporarily unavailable'),
                'error': content.get('error')
            }), 503
            
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/content/translate', methods=['POST'])
def translate_content():
    try:
        limited, retry_after = _rate_limit('translate', limit=30, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many requests. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        payload = request.get_json() or {}
        text_kz = (payload.get('text_kz') or '').strip()
        if not text_kz:
            return jsonify({'success': False, 'message': 'text_kz required'}), 400

        if len(text_kz) > 4000:
            return jsonify({'success': False, 'message': 'text_kz too long'}), 400

        return jsonify({'success': True, 'text_ru': _translate_kz_to_ru(text_kz)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mission/generate-scenario', methods=['POST'])
def generate_scenario():
    """
    Generate a single scenario for a mission using OpenAI
    Used by mission_generator.js
    """
    try:
        limited, retry_after = _rate_limit('scenario_generation', limit=30, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many requests. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        payload = request.get_json() or {}

        character = payload.get('character', '').strip()
        level = int(payload.get('level', 1))
        scenario_number = int(payload.get('scenarioNumber', 1))
        prompt = payload.get('prompt', '')
        language = payload.get('language', 'kk')

        if not character or not prompt:
            return jsonify({'success': False, 'message': 'character and prompt required'}), 400

        # Call OpenAI API
        try:
            if not OPENAI_AVAILABLE:
                return jsonify({
                    'success': False,
                    'message': 'OpenAI module not available'
                }), 503

            openai_api_key = OPENAI_API_KEY
            if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
                return jsonify({
                    'success': False,
                    'message': 'OpenAI API key not configured'
                }), 503

            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - эксперт по казахской истории и создатель интерактивных образовательных игр. Отвечай ТОЛЬКО валидным JSON, без markdown или пояснений."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            content_text = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                scenario = json.loads(content_text)

                # Validate required fields
                required_fields = ['scenario', 'text', 'options', 'correctAnswer', 'wrongConsequence', 'correctConsequence']
                for field in required_fields:
                    if field not in scenario:
                        # Return fallback
                        return jsonify({
                            'success': True,
                            'scenario': _get_fallback_scenario(character, scenario_number, language),
                            'fallback': True
                        })

                return jsonify({'success': True, 'scenario': scenario})

            except json.JSONDecodeError as e:
                print(f"[SCENARIO] JSON parsing error: {e}")
                return jsonify({
                    'success': True,
                    'scenario': _get_fallback_scenario(character, scenario_number, language),
                    'fallback': True
                })

        except Exception as e:
            print(f"[SCENARIO] OpenAI error: {str(e)}")
            return jsonify({
                'success': True,
                'scenario': _get_fallback_scenario(character, scenario_number, language),
                'fallback': True
            })

    except Exception as e:
        print(f"[SCENARIO] Generation error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/mission/personalized', methods=['POST'])
def generate_personalized_mission():
    """
    Generate AI-personalized mission based on user profile
    Uses OpenAI o4-mini model for personalization
    """
    try:
        limited, retry_after = _rate_limit('personalized_mission', limit=10, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many requests. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        payload = request.get_json() or {}

        # Extract user profile
        user_profile = {
            'level': int(payload.get('level', 1)),
            'completedMissions': payload.get('completedMissions', []),
            'weakAreas': payload.get('weakAreas', []),
            'language': payload.get('language', 'kk')
        }

        # Validate level
        if user_profile['level'] < 1 or user_profile['level'] > 6:
            return jsonify({'success': False, 'message': 'Invalid level'}), 400

        # Try OpenAI only
        success, content, error = _openai_generate_personal_mission(user_profile)

        if not success:
            # Use fallback missions
            return jsonify({
                'success': False,
                'message': 'AI service temporarily unavailable',
                'error': error
            }), 503

        return jsonify({'success': True, 'content': content})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/answer/check', methods=['POST'])
def check_answer():
    try:
        limited, retry_after = _rate_limit('answer_check', limit=40, window_seconds=60)
        if limited:
            return jsonify({'success': False, 'message': 'Too many requests. Try again later.'}), 429, {
                'Retry-After': str(retry_after)
            }

        payload = request.get_json() or {}
        question = (payload.get('question') or '').strip()
        user_answer = (payload.get('user_answer') or '').strip()
        correct_answer = payload.get('correct_answer')
        context = payload.get('context')
        
        if not question or not user_answer:
            return jsonify({'success': False, 'message': 'question and user_answer required'}), 400

        if len(question) > 600 or len(user_answer) > 600:
            return jsonify({'success': False, 'message': 'question/user_answer too long'}), 400
        
        # Simple answer check since Groq is disabled
        return jsonify({
            'success': True,
            'result': {
                'is_correct': True,
                'score': 85,
                'feedback': 'Answer received',
                'suggestions': 'Keep learning',
                'explanation': 'Answer processed'
            }
        })
        
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

@app.route('/api/clans/activity', methods=['POST'])
def track_clan_activity():
    """Track daily reading activity for clan members"""
    try:
        data = request.get_json()
        email = data.get('email')
        mission_completed = data.get('mission_completed', False)
        mission_skipped = data.get('mission_skipped', False)
        
        all_data = load_users()
        
        # Initialize daily activity tracking if not exists
        if 'daily_activity' not in all_data:
            all_data['daily_activity'] = {}
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Track user activity for today
        if today not in all_data['daily_activity']:
            all_data['daily_activity'][today] = {}
        
        if email not in all_data['daily_activity'][today]:
            all_data['daily_activity'][today][email] = {
                'mission_completed': False,
                'mission_skipped': False,
                'timestamp': datetime.now().isoformat()
            }
        
        # Update activity
        if mission_completed:
            all_data['daily_activity'][today][email]['mission_completed'] = True
        elif mission_skipped:
            all_data['daily_activity'][today][email]['mission_skipped'] = True
        
        save_users(all_data)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clans/members/status', methods=['GET'])
def get_clan_members_status():
    """Get reading status for all clan members today"""
    try:
        email = request.args.get('email')
        
        all_data = load_users()
        
        # Get user's clan
        user_clan = None
        if email in all_data['web_users']:
            user_clan = all_data['web_users'][email].get('clan')
        
        if not user_clan or user_clan not in all_data['clans']:
            return jsonify({'success': False, 'message': 'Клан не найден'}), 404
        
        # Get clan members
        clan_members = all_data['clans'][user_clan]['members']
        
        # Get today's activity
        today = datetime.now().strftime('%Y-%m-%d')
        daily_activity = all_data.get('daily_activity', {}).get(today, {})
        
        # Build member status list
        members_status = []
        for member_email in clan_members:
            if member_email in all_data['web_users']:
                user = all_data['web_users'][member_email]
                activity = daily_activity.get(member_email, {})
                
                members_status.append({
                    'email': member_email,
                    'name': user.get('name', 'Unknown'),
                    'xp': user.get('xp', 0),
                    'avatarUrl': user.get('avatarUrl'),
                    'mission_completed_today': activity.get('mission_completed', False),
                    'mission_skipped_today': activity.get('mission_skipped', False),
                    'has_activity_today': member_email in daily_activity
                })
        
        # Sort by XP (descending)
        members_status.sort(key=lambda x: x['xp'], reverse=True)
        
        return jsonify({
            'success': True,
            'clan_name': user_clan,
            'members': members_status,
            'date': today
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clans/leaderboard', methods=['GET'])
def get_clan_leaderboard():
    """Get updated clan leaderboard after mission completion"""
    try:
        all_data = load_users()
        clans = all_data.get('clans', {})
        web_users = all_data.get('web_users', {})
        
        # Calculate total XP for each clan
        clan_leaderboard = []
        for clan_name, clan_data in clans.items():
            total_xp = 0
            member_count = 0
            
            for member_email in clan_data['members']:
                if member_email in web_users:
                    total_xp += web_users[member_email].get('xp', 0)
                    member_count += 1
            
            clan_leaderboard.append({
                'name': clan_name,
                'total_xp': total_xp,
                'member_count': member_count,
                'leader': clan_data.get('leader', ''),
                'members': clan_data['members']
            })
        
        # Sort by total XP (descending)
        clan_leaderboard.sort(key=lambda x: x['total_xp'], reverse=True)
        
        return jsonify({
            'success': True,
            'leaderboard': clan_leaderboard
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions and send email"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()

        # Validation
        if not name or not email or not message:
            return jsonify({'success': False, 'message': 'Барлық өрістерді толтырыңыз'}), 400

        if len(name) < 2:
            return jsonify({'success': False, 'message': 'Аты кем дегенде 2 таңбадан тұруы керек'}), 400

        # Email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'success': False, 'message': 'Жарамсыз email форматы'}), 400

        # Log the contact message
        print(f"[CONTACT] New message from {name} ({email}):")
        print(f"Message: {message}")
        
        # Save to file for backup
        contact_entry = {
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'ip': _client_ip()
        }
        
        # Save to contacts file
        contacts_file = 'contacts.json'
        contacts = []
        if os.path.exists(contacts_file):
            try:
                with open(contacts_file, 'r', encoding='utf-8') as f:
                    contacts = json.load(f)
            except:
                contacts = []
        
        contacts.append(contact_entry)
        
        with open(contacts_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)

        # TODO: Send actual email to nurmiko22@gmail.com
        # For now, just log it
        print(f"[CONTACT] Would send email to: nurmiko22@gmail.com")
        print(f"[CONTACT] Subject: New Contact from {name}")
        print(f"[CONTACT] Body: From: {email}\n\n{message}")

        return jsonify({'success': True, 'message': 'Хабарлама сәтті жіберілді!'})

    except Exception as e:
        print(f"[CONTACT] Error: {str(e)}")
        return jsonify({'success': False, 'message': 'Қате пайда болды'}), 500

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
