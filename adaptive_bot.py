from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from datetime import date
import random
import json

# Импортируем адаптивную модель обучения
from learning_model import AdaptiveLearningModel

TOKEN = "8337334846:AAE9AvClYqFXGAHJ6tGALk_U-pFPFsxOaqk"

# ===== DATA =====
users = {}
leaderboard = {}

# Инициализируем адаптивную модель
adaptive_model = AdaptiveLearningModel()

# ===== HELPERS =====
def get_level(xp):
    if xp >= 50: return 4
    if xp >= 25: return 3
    if xp >= 10: return 2
    return 1

def today():
    return str(date.today())

def get_user_level(user_data):
    """Определить уровень пользователя на основе XP"""
    # Преобразуем уровень XP в категориальный уровень
    xp = user_data.get("xp", 0)
    if xp >= 30:
        return "advanced"
    elif xp >= 15:
        return "intermediate"
    else:
        return "beginner"

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",
        "done": [],
        "last_day": today(),
        "streak": 1,
        "current_mission": None,
        "skill_level": "beginner",  # Начальный уровень навыков
        "history_answers": []  # История ответов для адаптации
    }
    await update.message.reply_text(
        "🇰🇿 BATYR BOL\n\n"
        "Тарих пен қазақ тілін миссия арқылы үйренеміз!\n\n"
        "Тілді таңда:\n"
        "/kz — Қазақша\n"
        "/ru — Русский"
    )

async def set_kz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id]["lang"] = "kz"
    await update.message.reply_text("✅ Қазақ тілі таңдалды\n/missions")

async def set_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id]["lang"] = "ru"
    await update.message.reply_text("✅ Русский язык выбран\n/missions")

async def missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = users[uid]
    
    # reset daily
    if u["last_day"] != today():
        u["done"].clear()
        u["last_day"] = today()
        u["streak"] += 1
    
    # Определяем уровень пользователя
    user_skill_level = get_user_level(u)
    
    # Генерируем адаптивный контент
    content_type = random.choice(["history", "language"])
    content = adaptive_model.get_adaptive_content(user_skill_level, content_type)
    
    # Сохраняем контент для пользователя
    u["current_content"] = content
    
    # Генерируем вопросы на основе контента
    questions = adaptive_model.generate_questions(content, user_skill_level, 3)
    u["current_questions"] = questions
    
    # Формируем сообщение
    text = f"📖 {content['title']}\n\n"
    text += f"{content['text']}\n\n"
    text += "❓ Сұрақтар:\n\n"
    
    for i, q in enumerate(questions, 1):
        text += f"{i}. {q['text']}\n"
        # Для тестовых вопросов показываем варианты
        if q.get('options'):
            for j, option in enumerate(q['options'], 1):
                text += f"   {j}) {option}\n"
        text += "\n"
    
    text += "✍️ Жауап беру үшін:\n/answer <нөмір> <жауап>\nнемесе жай ғана жауап жазыңыз"
    
    await update.message.reply_text(text)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = users[uid]
    
    # Проверяем наличие активного контента
    if "current_content" not in u or "current_questions" not in u:
        await update.message.reply_text("Алдымен /missions командасын жіберіңіз")
        return
    
    questions = u["current_questions"]
    content = u["current_content"]
    
    # Handle command-based answers
    if context.args:
        if len(context.args) < 2:
            await update.message.reply_text("Формат: /answer <нөмір> <жауап>")
            return

        try:
            num = int(context.args[0]) - 1
        except ValueError:
            await update.message.reply_text("❗ Сұрақ нөмірі сан болуы керек")
            return
            
        # Check if question number is valid
        if num < 0 or num >= len(questions):
            await update.message.reply_text("❗ Сұрақ нөмірі қате")
            return
        
        user_answer = " ".join(context.args[1:]).lower()
    
    # Handle direct answers (non-command)
    else:
        user_answer = update.message.text.lower()
        num = 0  # Для простоты берем первый вопрос
    
    # Проверяем существование вопроса
    if num >= len(questions):
        await update.message.reply_text("Сұрақ нөмірі қате")
        return
    
    question = questions[num]
    
    # Оцениваем ответ с помощью адаптивной модели
    is_correct, feedback, new_skill_level = adaptive_model.evaluate_answer(
        question, user_answer, u.get("history_answers", [])
    )
    
    # Обновляем историю ответов пользователя
    answer_record = {
        "question_id": question["id"],
        "user_answer": user_answer,
        "correct": is_correct,
        "level": u.get("skill_level", "beginner"),
        "timestamp": today()
    }
    u["history_answers"].append(answer_record)
    
    # Обновляем уровень пользователя
    u["skill_level"] = new_skill_level
    
    # Начисляем XP
    if is_correct:
        gain = 2 if question["difficulty"] == "advanced" else 1
        u["xp"] += gain
        u["level"] = get_level(u["xp"])
        leaderboard[uid] = u["xp"]
        await update.message.reply_text(f"✅ {feedback}\n+{gain} XP")
    else:
        await update.message.reply_text(f"❌ {feedback}")
        
        # Для неправильных ответов даем дополнительную помощь
        if question.get('correct_answer'):
            await update.message.reply_text(f"💡 Көмек: Дұрыс жауап - {question['correct_answer']}")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = users[update.effective_user.id]
    skill_level = u.get("skill_level", "beginner")
    await update.message.reply_text(
        f"👤 Профиль\n\n"
        f"⭐ XP: {u['xp']}\n"
        f"🏆 Уровень: {u['level']}\n"
        f"📚 Білім деңгейі: {skill_level}\n"
        f"🔥 Streak: {u['streak']} күн"
    )

async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🏆 Апталық лидерборд:\n\n"
    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (uid, xp) in enumerate(top, 1):
        text += f"{i}. {xp} XP\n"
    await update.message.reply_text(text)

# ===== APP =====
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("kz", set_kz))
app.add_handler(CommandHandler("ru", set_ru))
app.add_handler(CommandHandler("missions", missions))
app.add_handler(CommandHandler("answer", answer))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))  # Direct text answers

print("Адаптивті бот іске қосылды және жұмысқа дайын")
app.run_polling()