#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный Telegram-бот BATYR BOL с адаптивной моделью обучения
"""

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from datetime import date
import random
import json

# Импортируем адаптивную модель обучения
from learning_model import adaptive_model

# ===== TOKEN =====
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на ваш токен

# ===== DATA =====
users = {}
leaderboard = {}

# ===== HELPERS =====
def get_level(xp):
    if xp >= 50: return 4
    if xp >= 25: return 3
    if xp >= 10: return 2
    return 1

def today():
    return str(date.today())

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",
        "done": set(),
        "last_day": today(),
        "streak": 1,
        "current_mission": None,
        "difficulty_level": "beginner",  # Начальный уровень сложности
        "learning_history": []  # История обучения
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
    
    # Сброс ежедневных данных
    if u["last_day"] != today():
        u["done"].clear()
        u["last_day"] = today()
        u["streak"] += 1
    
    # Получаем адаптивный контент на основе уровня пользователя
    content_type = random.choice(["history", "language"])
    content = adaptive_model.get_adaptive_content(u["difficulty_level"], content_type)
    
    # Сохраняем контент для пользователя
    u["current_content"] = content
    
    # Генерируем вопросы на основе контента
    questions = adaptive_model.generate_questions(content, u["difficulty_level"], 3)
    u["current_questions"] = questions
    
    # Отправляем контент пользователю
    text = f"📚 {content['title']}\n\n"
    text += f"{content['text']}\n\n"
    text += "❓ Сұрақтар:\n\n"
    
    for i, q in enumerate(questions, 1):
        text += f"{i}. {q['text']}\n"
        if q['type'] == 'choice' and q['options']:
            for j, option in enumerate(q['options'], 1):
                text += f"   {j}) {option}\n"
        text += "\n"
    
    text += "✍️ Жауап беру үшін:\n/answer <сұрақ нөмірі> <жауап>\nнемесе жай ғана жауап жазыңыз"
    
    await update.message.reply_text(text)

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    u = users[uid]
    
    # Обработка ответов через команду
    if context.args:
        if len(context.args) < 2:
            await update.message.reply_text("Формат: /answer <сұрақ нөмірі> <жауап>")
            return
        
        try:
            q_num = int(context.args[0]) - 1
        except ValueError:
            await update.message.reply_text("❗ Сұрақ нөмірі сан болуы керек")
            return
            
        # Проверяем наличие вопросов
        if "current_questions" not in u or q_num < 0 or q_num >= len(u["current_questions"]):
            await update.message.reply_text("❗ Сұрақ нөмірі қате")
            return
        
        user_answer = " ".join(context.args[1:]).lower()
    
    # Обработка прямых ответов
    else:
        # Для прямых ответов используем первый вопрос
        if "current_questions" not in u or not u["current_questions"]:
            await update.message.reply_text("Алдымен /missions командасын жіберіңіз")
            return
            
        user_answer = update.message.text.lower()
        q_num = 0  # Отвечаем на первый вопрос
    
    # Получаем вопрос
    question = u["current_questions"][q_num]
    
    # Оцениваем ответ с помощью адаптивной модели
    is_correct, feedback, new_difficulty = adaptive_model.evaluate_answer(
        question, user_answer, u.get("learning_history", [])
    )
    
    # Обновляем историю обучения
    learning_record = {
        "question": question["text"],
        "user_answer": user_answer,
        "correct": is_correct,
        "difficulty": u["difficulty_level"],
        "timestamp": str(date.today())
    }
    
    if "learning_history" not in u:
        u["learning_history"] = []
    u["learning_history"].append(learning_record)
    
    # Обновляем уровень сложности
    u["difficulty_level"] = new_difficulty
    
    # Начисляем XP
    if is_correct:
        gain = 2 if question["difficulty"] == "advanced" else 1
        u["xp"] += gain
        u["done"].add(q_num)
        u["level"] = get_level(u["xp"])
        leaderboard[uid] = u["xp"]
        await update.message.reply_text(f"✅ Дұрыс! +{gain} XP\n{feedback}")
    else:
        await update.message.reply_text(f"❌ Қате. {feedback}")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = users[update.effective_user.id]
    await update.message.reply_text(
        f"👤 Профиль\n\n"
        f"⭐ XP: {u['xp']}\n"
        f"🏆 Уровень: {u['level']}\n"
        f"📈 Сложность: {u['difficulty_level']}\n"
        f"🔥 Streak: {u['streak']} күн\n"
        f"📌 Бүгін: {len(u['done'])}/5"
    )

async def leaderboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🏆 Апталық лидерборд:\n\n"
    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (uid, xp) in enumerate(top, 1):
        text += f"{i}. {xp} XP\n"
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 BATYR BOL Ботының командалары:\n\n"
        "/start - Ботты бастау\n"
        "/missions - Жаңа миссиялар алу\n"
        "/profile - Профиліңізді көру\n"
        "/leaderboard - Лидерлер кестесі\n"
        "/help - Көмек\n"
        "/kz - Қазақ тіліне ауысу\n"
        "/ru - Орыс тіліне ауысу"
    )

# ===== APP =====
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("kz", set_kz))
app.add_handler(CommandHandler("ru", set_ru))
app.add_handler(CommandHandler("missions", missions))
app.add_handler(CommandHandler("answer", answer))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("leaderboard", leaderboard_cmd))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))  # Прямые ответы

print("Бот запущен и готов к работе")
# app.run_polling()  # Раскомментируйте для запуска бота

if __name__ == "__main__":
    # Для тестирования модели
    print("Адаптивная модель обучения готова к использованию!")
    print("Для запуска бота раскомментируйте app.run_polling()")