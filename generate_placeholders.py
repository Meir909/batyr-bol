#!/usr/bin/env python3
"""
Генератор плейхолдер изображений для BATYR BOL
Создает временные изображения для всех позиций в дизайне
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Цвета
COLORS = {
    'hero': '#0f172a',           # Темный синий
    'features': '#f59e0b',       # Золото
    'characters': '#10b981',     # Зеленый
    'eras': '#8b5cf6',           # Фиолетовый
    'backgrounds': '#ef4444',    # Красный
    'about': '#06b6d4',          # Голубой
    'testimonials': '#ec4899',   # Розовый
}

def hex_to_rgb(hex_color):
    """Преобразовать hex в RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_placeholder(width, height, title, filename, color_key='features'):
    """Создать плейхолдер изображение"""
    # Выбираем цвет
    color = COLORS.get(color_key, COLORS['features'])
    rgb_color = hex_to_rgb(color)

    # Создаем изображение
    img = Image.new('RGB', (width, height), rgb_color)
    draw = ImageDraw.Draw(img)

    # Пытаемся использовать встроенный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Добавляем текст
    text_color = (255, 255, 255)

    # Основной текст
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 20

    draw.text((x, y), title, fill=text_color, font=font)

    # Размер изображения
    size_text = f"{width}x{height}"
    size_bbox = draw.textbbox((0, 0), size_text, font=small_font)
    size_width = size_bbox[2] - size_bbox[0]

    x_size = (width - size_width) // 2
    y_size = (height - text_height) // 2 + 40

    draw.text((x_size, y_size), size_text, fill=text_color, font=small_font)

    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Сохраняем
    img.save(filename)
    print(f"Created: {filename}")

def main():
    base_path = "assets/images"

    # Герой изображения
    create_placeholder(1920, 1080, "Intro Hero", f"{base_path}/hero/intro-hero.jpg", 'hero')
    create_placeholder(1920, 1080, "Auth Background", f"{base_path}/backgrounds/auth-background.jpg", 'backgrounds')

    # Фотографии для секций About (400x300)
    features = [
        ("Game Learning", "game-learning.jpg", 'about'),
        ("History Heroes", "history-heroes.jpg", 'about'),
        ("Kazakh Language", "kazakh-language.jpg", 'about'),
        ("Missions Ratings", "missions-ratings.jpg", 'about'),
    ]
    for title, filename, color in features:
        create_placeholder(400, 300, title, f"{base_path}/features/{filename}", color)

    # Фотографии для секций Features (400x300)
    feature_cards = [
        ("Historical Accuracy", "historical-accuracy.jpg", 'features'),
        ("Learning Paths", "learning-paths.jpg", 'features'),
        ("Language Vocabulary", "language-vocabulary.jpg", 'features'),
        ("Cultural Context", "cultural-context.jpg", 'features'),
    ]
    for title, filename, color in feature_cards:
        create_placeholder(400, 300, title, f"{base_path}/features/{filename}", color)

    # Персонажи (большие - 800x1000)
    characters = [
        ("Abylai Khan", "abilay-khan.jpg"),
        ("Abai Kunanbayev", "abai.jpg"),
        ("Aiteke Bi", "aiteke-bi.jpg"),
    ]
    for title, filename in characters:
        create_placeholder(800, 1000, title, f"{base_path}/characters/{filename}", 'characters')

    # Персонажи мини (200x250)
    for title, filename in characters:
        mini_name = filename.replace('.jpg', '-mini.jpg')
        create_placeholder(200, 250, title[:8], f"{base_path}/characters/{mini_name}", 'characters')

    # Эпохи (400x250)
    eras = [
        ("Steppe Civilizations", "steppe-civilizations.jpg"),
        ("Turkic Khaganates", "turkic-khaganates.jpg"),
        ("Kazakh Khanate", "kazakh-khanate.jpg"),
        ("Heroes Legends", "heroes-legends.jpg"),
    ]
    for title, filename in eras:
        create_placeholder(400, 250, title, f"{base_path}/eras/{filename}", 'eras')

    # Целевая аудитория (500x400)
    audience = [
        ("Kids Teens", "kids-teens.jpg", 'characters'),
        ("Parents", "parents.jpg", 'about'),
        ("Schools Teachers", "schools-teachers.jpg", 'features'),
    ]
    for title, filename, color in audience:
        create_placeholder(500, 400, title, f"{base_path}/features/{filename}", color)

    # Как это работает (300x300)
    steps = [
        ("Choose Warrior", "choose-warrior.jpg"),
        ("Complete Missions", "complete-missions.jpg"),
        ("Study Culture", "study-culture.jpg"),
        ("Get Achievements", "get-achievements.jpg"),
    ]
    for title, filename in steps:
        create_placeholder(300, 300, title, f"{base_path}/features/{filename}", 'testimonials')

    print("\nAll placeholders created successfully!")
    print("Located in: assets/images/")
    print("\nTip: Replace these temporary images with real photos when ready!")

if __name__ == "__main__":
    main()
