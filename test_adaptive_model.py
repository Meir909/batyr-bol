#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование адаптивной модели обучения для BATYR BOL
"""

import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, '.')

def test_model_import():
    """Тест импорта модели"""
    try:
        from learning_model import AdaptiveLearningModel
        print("✓ Модель обучения успешно импортирована")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта модели: {e}")
        return False

def test_model_initialization():
    """Тест инициализации модели"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        print("✓ Модель успешно инициализирована")
        
        # Проверяем наличие контента
        if hasattr(model, 'content_database') and model.content_database:
            print(f"✓ База контента загружена ({len(model.content_database)} категорий)")
        else:
            print("❌ База контента не загружена")
            return False
            
        # Проверяем шаблоны вопросов
        if hasattr(model, 'question_templates') and model.question_templates:
            levels = list(model.question_templates.keys())
            print(f"✓ Шаблоны вопросов загружены (уровни: {', '.join(levels)})")
        else:
            print("❌ Шаблоны вопросов не загружены")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации модели: {e}")
        return False

def test_content_generation():
    """Тест генерации контента"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Тестируем получение контента для разных уровней
        for level in ["beginner", "intermediate", "advanced"]:
            content = model.get_adaptive_content(level, "history")
            if content:
                print(f"✓ Контент для уровня {level}: {content['title']}")
            else:
                print(f"❌ Не удалось получить контент для уровня {level}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Ошибка генерации контента: {e}")
        return False

def test_question_generation():
    """Тест генерации вопросов"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Получаем контент
        content = model.get_adaptive_content("beginner", "history")
        
        # Генерируем вопросы для разных уровней
        for level in ["beginner", "intermediate", "advanced"]:
            questions = model.generate_questions(content, level, 3)
            if questions:
                print(f"✓ Вопросы для уровня {level}: {len(questions)} шт.")
                
                # Проверяем структуру вопросов
                for i, q in enumerate(questions):
                    required_fields = ['id', 'text', 'type', 'difficulty']
                    missing_fields = [field for field in required_fields if field not in q]
                    if missing_fields:
                        print(f"❌ Вопрос {i+1} не содержит обязательных полей: {missing_fields}")
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
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Получаем контент и генерируем вопрос
        content = model.get_adaptive_content("beginner", "history")
        questions = model.generate_questions(content, "beginner", 1)
        
        if not questions:
            print("❌ Не удалось сгенерировать вопросы для тестирования")
            return False
            
        question = questions[0]
        
        # Тестируем оценку правильного ответа
        correct_answer = question.get('correct_answer', '1465')
        is_correct, feedback, new_level = model.evaluate_answer(
            question, correct_answer, []
        )
        
        if is_correct:
            print("✓ Оценка правильного ответа работает корректно")
        else:
            print("❌ Оценка правильного ответа работает некорректно")
            return False
            
        # Тестируем оценку неправильного ответа
        is_correct, feedback, new_level = model.evaluate_answer(
            question, "неправильный ответ", []
        )
        
        if not is_correct:
            print("✓ Оценка неправильного ответа работает корректно")
        else:
            print("❌ Оценка неправильного ответа работает некорректно")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка оценки ответов: {e}")
        return False

def test_level_adjustment():
    """Тест адаптации уровня"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Создаем историю ответов пользователя
        user_history = [
            {"correct": True, "level": "beginner"},
            {"correct": True, "level": "beginner"},
            {"correct": True, "level": "beginner"},
        ]
        
        # Проверяем повышение уровня
        new_level = model._adjust_level(user_history, True)
        if new_level in ["beginner", "intermediate", "advanced"]:
            print(f"✓ Адаптация уровня работает корректно: {new_level}")
        else:
            print("❌ Адаптация уровня работает некорректно")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка адаптации уровня: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Тестирование адаптивной модели обучения BATYR BOL")
    print("=" * 50)
    
    tests = [
        test_model_import,
        test_model_initialization,
        test_content_generation,
        test_question_generation,
        test_answer_evaluation,
        test_level_adjustment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        print("\nТеперь вы можете запустить адаптивного бота командой:")
        print("python adaptive_bot.py")
        return True
    else:
        print("❌ Некоторые тесты не пройдены. Проверьте код.")
        return False

if __name__ == "__main__":
    main()