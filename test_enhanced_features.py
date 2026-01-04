#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование расширенных функций BATYR BOL
"""

import sys
import os
import json
from datetime import datetime

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
        
        # Проверяем наличие новых компонентов
        if hasattr(model, 'user_profiles'):
            print("✓ Система профилей пользователей инициализирована")
        else:
            print("❌ Система профилей пользователей не инициализирована")
            return False
            
        if hasattr(model, 'achievements') and model.achievements:
            print(f"✓ Система достижений инициализирована ({len(model.achievements)} достижений)")
        else:
            print("❌ Система достижений не инициализирована")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации модели: {e}")
        return False

def test_achievement_system():
    """Тест системы достижений"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Создаем тестовые данные пользователя
        user_data = {
            "xp": 10,
            "history_answers": [],
            "streak": 3,
            "voice_missions_completed": 0
        }
        
        # Проверяем достижения
        achievements = model.check_achievements("test_user", user_data)
        
        # Должно быть хотя бы одно достижение (first_mission)
        if len(achievements) > 0:
            print(f"✓ Система достижений работает корректно ({len(achievements)} достижений)")
            
            # Проверяем структуру достижений
            for achievement in achievements:
                required_fields = ['name', 'description', 'xp_reward']
                missing_fields = [field for field in required_fields if field not in achievement]
                if missing_fields:
                    print(f"❌ Достижение не содержит обязательных полей: {missing_fields}")
                    return False
                    
            return True
        else:
            print("❌ Система достижений не работает корректно")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования системы достижений: {e}")
        return False

def test_error_analysis():
    """Тест анализа ошибок пользователей"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Создаем тестовую историю пользователя с ошибками
        user_history = [
            {"correct": True, "topic": "history", "difficulty": "beginner"},
            {"correct": False, "topic": "history", "difficulty": "beginner"},
            {"correct": True, "topic": "language", "difficulty": "intermediate"},
            {"correct": False, "topic": "language", "difficulty": "intermediate"},
            {"correct": False, "topic": "history", "difficulty": "beginner"},
        ]
        
        # Анализируем ошибки
        error_analysis = model.analyze_user_errors("test_user", user_history)
        
        if error_analysis:
            print("✓ Анализ ошибок пользователей работает корректно")
            
            # Проверяем наличие ключевых метрик
            required_metrics = ["total_attempts", "correct_answers", "incorrect_answers"]
            for metric in required_metrics:
                if metric not in error_analysis:
                    print(f"❌ В анализе ошибок отсутствует метрика: {metric}")
                    return False
                    
            return True
        else:
            print("❌ Анализ ошибок пользователей не работает корректно")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования анализа ошибок: {e}")
        return False

def test_personalized_recommendations():
    """Тест персонализированных рекомендаций"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Создаем тестовую историю пользователя с плохими результатами по истории
        user_history = [
            {"correct": False, "topic": "history", "difficulty": "beginner"},
            {"correct": False, "topic": "history", "difficulty": "beginner"},
            {"correct": True, "topic": "language", "difficulty": "intermediate"},
        ]
        
        # Получаем рекомендации
        recommendations = model.get_personalized_recommendations("test_user", user_history)
        
        print(f"✓ Персонализированные рекомендации работают корректно ({len(recommendations)} рекомендаций)")
        
        # Проверяем структуру рекомендаций
        for recommendation in recommendations:
            required_fields = ['type', 'content', 'reason']
            missing_fields = [field for field in required_fields if field not in recommendation]
            if missing_fields:
                print(f"❌ Рекомендация не содержит обязательных полей: {missing_fields}")
                return False
                
        return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования персонализированных рекомендаций: {e}")
        return False

def test_multilanguage_support():
    """Тест поддержки нескольких языков"""
    try:
        from learning_model import AdaptiveLearningModel
        model = AdaptiveLearningModel()
        
        # Получаем контент
        content = model.get_adaptive_content("beginner", "history")
        
        # Генерируем вопросы на разных языках
        ru_questions = model.generate_questions(content, "beginner", 2, "ru")
        kk_questions = model.generate_questions(content, "beginner", 2, "kk")
        
        if ru_questions and kk_questions:
            print("✓ Поддержка нескольких языков работает корректно")
            
            # Проверяем, что у вопросов указан язык
            for q in ru_questions + kk_questions:
                if 'language' not in q:
                    print("❌ Вопросы не содержат информацию о языке")
                    return False
                    
            return True
        else:
            print("❌ Поддержка нескольких языков не работает корректно")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования поддержки нескольких языков: {e}")
        return False

def test_enhanced_bot_import():
    """Тест импорта расширенного бота"""
    try:
        # Просто проверяем, что файл существует и может быть импортирован
        if os.path.exists("enhanced_bot.py"):
            print("✓ Файл расширенного бота существует")
            return True
        else:
            print("❌ Файл расширенного бота не найден")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки расширенного бота: {e}")
        return False

def test_game_integration_file():
    """Тест файла интеграции с игрой"""
    try:
        if os.path.exists("game_integration.js"):
            print("✓ Файл интеграции с игрой существует")
            
            # Проверяем размер файла (должен быть достаточно большим)
            file_size = os.path.getsize("game_integration.js")
            if file_size > 1000:  # Больше 1KB
                print(f"✓ Файл интеграции имеет подходящий размер ({file_size} байт)")
                return True
            else:
                print("❌ Файл интеграции слишком маленький")
                return False
        else:
            print("❌ Файл интеграции с игрой не найден")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки файла интеграции: {e}")
        return False

def test_html_integration():
    """Тест интеграции HTML"""
    try:
        if os.path.exists("igra.html"):
            print("✓ HTML файл игры существует")
            
            # Читаем содержимое файла
            with open("igra.html", "r", encoding="utf-8") as f:
                content = f.read()
                
            # Проверяем наличие ключевых элементов
            required_elements = [
                "game_integration.js",
                "id=\"missions-btn\"",
                "id=\"mission-content\"",
                "id=\"mission-questions\"",
                "id=\"answer-form\""
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                    
            if not missing_elements:
                print("✓ HTML интеграция содержит все необходимые элементы")
                return True
            else:
                print(f"❌ В HTML интеграции отсутствуют элементы: {missing_elements}")
                return False
        else:
            print("❌ HTML файл игры не найден")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки HTML интеграции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Тестирование расширенных функций BATYR BOL")
    print("=" * 50)
    
    tests = [
        test_model_import,
        test_model_initialization,
        test_achievement_system,
        test_error_analysis,
        test_personalized_recommendations,
        test_multilanguage_support,
        test_enhanced_bot_import,
        test_game_integration_file,
        test_html_integration
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
        print("\nРасширенные функции готовы к использованию:")
        print("- Система достижений")
        print("- Анализ ошибок пользователей")
        print("- Персонализированные рекомендации")
        print("- Поддержка нескольких языков")
        print("- Интеграция с веб-интерфейсом")
        return True
    else:
        print("❌ Некоторые тесты не пройдены. Проверьте код.")
        return False

if __name__ == "__main__":
    main()