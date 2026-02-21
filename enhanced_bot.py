from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from datetime import date
import random
import json
import os
from dotenv import load_dotenv

# Импортируем адаптивную модель обучения
from learning_model import AdaptiveLearningModel

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

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
    uid = str(update.effective_user.id)  # Преобразуем в строку для использования в качестве ключа
    users[uid] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",  # По умолчанию казахский язык
        "done": set(),
        "last_day": today(),
        "streak": 1,
        "current_mission": None,
        "skill_level": "beginner",  # Начальный уровень навыков
        "history_answers": [],  # История ответов для адаптации
        "voice_missions_completed": 0  # Счетчик выполненных голосовых миссий
    }
    await update.message.reply_text(
        "🇰🇿 BATYR BOL\n\n"
        "Тарих пен қазақ тілін миссия арқылы үйренеміз!\n\n"
        "Тілді таңда:\n"
        "/kz — Қазақша\n"
        "/ru — Русский"
    )

async def set_kz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in users:
        users[uid]["lang"] = "kz"
    await update.message.reply_text("✅ Қазақ тілі таңдалды\n/missions")

async def set_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in users:
        users[uid]["lang"] = "ru"
    await update.message.reply_text("✅ Русский язык выбран\n/missions")

async def missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Алдымен /start командасын жіберіңіз")
        return
        
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
    
    # Определяем язык для вопросов (на основе языка интерфейса пользователя)
    question_language = "kk" if u["lang"] == "kz" else "ru"
    
    # Генерируем вопросы на основе контента
    questions = adaptive_model.generate_questions(content, user_skill_level, 5, question_language)
    u["current_questions"] = questions
    
    # Формируем сообщение
    title_text = content['title']
    if u["lang"] == "kz":
        title_text = f"📖 {content['title']}"
        content_text = content['text']
        questions_header = "❓ Сұрақтар:"
    else:
        title_text = f"📖 {content['title']}"
        content_text = content['text']
        questions_header = "❓ Вопросы:"
    
    text = f"{title_text}\n\n"
    text += f"{content_text}\n\n"
    text += f"{questions_header}\n\n"
    
    for i, q in enumerate(questions, 1):
        text += f"{i}. {q['text']}\n"
        # Для тестовых вопросов показываем варианты
        if q.get('options'):
            for j, option in enumerate(q['options'], 1):
                text += f"   {j}) {option}\n"
        text += "\n"
    
    if u["lang"] == "kz":
        text += "✍️ Жауап беру үшін:\n/answer <нөмір> <жауап>\nнемесе жай ғана жауап жазыңыз"
    else:
        text += "✍️ Чтобы ответить:\n/answer <номер> <ответ>\nили просто напишите ответ"
    
    await update.message.reply_text(text)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Алдымен /start командасын жіберіңіз")
        return
        
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
            if u["lang"] == "kz":
                await update.message.reply_text("Формат: /answer <нөмір> <жауап>")
            else:
                await update.message.reply_text("Формат: /answer <номер> <ответ>")
            return

        try:
            num = int(context.args[0]) - 1
        except ValueError:
            if u["lang"] == "kz":
                await update.message.reply_text("❗ Сұрақ нөмірі сан болуы керек")
            else:
                await update.message.reply_text("❗ Номер вопроса должен быть числом")
            return
            
        # Check if question number is valid
        if num < 0 or num >= len(questions):
            if u["lang"] == "kz":
                await update.message.reply_text("❗ Сұрақ нөмірі қате")
            else:
                await update.message.reply_text("❗ Неверный номер вопроса")
            return
        
        user_answer = " ".join(context.args[1:]).lower()
    
    # Handle direct answers (non-command)
    else:
        user_answer = update.message.text.lower()
        num = 0  # Для простоты берем первый вопрос
    
    # Проверяем существование вопроса
    if num >= len(questions):
        if u["lang"] == "kz":
            await update.message.reply_text("Сұрақ нөмірі қате")
        else:
            await update.message.reply_text("Неверный номер вопроса")
        return
    
    question = questions[num]
    
    # Оцениваем ответ с помощью адаптивной модели
    is_correct, feedback, new_skill_level, new_achievements = adaptive_model.evaluate_answer(
        question, user_answer, u.get("history_answers", []), uid, u
    )
    
    # Обновляем историю ответов пользователя
    answer_record = {
        "question_id": question["id"],
        "user_answer": user_answer,
        "correct": is_correct,
        "level": u.get("skill_level", "beginner"),
        "topic": "voice" if question.get("type") == "voice" else "general",
        "difficulty": question.get("difficulty", "beginner"),
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
        
        # Если это голосовая миссия, увеличиваем счетчик
        if question.get("type") == "voice":
            u["voice_missions_completed"] += 1
        
        # Формируем сообщение о правильном ответе
        if u["lang"] == "kz":
            response_text = f"✅ {feedback}\n+{gain} XP"
        else:
            response_text = f"✅ {feedback}\n+{gain} XP"
            
        # Добавляем информацию о достижениях, если есть
        if new_achievements:
            achievements_text = ""
            total_xp_bonus = 0
            for achievement in new_achievements:
                achievements_text += f"\n🏆 Жаңа жетістік: {achievement['name']} (+{achievement['xp_reward']} XP)"
                total_xp_bonus += achievement['xp_reward']
            
            if total_xp_bonus > 0:
                u["xp"] += total_xp_bonus
                achievements_text += f"\n🎁 Бонус: +{total_xp_bonus} XP"
            
            response_text += achievements_text
            
        await update.message.reply_text(response_text)
    else:
        if u["lang"] == "kz":
            response_text = f"❌ {feedback}"
        else:
            response_text = f"❌ {feedback}"
            
        # Для неправильных ответов даем дополнительную помощь
        if question.get('correct_answer'):
            if u["lang"] == "kz":
                response_text += f"\n💡 Көмек: Дұрыс жауап - {question['correct_answer']}"
            else:
                response_text += f"\n💡 Подсказка: Правильный ответ - {question['correct_answer']}"
                
        await update.message.reply_text(response_text)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Алдымен /start командасын жіберіңіз")
        return
        
    u = users[uid]
    skill_level = u.get("skill_level", "beginner")
    
    if u["lang"] == "kz":
        text = f"👤 Профиль\n\n"
        text += f"⭐ XP: {u['xp']}\n"
        text += f"🏆 Деңгей: {u['level']}\n"
        text += f"📚 Білім деңгейі: {skill_level}\n"
        text += f"🔥 Streak: {u['streak']} күн\n"
        text += f"🎤 Дауыс міндеттері: {u.get('voice_missions_completed', 0)}"
    else:
        text = f"👤 Профиль\n\n"
        text += f"⭐ XP: {u['xp']}\n"
        text += f"🏆 Уровень: {u['level']}\n"
        text += f"📚 Уровень знаний: {skill_level}\n"
        text += f"🔥 Streak: {u['streak']} дней\n"
        text += f"🎤 Голосовые миссии: {u.get('voice_missions_completed', 0)}"
        
    await update.message.reply_text(text)

async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(leaderboard) == 0:
        await update.message.reply_text("Әзірге рейтинг бос")
        return
        
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    text = "🏆 Апталық лидерборд:\n\n"
    for i, (uid, xp) in enumerate(sorted_leaderboard[:10], 1):  # Показываем топ-10
        # Пытаемся получить имя пользователя
        try:
            user = await context.bot.get_chat(uid)
            username = user.first_name if user.first_name else f"Пользователь {i}"
        except:
            username = f"Пользователь {i}"
            
        text += f"{i}. {username}: {xp} XP\n"
        
    await update.message.reply_text(text)

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Алдымен /start командасын жіберіңіз")
        return
        
    u = users[uid]
    
    # Получаем персонализированные рекомендации
    recommendations = adaptive_model.get_personalized_recommendations(uid, u.get("history_answers", []))
    
    if not recommendations:
        if u["lang"] == "kz":
            await update.message.reply_text("Әзірге сіз үшін ұсыныстар жоқ. Көбірек миссиялар орындаңыз!")
        else:
            await update.message.reply_text("Пока нет рекомендаций для вас. Выполните больше миссий!")
        return
    
    if u["lang"] == "kz":
        text = "🤖 Сіз үшін ұсыныстар:\n\n"
    else:
        text = "🤖 Рекомендации для вас:\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        if u["lang"] == "kz":
            text += f"{i}. {rec['reason']}\n"
            text += f"   📖 {rec['content']['title']}\n\n"
        else:
            text += f"{i}. {rec['reason']}\n"
            text += f"   📖 {rec['content']['title']}\n\n"
            
    await update.message.reply_text(text)

# ===== VOICE HANDLING =====
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in users:
        await update.message.reply_text("Алдымен /start командасын жіберіңіз")
        return
        
    u = users[uid]
    
    # Проверяем, есть ли активные миссии
    if "current_questions" not in u or not u["current_questions"]:
        if u["lang"] == "kz":
            await update.message.reply_text("Алдымен /missions командасын жіберіңіз")
        else:
            await update.message.reply_text("Сначала отправьте команду /missions")
        return
    
    # Ищем голосовую миссию среди активных вопросов
    voice_question = None
    voice_question_index = None
    
    for i, question in enumerate(u["current_questions"]):
        if question.get("type") == "voice" and i not in u["done"]:
            voice_question = question
            voice_question_index = i
            break
    
    # Если голосовая миссия найдена
    if voice_question:
        # Помечаем миссию как выполненную
        u["done"].add(voice_question_index)
        u["voice_missions_completed"] += 1
        
        # Начисляем XP
        gain = 2  # Голосовые миссии дают 2 XP
        u["xp"] += gain
        u["level"] = get_level(u["xp"])
        leaderboard[uid] = u["xp"]
        
        # Проверяем достижения
        new_achievements = adaptive_model.check_achievements(uid, u)
        
        # Формируем ответ
        if u["lang"] == "kz":
            response_text = f"🎉 Керемет! +{gain} XP"
        else:
            response_text = f"🎉 Отлично! +{gain} XP"
            
        # Добавляем информацию о достижениях
        if new_achievements:
            achievements_text = ""
            total_xp_bonus = 0
            for achievement in new_achievements:
                if u["lang"] == "kz":
                    achievements_text += f"\n🏆 Жаңа жетістік: {achievement['name']} (+{achievement['xp_reward']} XP)"
                else:
                    achievements_text += f"\n🏆 Новое достижение: {achievement['name']} (+{achievement['xp_reward']} XP)"
                total_xp_bonus += achievement['xp_reward']
            
            if total_xp_bonus > 0:
                u["xp"] += total_xp_bonus
                if u["lang"] == "kz":
                    achievements_text += f"\n🎁 Бонус: +{total_xp_bonus} XP"
                else:
                    achievements_text += f"\n🎁 Бонус: +{total_xp_bonus} XP"
            
            response_text += achievements_text
            
        await update.message.reply_text(response_text)
        
        # Проверяем, остались ли еще голосовые миссии
        remaining_voice = sum(1 for i, q in enumerate(u["current_questions"]) 
                             if q.get("type") == "voice" and i not in u["done"])
        
        if remaining_voice > 0:
            if u["lang"] == "kz":
                await update.message.reply_text(f"Қалған дауыстық міндеттер: {remaining_voice}")
            else:
                await update.message.reply_text(f"Осталось голосовых миссий: {remaining_voice}")
        else:
            if u["lang"] == "kz":
                await update.message.reply_text("✅ Барлық дауыстық міндеттер орындалды!")
            else:
                await update.message.reply_text("✅ Все голосовые миссии выполнены!")
    else:
        # Если голосовых миссий нет
        if u["lang"] == "kz":
            await update.message.reply_text("🎙️ Дауыс хабарламаңыз қабылданды. Қазіргі уақытта дауыстық міндеттер жоқ, бірақ сіз жақсы жасадыңыз!")
        else:
            await update.message.reply_text("🎙️ Ваше голосовое сообщение принято. Сейчас нет голосовых миссий, но вы отлично справились!")

# ===== APP =====
def create_app(token: str) -> Application:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kz", set_kz))
    application.add_handler(CommandHandler("ru", set_ru))
    application.add_handler(CommandHandler("missions", missions))
    application.add_handler(CommandHandler("answer", answer))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
    application.add_handler(CommandHandler("recommendations", recommendations))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))  # Direct text answers
    return application


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Put it into .env or environment variables.")
    print("Кеңейтілген бот іске қосылды және жұмысқа дайын")
    app = create_app(TOKEN)
    app.run_polling()