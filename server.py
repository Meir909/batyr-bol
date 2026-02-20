from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
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
import time
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Safe import for groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARNING] Groq module not found. Install with: pip install groq")

# Safe import for OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] OpenAI module not found. Install with: pip install openai")

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

def _groq_check_answer(question, user_answer, correct_answer=None, context=None):
    """
    Check user answer using Groq API with intelligent evaluation
    Returns: (success, result, error_message)
    """
    if not GROQ_AVAILABLE:
        return False, None, "Groq module not available"
        
    try:
        groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
        if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
            return False, None, "Groq API key not configured"
        
        client = Groq(api_key=groq_api_key)
        
        prompt = f"""
Проверь ответ пользователя на вопрос по истории Казахстана.

Контекст (если доступен): {context or 'Нет контекста'}

Вопрос: {question}

Ответ пользователя: {user_answer}

{f'Эталонный ответ: {correct_answer}' if correct_answer else ''}

Оцени ответ по следующим критериям:
1. Правильность фактов
2. Полнота ответа
3. Понимание темы
4. Точность формулировок

Верни JSON в следующем формате:
{{
    "is_correct": true/false,
    "score": 0-100,
    "feedback": "Подробный отзыв об ответе",
    "suggestions": "Что можно улучшить или добавить",
    "explanation": "Объяснение правильного ответа"
}}

Будь объективным, но поощряй правильные идеи даже если формулировка не идеальна.
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        
        result_text = response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                result = json.loads(json_text)
            else:
                result = json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"[GROQ] JSON parsing error in answer check: {e}")
            print(f"[GROQ] Raw response: {result_text[:200]}...")
            return False, None, f"JSON parsing error: {str(e)}"
        
        return True, result, None
        
    except Exception as e:
        error_msg = f"Groq API error: {str(e)}"
        return False, None, error_msg

def _groq_generate_mission(topic, level=1):
    """
    Generate mission content using Groq API
    Returns: (success, content, error_message)
    """
    if not GROQ_AVAILABLE:
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
    Generate personalized mission using OpenAI API (o4-mini model)
    Takes user profile with: level, completedMissions, weakAreas, language
    Returns: (success, content, error_message)
    """
    if not OPENAI_AVAILABLE:
        return False, None, "OpenAI module not available"

    try:
        openai_api_key = os.getenv('OPENAI_API_KEY', '').strip()
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
    Generate learning content using Groq API only
    """
    # Try Groq API only - no fallback
    success, groq_content, error = _groq_generate_mission(topic, level)
    if success:
        return groq_content
    
    # Log the error for debugging
    print(f"[GROQ] API failed: {error}")
    
    # Return error instead of fallback
    return {
        'error': 'Groq API temporarily unavailable',
        'message': 'Please try again later',
        'text_kz': 'Қызмет уақытша қолжетімсіз. Кейінірек қайталап көріңіз.',
        'questions_kz': [],
        'options_kz': [],
        'correct_answers': [],
        'topic': topic,
        'level': level
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
                return jsonify({'success': True, 'user': _public_user(user)})

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
            'id': str(uuid.uuid4()),
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

        # Try OpenAI first, fallback to Groq
        success, content, error = _openai_generate_personal_mission(user_profile)

        if not success:
            # Fallback to Groq with a random topic
            topics = ["Қазақ хандығы", "Абылай хан", "Томирис патша", "Әз-Тәуке хан", "Кенесары хан"]
            topic = random.choice(topics)
            success, content, error = _groq_generate_mission(topic, user_profile['level'])

            if not success:
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
        
        # Use Groq API only - no fallback
        success, result, error = _groq_check_answer(question, user_answer, correct_answer, context)
        
        if success:
            response_data = {'success': True, 'result': result}
            return jsonify(response_data)
        
        # Log the error and return error response
        print(f"[GROQ] Answer check failed: {error}")
        return jsonify({
            'success': False, 
            'message': 'AI service temporarily unavailable. Please try again later.',
            'error': error
        }), 503
        
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
