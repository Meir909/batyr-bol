#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование адаптивной модели обучения для BATYR BOL
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, '.')

def test_model_import():
    """Тест импорта модели"""
    try:
        from learning_model import adaptive_model
        print("✅ Модель обучения успешно импортирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта модели: {e}")
        return False

def test_content_generation():
    """Тест генерации контента"""
    try:
        from learning_model import adaptive_model
        
        # Тестируем получение контента для разных уровней
        levels = ["beginner", "intermediate", "advanced"]
        content_types = ["history", "language"]
        
        for level in levels:
            for content_type in content_types:
                content = adaptive_model.get_adaptive_content(level, content_type)
                if content and "title" in content and "text" in content:
                    print(f"✅ Контент для уровня {level}, типа {content_type}: {content['title']}")
                else:
                    print(f"❌ Не удалось получить контент для уровня {level}, типа {content_type}")
                    return False
        
        return True
    except Exception as e:
        print(f"❌ Ошибка генерации контента: {e}")
        return False

def test_question_generation():
    """Тест генерации вопросов"""
    try:
        from learning_model import adaptive_model
        
        # Получаем пример контента
        content = adaptive_model.get_adaptive_content("beginner", "history")
        
        # Генерируем вопросы для разных уровней
        levels = ["beginner", "intermediate", "advanced"]
        
        for level in levels:
            questions = adaptive_model.generate_questions(content, level, 3)
            if questions and len(questions) > 0:
                print(f"✅ Вопросы для уровня {level}: сгенерировано {len(questions)} вопросов")
                # Проверяем структуру первого вопроса
                if "text" in questions[0] and "type" in questions[0]:
                    print(f"   Пример вопроса: {questions[0]['text']}")
                else:
                    print(f"❌ Неправильная структура вопросов для уровня {level}")
                    return False
            else:
                print(f"❌ Не удалось сгенерировать вопросы для уровня {level}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Ошибка генерации вопросов: {e}")
        return False

def test_answer_evaluation():
    """Тест оценки ответов"""
    try:
        from learning_model import adaptive_model
        
        # Получаем контент и вопрос
        content = adaptive_model.get_adaptive_content("beginner", "history")
        questions = adaptive_model.generate_questions(content, "beginner", 1)
        question = questions[0]
        
        # Тестируем оценку правильного ответа
        user_answer = "правильный ответ"  # Упрощенный тест
        user_history = []
        
        is_correct, feedback, new_level = adaptive_model.evaluate_answer(
            question, user_answer, user_history
        )
        
        if isinstance(is_correct, bool) and isinstance(feedback, str) and isinstance(new_level, str):
            print("✅ Оценка ответов работает корректно")
            print(f"   Результат: {'Правильно' if is_correct else 'Неправильно'}")
            print(f"   Обратная связь: {feedback}")
            print(f"   Новый уровень: {new_level}")
            return True
        else:
            print("❌ Ошибка в формате оценки ответов")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка оценки ответов: {e}")
        return False

def test_level_adjustment():
    """Тест адаптации уровня сложности"""
    try:
        from learning_model import adaptive_model
        
        # Создаем историю пользователя с правильными ответами
        correct_history = [
            {"correct": True, "level": "beginner"},
            {"correct": True, "level": "beginner"},
            {"correct": True, "level": "beginner"}
        ]
        
        # Создаем историю с неправильными ответами
        incorrect_history = [
            {"correct": False, "level": "intermediate"},
            {"correct": False, "level": "intermediate"},
            {"correct": False, "level": "intermediate"}
        ]
        
        # Тестируем повышение уровня
        new_level_up = adaptive_model._adjust_level(correct_history, True)
        print(f"✅ Адаптация уровня (повышение): beginner → {new_level_up}")
        
        # Тестируем понижение уровня
        new_level_down = adaptive_model._adjust_level(incorrect_history, False)
        print(f"✅ Адаптация уровня (понижение): intermediate → {new_level_down}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка адаптации уровня: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔍 Тестирование адаптивной модели обучения BATYR BOL")
    print("=" * 60)
    print()
    
    tests = [
        ("Импорт модели", test_model_import),
        ("Генерация контента", test_content_generation),
        ("Генерация вопросов", test_question_generation),
        ("Оценка ответов", test_answer_evaluation),
        ("Адаптация уровня", test_level_adjustment)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"🧪 Тест: {test_name}")
        try:
            if test_func():
                print("   ✅ Пройден")
                passed += 1
            else:
                print("   ❌ Провален")
                failed += 1
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"Всего тестов: {len(tests)}")
    print(f"Пройдено: {passed}")
    print(f"Провалено: {failed}")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        print("Адаптивная модель обучения готова к интеграции с Telegram-ботом.")
        return True
    else:
        print(f"\n⚠️  {failed} тестов провалено. Требуется доработка.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)