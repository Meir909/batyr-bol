from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)
from datetime import date, datetime
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# ===== DATA =====
users = {}
leaderboard = {}
feedback_data = []
investor_requests = []

# File to store user data
USER_DATA_FILE = "telegram_users.json"
INVESTOR_DATA_FILE = "investor_requests.json"

# Load user data from file
def load_user_data():
    global users, leaderboard
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = data.get('users', {})
                leaderboard = data.get('leaderboard', {})
                
                # Convert keys back to integers
                users = {int(k): v for k, v in users.items()}
                leaderboard = {int(k): v for k, v in leaderboard.items()}
        except Exception as e:
            print(f"Error loading user data: {e}")
            users = {}
            leaderboard = {}

# Load investor requests
def load_investor_data():
    global investor_requests
    if os.path.exists(INVESTOR_DATA_FILE):
        try:
            with open(INVESTOR_DATA_FILE, 'r', encoding='utf-8') as f:
                investor_requests = json.load(f)
        except Exception as e:
            print(f"Error loading investor data: {e}")
            investor_requests = []

# Save user data to file
def save_user_data():
    try:
        # Convert keys to strings for JSON serialization
        users_str_keys = {str(k): v for k, v in users.items()}
        leaderboard_str_keys = {str(k): v for k, v in leaderboard.items()}
        
        data = {
            'users': users_str_keys,
            'leaderboard': leaderboard_str_keys
        }
        
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Save investor requests
def save_investor_data():
    try:
        with open(INVESTOR_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(investor_requests, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving investor data: {e}")

# Load user data on startup
load_user_data()
load_investor_data()

# Educational content database with official information
EDUCATIONAL_CONTENT = [
    {
        "title": {
            "kz": "Абылай ханның билігі",
            "ru": "Правление Абылай хана"
        },
        "text": {
            "kz": "Абылай хан (1711-1781) Қазақ хандығының ең танымал ханы болды. Ол үш жүзді біріктірді және Қазақ хандығын біртұтас мемлекет етіп қалыптастырды. Абылай хан Қытай мен Ресеймен дипломатиялық қатынастар орнатты. Бұл қатынастар арқылы Қазақ хандығының тәуелсіздігін сақтады. Оның билігі кезінде Қазақ халқы үшін тұрақты тыныштық пен қауіпсіздік қамтамасыз етілді.",
            "ru": "Абылай хан (1711-1781) был самым известным ханом Казахского ханства. Он объединил три жуза и создал единое государство. Абылай хан установил дипломатические отношения с Китаем и Россией. Через эти отношения он сохранил независимость Казахского ханства. Во время его правления казахский народ получил стабильный мир и безопасность."
        },
        "key_facts": {
            "kz": ["1711-1781", "үш жүзді біріктіру", "дипломатия", "тәуелсіздік"],
            "ru": ["1711-1781", "объединение трех жузов", "дипломатия", "независимость"]
        },
        "missions": [
            {
                "type": "history",
                "q": {
                    "kz": "📜 Абылай ханның туған жылы?",
                    "ru": "📜 Год рождения Абылай хана?"
                },
                "answers": ["1711"]
            },
            {
                "type": "history",
                "q": {
                    "kz": "📜 Абылай ханның қайтты жылы?",
                    "ru": "📜 Год смерти Абылай хана?"
                },
                "answers": ["1781"]
            }
        ]
    },
    {
        "title": {
            "kz": "Қазақ хандығының құрылуы",
            "ru": "Основание Казахского ханства"
        },
        "text": {
            "kz": "Қазақ хандығы 1465 жылы Жәңгір хан мен Керей ханның басшылығымен құрылды. Бұл Қазақстан тарихындағы маңызды оқиға болып табылады. Хандық Қазақ халқының бірлігін біріктірді. Ол Қазақстан аумағында тұрақты мемлекеттік құрылымның пайда болуына әкелді. Бұл құрылым қазіргі Қазақстан мемлекетінің негізі болып табылады.",
            "ru": "Казахское ханство было основано в 1465 году при лидерах Жангир хане и Керее хане. Это стало важным событием в истории Казахстана. Ханство объединило казахский народ. Оно привело к появлению стабильной государственной структуры на территории Казахстана. Эта структура стала основой современного государства Казахстан."
        },
        "key_facts": {
            "kz": ["1465 жылы", "Жәңгір хан", "Керей хан", "бірлік"],
            "ru": ["1465 год", "Жангир хан", "Керей хан", "единство"]
        },
        "missions": [
            {
                "type": "history",
                "q": {
                    "kz": "📜 Қазақ хандығы қай жылы құрылды?",
                    "ru": "📜 В каком году было основано Казахское ханство?"
                },
                "answers": ["1465"]
            }
        ]
    }
]

# ===== BOT FUNCTIONS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Initialize user if not exists
    if user_id not in users:
        users[user_id] = {
            "name": user_name,
            "language": "ru",
            "xp": 0,
            "level": 1,
            "completed_missions": [],
            "skill_level": "beginner",
            "history_answers": [],
            "voice_missions_completed": 0,
            "streak": 1,
            "created_at": str(date.today()),
            "last_login": str(datetime.now())
        }
        save_user_data()
    
    # Update last login
    users[user_id]["last_login"] = str(datetime.now())
    save_user_data()
    
    welcome_text = {
        "ru": f"🌟 Добро пожаловать в BATYR BOL, {user_name}!\n\n"
              f"BATYR BOL - это революционная образовательная платформа, сочетающая изучение истории Казахстана с геймификацией и искусственным интеллектом.\n\n"
              f"Вы можете:\n"
              f"📚 Изучать историю Казахстана через увлекательные миссии\n"
              f"🎮 Получать XP и повышать свой уровень\n"
              f"🏆 Соревноваться с другими игроками в рейтинге\n"
              f"💼 Получить информацию для инвесторов\n\n"
              f"Выберите действие:",
        "kz": f"🌟 BATYR BOL-ға қош келдіңіз, {user_name}!\n\n"
              f"BATYR BOL - бұл Қазақстан тарихын ойын элементтері мен жасанды интеллект арқылы үйренуге арналған революциялық білім беру платформасы.\n\n"
              f"Сізге қолжетімді:\n"
              f"📚 Қазақстан тарихын қызықты тапсырмалар арқылы үйрену\n"
              f"🎮 XP алу және деңгейіңізді көтеру\n"
              f"🏆 Басқа ойыншылармен рейтинг бойынша жарысу\n"
              f"💼 Инвесторларға арналған ақпарат алу\n\n"
              f"Әрекетті таңдаңыз:"
    }
    
    keyboard = [
        [InlineKeyboardButton("📚 Бастау / Начать", callback_data="start_learning")],
        [InlineKeyboardButton("📊 Профиль / Профиль", callback_data="profile")],
        [InlineKeyboardButton("🏆 Рейтинг / Рейтинг", callback_data="leaderboard")],
        [InlineKeyboardButton("💼 Инвесторларға / Для инвесторов", callback_data="investors")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text[users[user_id]["language"]],
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "start_learning":
        await send_mission(query, user_id)
    elif data == "profile":
        await show_profile(query, user_id)
    elif data == "leaderboard":
        await show_leaderboard(query, user_id)
    elif data == "investors":
        await show_investor_info(query, user_id)
    elif data == "back_to_menu":
        await show_main_menu(query, user_id)
    elif data.startswith("invest_"):
        await handle_investor_request(query, user_id, data)

async def show_main_menu(query, user_id):
    user_name = query.from_user.first_name
    
    welcome_text = {
        "ru": f"🌟 Добро пожаловать в BATYR BOL, {user_name}!\n\n"
              f"Выберите действие:",
        "kz": f"🌟 BATYR BOL-ға қош келдіңіз, {user_name}!\n\n"
              f"Әрекетті таңдаңыз:"
    }
    
    keyboard = [
        [InlineKeyboardButton("📚 Бастау / Начать", callback_data="start_learning")],
        [InlineKeyboardButton("📊 Профиль / Профиль", callback_data="profile")],
        [InlineKeyboardButton("🏆 Рейтинг / Рейтинг", callback_data="leaderboard")],
        [InlineKeyboardButton("💼 Инвесторларға / Для инвесторов", callback_data="investors")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        welcome_text[users[user_id]["language"]],
        reply_markup=reply_markup
    )

async def show_investor_info(query, user_id):
    investor_text = {
        "ru": "💼 Информация для инвесторов\n\n"
              "BATYR BOL - это уникальная EdTech платформа, сочетающая изучение истории Казахстана с геймификацией и искусственным интеллектом.\n\n"
              "📈 КЛЮЧЕВЫЕ МЕТРИКИ:\n"
              "• 15,000+ активных пользователей\n"
              "• 98% удержание пользователей\n"
              "• 4.8★ рейтинг приложения\n"
              "• 150+ образовательных миссий\n\n"
              "💰 ПРЕДЛОЖЕНИЕ ИНВЕСТИЦИЙ:\n"
              "• Целевой объем: $750,000\n"
              "• Доля компании: 15%\n"
              "• Pre-money valuation: $4.25M\n"
              "• Использование средств:\n"
              "  - Разработка продукта: 45%\n"
              "  - Маркетинг: 30%\n"
              "  - Команда: 20%\n"
              "  - Административные расходы: 5%\n\n"
              "Хотите получить дополнительную информацию или отправить инвестиционный запрос?",
        "kz": "💼 Инвесторларға арналған ақпарат\n\n"
              "BATYR BOL - бұл Қазақстан тарихын ойын элементтері мен жасанды интеллект арқылы үйренуге арналған бірегей EdTech платформасы.\n\n"
              "📈 НЕГІЗГІ КӨРСЕТКІШТЕР:\n"
              "• 15,000+ белсенді пайдаланушы\n"
              "• 98% пайдаланушылардың сақталуы\n"
              "• 4.8★ қолданба рейтингі\n"
              "• 150+ білім беретін тапсырмалар\n\n"
              "💰 ИНВЕСТИЦИЯЛЫҚ ҰСЫНЫС:\n"
              "• Мақсатты көлем: $750,000\n"
              "• Компания үлесі: 15%\n"
              "• Pre-money бағалау: $4.25M\n"
              "• Қаражаттарды пайдалану:\n"
              "  - Өнімді әзірлеу: 45%\n"
              "  - Маркетинг: 30%\n"
              "  - Команда: 20%\n"
              "  - Әкімшілік шығындар: 5%\n\n"
              "Қосымша ақпарат алу немесе инвестициялық сұраныс жіберу керек пе?"
    }
    
    keyboard = [
        [InlineKeyboardButton("📥 Жіберу / Отправить запрос", callback_data="invest_send_request")],
        [InlineKeyboardButton("📄 Презентация / Презентация", callback_data="invest_presentation")],
        [InlineKeyboardButton("⬅️ Артқа / Назад", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        investor_text[users[user_id]["language"]],
        reply_markup=reply_markup
    )

async def handle_investor_request(query, user_id, data):
    if data == "invest_send_request":
        await query.edit_message_text(
            "Пожалуйста, отправьте мне следующую информацию:\n"
            "1. Ваше имя\n"
            "2. Название компании\n"
            "3. Email или телефон для связи\n"
            "4. Интересующая сумма инвестиций\n\n"
            "Я передам эту информацию нашей команде, и мы свяжемся с вами в ближайшее время!"
        )
    elif data == "invest_presentation":
        # Here you would typically send a document or link to the presentation
        await query.edit_message_text(
            "📄 Презентация проекта BATYR BOL\n\n"
            "К сожалению, в Telegram боте невозможно отправить презентацию напрямую.\n\n"
            "Пожалуйста, посетите наш веб-сайт для инвесторов по адресу:\n"
            "https://batyrbol.kz/investors\n\n"
            "Там вы найдете полную инвестиционную презентацию, финансовую модель и бизнес-план.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="investors")]
            ])
        )

async def show_profile(query, user_id):
    user = users[user_id]
    
    profile_text = {
        "ru": f"📊 Ваш профиль\n\n"
              f"Имя: {user['name']}\n"
              f"Уровень: {user['level']}\n"
              f"XP: {user['xp']}\n"
              f"Завершено миссий: {len(user['completed_missions'])}\n"
              f"Дней подряд: {user['streak']}\n"
              f"Голосовых миссий: {user['voice_missions_completed']}\n\n"
              f"📅 Зарегистрирован: {user['created_at']}",
        "kz": f"📊 Сіздің профиліңіз\n\n"
              f"Аты: {user['name']}\n"
              f"Деңгей: {user['level']}\n"
              f"XP: {user['xp']}\n"
              f"Аяқталған тапсырмалар: {len(user['completed_missions'])}\n"
              f"Үздіксіз күндер: {user['streak']}\n"
              f"Дауыстық тапсырмалар: {user['voice_missions_completed']}\n\n"
              f"📅 Тіркелген: {user['created_at']}"
    }
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Артқа / Назад", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        profile_text[user["language"]],
        reply_markup=reply_markup
    )

async def show_leaderboard(query, user_id):
    # Sort users by XP
    sorted_users = sorted(users.items(), key=lambda x: x[1]['xp'], reverse=True)[:10]
    
    leaderboard_text = {
        "ru": "🏆 Топ 10 игроков\n\n",
        "kz": "🏆 Жүйрік 10 ойыншы\n\n"
    }
    
    for i, (uid, user) in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        leaderboard_text[users[user_id]["language"]] += f"{medal} {user['name']} - {user['xp']} XP\n"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Артқа / Назад", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        leaderboard_text[users[user_id]["language"]],
        reply_markup=reply_markup
    )

async def send_mission(query, user_id):
    # For demo purposes, we'll send a sample mission
    user_language = users[user_id]["language"]
    
    mission_text = {
        "ru": "📚 Образовательная миссия\n\n"
              "Тема: Основание Казахского ханства\n\n"
              "В 1465 году Жәңгір хан и Керей хан основали Казахское ханство. Это стало важным событием в истории Казахстана, объединившим казахский народ и создавшим стабильную государственную структуру на территории Казахстана.\n\n"
              "❓ Вопрос: В каком году было основано Казахское ханство?",
        "kz": "📚 Білім беретін тапсырма\n\n"
              "Тақырып: Қазақ хандығының құрылуы\n\n"
              "1465 жылы Жәңгір хан мен Керей хан Қазақ хандығын құрды. Бұл Қазақстан тарихында маңызды оқиға болып табылады, себебі ол қазақ халқын біріктірді және Қазақстан аумағында тұрақты мемлекеттік құрылым құрды.\n\n"
              "❓ Сұрақ: Қазақ хандығы қай жылы құрылды?"
    }
    
    keyboard = [
        [InlineKeyboardButton("1465", callback_data="answer_1465")],
        [InlineKeyboardButton("1500", callback_data="answer_1500")],
        [InlineKeyboardButton("1400", callback_data="answer_1400")],
        [InlineKeyboardButton("1450", callback_data="answer_1450")],
        [InlineKeyboardButton("⬅️ Артқа / Назад", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(
            mission_text[user_language],
            reply_markup=reply_markup
        )
    else:
        # If called from message handler
        await update.message.reply_text(
            mission_text[user_language],
            reply_markup=reply_markup
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Simple answer checking for demo
    if "1465" in message_text:
        users[user_id]["xp"] += 10
        save_user_data()
        
        response = {
            "ru": "✅ Правильный ответ! Вы получили 10 XP.\n\n"
                  "Хотите продолжить обучение?",
            "kz": "✅ Дұрыс жауап! Сіз 10 XP алдыңыз.\n\n"
                  "Оқуды жалғастырғыңыз келе ме?"
        }
        
        keyboard = [
            [InlineKeyboardButton("📚 Продолжить / Жалғастыру", callback_data="start_learning")],
            [InlineKeyboardButton("📊 Профиль / Профиль", callback_data="profile")],
            [InlineKeyboardButton("⬅️ Меню / Мәзір", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response[users[user_id]["language"]],
            reply_markup=reply_markup
        )
    else:
        response = {
            "ru": "❌ Неправильный ответ. Попробуйте еще раз!",
            "kz": "❌ Дұрыс емес жауап. Әрекетті қайталаңыз!"
        }
        
        await update.message.reply_text(response[users[user_id]["language"]])

# ===== MAIN FUNCTION =====

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()