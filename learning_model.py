#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модель адаптивного обучения для Telegram-бота BATYR BOL
Эта модель генерирует контент о казахской истории и языке, задает вопросы
и адаптируется к уровню знаний пользователя.
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class AdaptiveLearningModel:
    """Адаптивная модель обучения для казахской истории и языка"""
    
    def __init__(self):
        """Инициализация модели"""
        self.content_database = self._initialize_content()
        self.question_templates = self._initialize_question_templates()
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.feedback_messages = self._initialize_feedback_messages()
        self.user_profiles = {}  # Хранение профилей пользователей
        self.achievements = self._initialize_achievements()  # Система достижений
        
    def _initialize_achievements(self) -> Dict:
        """Инициализация системы достижений"""
        return {
            "first_mission": {
                "name": "Первая миссия",
                "description": "Выполните первую миссию",
                "xp_reward": 5
            },
            "voice_master": {
                "name": "Мастер голоса",
                "description": "Выполните 10 голосовых миссий",
                "xp_reward": 10
            },
            "history_expert": {
                "name": "Эксперт по истории",
                "description": "Ответьте правильно на 20 вопросов по истории",
                "xp_reward": 15
            },
            "language_pro": {
                "name": "Профи языка",
                "description": "Ответьте правильно на 20 вопросов по языку",
                "xp_reward": 15
            },
            "streak_champion": {
                "name": "Чемпион по дням",
                "description": "Изучайте каждый день в течение 7 дней подряд",
                "xp_reward": 20
            }
        }
    
    def _initialize_content(self) -> Dict:
        """Инициализация базы контента о казахской истории и языке"""
        return {
            "history": [
                {
                    "title": "Основание Казахского ханства",
                    "text": "Казахское ханство было основано в 1465 году Жанибеком и Керем ханами. Это произошло после того, как они отделились от Узбекского ханства из-за конфликта с Абулхаиром ханом. Новое государство быстро развивалось благодаря выгодному географическому положению и сильной армии.",
                    "difficulty": "beginner",
                    "key_facts": ["1465 год", "Жанибек и Керей ханы", "отделение от Узбекского ханства"],
                    "keywords": ["ханство", "основание", "Жанибек", "Керей"]
                },
                {
                    "title": "Правление Абылай хана",
                    "text": "Абылай хан (1711-1781) был одним из самых выдающихся правителей Казахского ханства. Он сумел объединить три жуза, установил дипломатические отношения с Россией и Китаем, и успешно противостоял Джунгарам. Его столица находилась в Сарайшыке.",
                    "difficulty": "intermediate",
                    "key_facts": ["1711-1781", "объединение трех жузов", "дипломатия с Россией и Китаем"],
                    "keywords": ["Абылай", "джунгары", "Россия", "Китай"]
                },
                {
                    "title": "Великое жертвоприношение Казбека бия",
                    "text": "Казбек бий был известным бием Младшего жуза в конце XVIII века. Во время нашествия Джунгар он добровольно отдал своих сыновей в заложники, чтобы спасти свой народ. Его жертва спасла многих казахов от полного уничтожения и стала символом героизма и патриотизма.",
                    "difficulty": "advanced",
                    "key_facts": ["Младший жуз", "добровольное жертвоприношение", "спасение народа"],
                    "keywords": ["Казбек бий", "жертвоприношение", "патриотизм"]
                },
                # Дополнительный контент по истории
                {
                    "title": "Золотая Орда и ее влияние на Казахстан",
                    "text": "Золотая Орда была одним из самых могущественных государств Средневековья. Она оказала значительное влияние на формирование казахской государственности. Многие традиции, обычаи и административные практики Золотой Орды были унаследованы Казахским ханством.",
                    "difficulty": "intermediate",
                    "key_facts": ["Средневековье", "влияние на государственность", "традиции"],
                    "keywords": ["Золотая Орда", "традиции", "государственность"]
                },
                {
                    "title": "Казахско-Джунгарская война",
                    "text": "Казахско-Джунгарская война длилась с 1723 по 1756 год. Это был один из самых трагических периодов в истории Казахского ханства. Народ получил название 'Ақтабан шұбырынды' - Великое бедствие. Однако казахи смогли сохранить свою независимость.",
                    "difficulty": "advanced",
                    "key_facts": ["1723-1756", "Великое бедствие", "сохранение независимости"],
                    "keywords": ["Джунгары", "война", "независимость"]
                },
                {
                    "title": "Реформы в Казахском ханстве при Кайып хане",
                    "text": "Кайып хан провел важные реформы в государственном управлении. Он стремился централизовать власть и укрепить армию. При нем началось строительство укрепленных городов и развитие торговли с соседними государствами.",
                    "difficulty": "advanced",
                    "key_facts": ["реформы управления", "централизация", "армия"],
                    "keywords": ["Кайып хан", "реформы", "централизация"]
                }
            ],
            "language": [
                {
                    "title": "Алфавит казахского языка",
                    "text": "Современный казахский алфавит состоит из 31 буквы. В 1940 году была принята латинская графика, а в 1945 году - кириллица. В 2017 году снова планируется переход на латиницу. В алфавите есть уникальные буквы: ә, ғ, қ, ң, ө, ү, ұ, һ, і.",
                    "difficulty": "beginner",
                    "key_facts": ["31 буква", "латиница и кириллица", "уникальные буквы"],
                    "keywords": ["алфавит", "кириллица", "латиница", "буквы"]
                },
                {
                    "title": "Глаголы в казахском языке",
                    "text": "Глаголы в казахском языке изменяются по времени и лицам. Настоящее время образуется с помощью суффиксов: -мын/-мін (1 лицо), -сың/-сің (2 лицо), -ды/-ті (3 лицо). Прошедшее время образуется с помощью окончаний -ды/-ті, -ған/-ген, -қан/-кен.",
                    "difficulty": "intermediate",
                    "key_facts": ["изменение по времени", "суффиксы настоящего времени", "окончания прошедшего времени"],
                    "keywords": ["глаголы", "времена", "суффиксы", "окончания"]
                },
                {
                    "title": "Сложносокращенные слова в казахском языке",
                    "text": "Сложносокращенные слова (ССС) в казахском языке образуются путем соединения начальных частей слов. Например: университет + радио = универсиада, Казахстан + телевидение = КазТВ. Они широко используются в официальной и научной терминологии.",
                    "difficulty": "advanced",
                    "key_facts": ["соединение начальных частей", "официальная терминология", "примеры ССС"],
                    "keywords": ["сложносокращенные слова", "ССС", "терминология"]
                },
                # Дополнительный контент по языку
                {
                    "title": "Имена прилагательные в казахском языке",
                    "text": "Имена прилагательные в казахском языке изменяются по числам и падежам. В единственном числе они имеют 7 падежных форм, а во множественном - 6. Прилагательные согласуются с существительными в роде, числе и падеже.",
                    "difficulty": "intermediate",
                    "key_facts": ["изменение по числам", "падежи", "согласование"],
                    "keywords": ["прилагательные", "падежи", "согласование"]
                },
                {
                    "title": "Числительные в казахском языке",
                    "text": "Числительные в казахском языке делятся на количественные и порядковые. Количественные числительные изменяются по падежам. Особенности согласования зависят от типа числительного и существительного, к которому оно относится.",
                    "difficulty": "intermediate",
                    "key_facts": ["количественные", "порядковые", "согласование"],
                    "keywords": ["числительные", "количественные", "порядковые"]
                },
                {
                    "title": "Фразеологизмы казахского языка",
                    "text": "Фразеологизмы - это устойчивые выражения, значение которых не определяется значением составляющих их слов. В казахском языке много фразеологизмов, отражающих народную мудрость, обычаи и традиции казахского народа.",
                    "difficulty": "advanced",
                    "key_facts": ["устойчивые выражения", "народная мудрость", "традиции"],
                    "keywords": ["фразеологизмы", "мудрость", "традиции"]
                }
            ]
        }
    
    def _initialize_question_templates(self) -> Dict:
        """Инициализация шаблонов вопросов"""
        return {
            "beginner": [
                "Когда произошло событие, описанное в тексте?",
                "Кто главный герой описанного события?",
                "Как называется событие, о котором говорится в тексте?",
                "Где происходило описанное событие?",
                "Почему это событие важно?"
            ],
            "intermediate": [
                "Объясните причину описанного события.",
                "Каковы последствия описанного события?",
                "Сравните это событие с другими историческими событиями.",
                "Какие персонажи участвовали в этом событии?",
                "Оцените значимость этого события."
            ],
            "advanced": [
                "Проанализируйте влияние этого события на дальнейшее развитие.",
                "Сформулируйте критическое мнение о данном событии.",
                "Свяжите это событие с современностью.",
                "Обоснуйте важность этого события в историческом контексте.",
                "Выскажите свое мнение о последствиях этого события."
            ]
        }
    
    def _initialize_feedback_messages(self) -> Dict:
        "Инициализация сообщений обратной связи"
        return {
            "positive": [
                "Отлично! Вы хорошо справляетесь!",
                "Превосходно! Так держать!",
                "Великолепно! Вы делаете успехи!",
                "Замечательно! Продолжайте в том же духе!",
                "Прекрасно! Вы отлично понимаете материал!"
            ],
            "constructive": [
                "Хорошая попытка! Давайте попробуем еще раз.",
                "Вы на правильном пути! Обратите внимание на детали.",
                "Почти верно! Попробуйте еще раз.",
                "Не совсем так, но вы близки к правильному ответу.",
                "Еще одна попытка, и у вас получится!"
            ],
            "encouraging": [
                "Не переживайте! Учиться - это процесс.",
                "Каждая ошибка - это шаг к успеху.",
                "Вы сможете! Главное - не сдаваться.",
                "Попробуйте еще раз, у вас всё получится!",
                "Ошибки помогают нам учиться лучше."
            ]
        }
    
    def get_adaptive_content(self, user_level: str, content_type: str) -> Dict:
        """
        Получить контент соответствующий уровню пользователя
        
        Args:
            user_level: Уровень пользователя (beginner, intermediate, advanced)
            content_type: Тип контента (history, language)
        
        Returns:
            Словарь с контентом
        """
        # Фильтруем контент по типу и уровню
        filtered_content = [
            item for item in self.content_database[content_type] 
            if item["difficulty"] == user_level
        ]
        
        # Если нет контента для данного уровня, берем любой
        if not filtered_content:
            filtered_content = self.content_database[content_type]
        
        # Выбираем случайный контент
        return random.choice(filtered_content)
    
    def generate_questions(self, content: Dict, user_level: str, num_questions: int = 3, language: str = "ru") -> List[Dict]:
        """
        Генерировать вопросы на основе контента
        
        Args:
            content: Контент для генерации вопросов
            user_level: Уровень пользователя
            num_questions: Количество вопросов
            language: Язык вопросов ("ru" для русского, "kk" для казахского)
        
        Returns:
            Список вопросов
        """
        questions = []
        
        # Генерируем вопросы на основе шаблонов
        templates = self.question_templates[user_level]
        
        for i in range(min(num_questions, len(templates))):
            # Локализуем шаблоны вопросов
            localized_template = self._localize_template(templates[i], language)
            
            question = {
                "id": f"q_{datetime.now().timestamp()}_{i}",
                "text": localized_template,
                "type": "open" if user_level == "advanced" else "choice",
                "difficulty": user_level,
                "related_content": content["title"],
                "correct_answer": self._generate_correct_answer(content, templates[i]),
                "options": self._generate_options(content, templates[i]) if user_level != "advanced" else None,
                "language": language  # Добавляем информацию о языке
            }
            questions.append(question)
        
        # Добавляем тестовые вопросы
        test_questions = self._generate_test_questions(content, user_level, language)
        questions.extend(test_questions)
        
        return questions[:num_questions]
    
    def _localize_template(self, template: str, language: str) -> str:
        """Локализовать шаблон вопроса на указанный язык"""
        # Словарь переводов для основных шаблонов
        translations = {
            "ru": {
                "Когда произошло событие, описанное в тексте?": "Мәтінде сипатталған оқиға қашан болды?",
                "Кто главный герой описанного события?": "Сипатталған оқиғаның басты кейіпкері кім?",
                "Как называется событие, о котором говорится в тексте?": "Мәтінде қай оқиға туралы айтылады?",
                "Где происходило описанное событие?": "Сипатталған оқиға қайда болды?",
                "Почему это событие важно?": "Бұл оқиға неліктен маңызды?",
                "Объясните причину описанного события.": "Сипатталған оқиғаның себебін түсіндіріңіз.",
                "Каковы последствия описанного события?": "Сипатталған оқиғаның салдары қандай?",
                "Сравните это событие с другими историческими событиями.": "Бұл оқиғаны басқа тарихи оқиғалармен салыстырыңыз.",
                "Какие персонажи участвовали в этом событии?": "Бұл оқиғаға қай кейіпкерлер қатысты?",
                "Оцените значимость этого события.": "Бұл оқиғаның маңызын бағалаңыз.",
                "Проанализируйте влияние этого события на дальнейшее развитие.": "Бұл оқиғаның әрі қарай дамуына әсерін талдаңыз.",
                "Сформулируйте критическое мнение о данном событии.": "Бұл оқиға туралы сын тұрғысынан пікір білдіріңіз.",
                "Свяжите это событие с современностью.": "Бұл оқиғаны қазіргі таңмен байланыстырыңыз.",
                "Обоснуйте важность этого события в историческом контексте.": "Бұл оқиғаның тарихи контекстегі маңызын негіздеңіз.",
                "Выскажите свое мнение о последствиях этого события.": "Бұл оқиғаның салдары туралы өз пікіріңізді білдіріңіз."
            }
        }
        
        # Если запрошен казахский язык и есть перевод, возвращаем его
        if language == "kk" and template in translations["ru"]:
            return translations["ru"][template]
        
        # Иначе возвращаем оригинальный шаблон
        return template
    
    def _generate_correct_answer(self, content: Dict, template: str) -> str:
        """Генерировать правильный ответ на основе контента и шаблона вопроса"""
        # Это упрощенная реализация, в реальности потребуется более сложная логика
        if "когда" in template.lower():
            return content.get("key_facts", ["Ответ находится в тексте"])[0]
        elif "кто" in template.lower():
            return content.get("keywords", ["Персонаж из текста"])[0]
        else:
            return "Ответ можно найти в представленном тексте"
    
    def _generate_options(self, content: Dict, template: str) -> List[str]:
        """Генерировать варианты ответов для тестовых вопросов"""
        correct = self._generate_correct_answer(content, template)
        # Упрощенная реализация с фиктивными вариантами
        distractors = [
            "Это не упоминалось в тексте",
            "Событие произошло позже",
            "Это другой исторический период",
            "Персонаж не связан с этим событием"
        ]
        options = [correct] + random.sample(distractors, min(3, len(distractors)))
        random.shuffle(options)
        return options
    
    def _generate_test_questions(self, content: Dict, user_level: str, language: str = "ru") -> List[Dict]:
        """Генерировать тестовые вопросы"""
        test_questions = []
        
        if user_level == "beginner":
            # Простые тестовые вопросы
            question_text = self._localize_text(f"Что из перечисленного относится к теме '{content['title']}'?", language)
            q1 = {
                "id": f"tq_{datetime.now().timestamp()}_1",
                "text": question_text,
                "type": "choice",
                "difficulty": user_level,
                "related_content": content["title"],
                "correct_answer": content["key_facts"][0],
                "options": content["key_facts"] + [self._localize_text("Это не относится к теме", language)],
                "language": language
            }
            test_questions.append(q1)
        
        elif user_level == "intermediate":
            # Вопросы средней сложности
            question_text = self._localize_text("Расставьте события в хронологическом порядке:", language)
            q1 = {
                "id": f"tq_{datetime.now().timestamp()}_1",
                "text": question_text,
                "type": "ordering",
                "difficulty": user_level,
                "related_content": content["title"],
                "correct_answer": content["key_facts"],
                "options": list(reversed(content["key_facts"])),
                "language": language
            }
            test_questions.append(q1)
        
        elif user_level == "advanced":
            # Сложные аналитические вопросы
            question_text = self._localize_text(f"Проанализируйте значение события '{content['title']}' для развития Казахстана.", language)
            q1 = {
                "id": f"tq_{datetime.now().timestamp()}_1",
                "text": question_text,
                "type": "open",
                "difficulty": user_level,
                "related_content": content["title"],
                "correct_answer": self._localize_text("Ответ должен содержать анализ влияния события", language),
                "options": None,
                "language": language
            }
            test_questions.append(q1)
        
        return test_questions
    
    def _localize_text(self, text: str, language: str) -> str:
        """Локализовать текст на указанный язык"""
        # Словарь переводов
        translations = {
            "ru": {
                "Что из перечисленного относится к теме": "Тізімделген нәрселердің қайсысы тақырыпқа жатады",
                "Это не относится к теме": "Бұл тақырыпқа жатпайды",
                "Расставьте события в хронологическом порядке:": "Оқиғаларды хронологиялық тәртіпте орналастырыңыз:",
                "Проанализируйте значение события": "Оқиғаның маңызын талдаңыз",
                "для развития Казахстана": "Қазақстанның дамуы үшін",
                "Ответ должен содержать анализ влияния события": "Жауап оқиғаның әсерін талдауы тиіс"
            }
        }
        
        # Если запрошен казахский язык, пытаемся перевести
        if language == "kk":
            for ru_text, kk_text in translations["ru"].items():
                if ru_text in text:
                    return text.replace(ru_text, kk_text)
        
        # Иначе возвращаем оригинальный текст
        return text
    
    def evaluate_answer(self, question: Dict, user_answer: str, user_history: List, user_id: str = None, user_data: Dict = None) -> Tuple[bool, str, str, List]:
        """
        Оценить ответ пользователя
        
        Args:
            question: Вопрос
            user_answer: Ответ пользователя
            user_history: История ответов пользователя
            user_id: Идентификатор пользователя (опционально)
            user_data: Полные данные пользователя (опционально)
        
        Returns:
            Кортеж: (правильно/неправильно, сообщение, новый уровень пользователя, новые достижения)
        """
        # Упрощенная оценка - в реальности потребуется более сложная логика NLP
        is_correct = self._simple_evaluate(question["correct_answer"], user_answer)
        
        if is_correct:
            feedback = random.choice(self.feedback_messages["positive"])
            new_level = self._adjust_level(user_history, True)
        else:
            # Выбираем подходящее сообщение обратной связи
            if len([h for h in user_history if not h.get("correct", True)]) > 2:
                feedback = random.choice(self.feedback_messages["encouraging"])
            else:
                feedback = random.choice(self.feedback_messages["constructive"])
            new_level = self._adjust_level(user_history, False)
        
        # Проверяем достижения (если указаны user_id и user_data)
        new_achievements = []
        if user_id and user_data and hasattr(self, 'user_profiles'):
            new_achievements = self.check_achievements(user_id, user_data)
        
        return is_correct, feedback, new_level, new_achievements
    
    def _simple_evaluate(self, correct_answer: str, user_answer: str) -> bool:
        """Упрощенная оценка ответа"""
        # В реальности здесь должна быть сложная логика NLP
        correct_lower = correct_answer.lower()
        user_lower = user_answer.lower()
        
        # Проверяем совпадение ключевых слов
        return any(word in user_lower for word in correct_lower.split() if len(word) > 3)
    
    def _adjust_level(self, user_history: List, last_correct: bool) -> str:
        """Настроить уровень пользователя на основе истории ответов"""
        if not user_history:
            return "beginner"
        
        # Подсчитываем процент правильных ответов
        correct_count = sum(1 for h in user_history if h.get("correct", False))
        total_count = len(user_history)
        accuracy = correct_count / total_count if total_count > 0 else 0
        
        # Получаем текущий уровень (из последнего элемента истории)
        current_level = user_history[-1].get("level", "beginner") if user_history else "beginner"
        
        # Определяем индекс текущего уровня
        level_index = self.difficulty_levels.index(current_level)
        
        # Адаптируем уровень
        if accuracy > 0.8 and last_correct and level_index < len(self.difficulty_levels) - 1:
            # Повышаем уровень
            return self.difficulty_levels[level_index + 1]
        elif accuracy < 0.5 and not last_correct and level_index > 0:
            # Понижаем уровень
            return self.difficulty_levels[level_index - 1]
        else:
            # Оставляем тот же уровень
            return current_level
    
    def analyze_user_errors(self, user_id: str, user_history: List) -> Dict:
        """Анализ ошибок пользователя для персонализации обучения"""
        if not user_history:
            return {}
        
        # Собираем статистику по типам ошибок
        error_analysis = {
            "total_attempts": len(user_history),
            "correct_answers": sum(1 for h in user_history if h.get("correct", False)),
            "incorrect_answers": sum(1 for h in user_history if not h.get("correct", True)),
            "topic_performance": {},
            "difficulty_performance": {},
            "common_mistakes": []
        }
        
        # Анализируем производительность по темам и сложности
        for entry in user_history:
            topic = entry.get("topic", "unknown")
            difficulty = entry.get("difficulty", "beginner")
            
            # Статистика по темам
            if topic not in error_analysis["topic_performance"]:
                error_analysis["topic_performance"][topic] = {"correct": 0, "total": 0}
            
            # Статистика по сложности
            if difficulty not in error_analysis["difficulty_performance"]:
                error_analysis["difficulty_performance"][difficulty] = {"correct": 0, "total": 0}
            
            # Обновляем статистику
            if entry.get("correct", False):
                error_analysis["topic_performance"][topic]["correct"] += 1
                error_analysis["difficulty_performance"][difficulty]["correct"] += 1
            
            error_analysis["topic_performance"][topic]["total"] += 1
            error_analysis["difficulty_performance"][difficulty]["total"] += 1
        
        # Вычисляем проценты
        for topic in error_analysis["topic_performance"]:
            total = error_analysis["topic_performance"][topic]["total"]
            correct = error_analysis["topic_performance"][topic]["correct"]
            error_analysis["topic_performance"][topic]["accuracy"] = (correct / total * 100) if total > 0 else 0
        
        for difficulty in error_analysis["difficulty_performance"]:
            total = error_analysis["difficulty_performance"][difficulty]["total"]
            correct = error_analysis["difficulty_performance"][difficulty]["correct"]
            error_analysis["difficulty_performance"][difficulty]["accuracy"] = (correct / total * 100) if total > 0 else 0
        
        return error_analysis
    
    def get_personalized_recommendations(self, user_id: str, user_history: List) -> List[Dict]:
        """Получить персонализированные рекомендации на основе истории пользователя"""
        # Анализируем ошибки пользователя
        error_analysis = self.analyze_user_errors(user_id, user_history)
        
        # Определяем слабые места пользователя
        weak_topics = []
        weak_difficulties = []
        
        # Ищем темы с низкой точностью (< 70%)
        for topic, stats in error_analysis.get("topic_performance", {}).items():
            if stats.get("accuracy", 100) < 70:
                weak_topics.append(topic)
        
        # Ищем уровни сложности с низкой точностью
        for difficulty, stats in error_analysis.get("difficulty_performance", {}).items():
            if stats.get("accuracy", 100) < 70:
                weak_difficulties.append(difficulty)
        
        # Генерируем рекомендации
        recommendations = []
        
        # Рекомендуем контент по слабым темам
        for topic in weak_topics:
            # Ищем контент по слабой теме
            for content_type, contents in self.content_database.items():
                for content in contents:
                    if topic.lower() in content["title"].lower() or topic.lower() in content["keywords"]:
                        recommendations.append({
                            "type": "review",
                            "content": content,
                            "reason": f"Повторите материал по теме '{topic}'"
                        })
                        break
        
        # Рекомендуем более легкий контент, если пользователь struggles с высокой сложностью
        if "advanced" in weak_difficulties and len(weak_difficulties) > 1:
            # Ищем контент среднего уровня
            for content_type, contents in self.content_database.items():
                for content in contents:
                    if content["difficulty"] == "intermediate":
                        recommendations.append({
                            "type": "easier_content",
                            "content": content,
                            "reason": "Попробуйте материал среднего уровня перед возвращением к сложному"
                        })
                        break
                if recommendations:
                    break
        
        # Если у пользователя высокая точность, рекомендуем более сложный контент
        if error_analysis.get("correct_answers", 0) > error_analysis.get("total_attempts", 1) * 0.8:
            # Ищем контент более высокого уровня
            user_level = "beginner"  # по умолчанию
            if user_history:
                user_level = user_history[-1].get("level", "beginner")
            
            target_level = self._get_next_level(user_level)
            if target_level:
                for content_type, contents in self.content_database.items():
                    for content in contents:
                        if content["difficulty"] == target_level:
                            recommendations.append({
                                "type": "challenge",
                                "content": content,
                                "reason": "Попробуйте более сложный материал"
                            })
                            break
                    if recommendations:
                        break
        
        return recommendations[:3]  # Возвращаем максимум 3 рекомендации
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """Получить следующий уровень сложности"""
        level_index = self.difficulty_levels.index(current_level)
        if level_index < len(self.difficulty_levels) - 1:
            return self.difficulty_levels[level_index + 1]
        return None
    
    def check_achievements(self, user_id: str, user_data: Dict) -> List[Dict]:
        """Проверить, получил ли пользователь новые достижения"""
        new_achievements = []
        
        # Создаем профиль пользователя, если его нет
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {"achievements": set()}
        
        user_profile = self.user_profiles[user_id]
        earned_achievements = user_profile["achievements"]
        
        # Проверяем достижения
        
        # Первая миссия
        if "first_mission" not in earned_achievements and user_data.get("xp", 0) > 0:
            new_achievements.append(self.achievements["first_mission"])
            earned_achievements.add("first_mission")
        
        # Мастер голоса
        voice_missions_completed = sum(1 for h in user_data.get("history_answers", []) 
                                     if h.get("topic") == "voice" and h.get("correct", False))
        if "voice_master" not in earned_achievements and voice_missions_completed >= 10:
            new_achievements.append(self.achievements["voice_master"])
            earned_achievements.add("voice_master")
        
        # Эксперт по истории
        history_correct = sum(1 for h in user_data.get("history_answers", []) 
                            if h.get("topic") == "history" and h.get("correct", False))
        if "history_expert" not in earned_achievements and history_correct >= 20:
            new_achievements.append(self.achievements["history_expert"])
            earned_achievements.add("history_expert")
        
        # Профи языка
        language_correct = sum(1 for h in user_data.get("history_answers", []) 
                            if h.get("topic") == "language" and h.get("correct", False))
        if "language_pro" not in earned_achievements and language_correct >= 20:
            new_achievements.append(self.achievements["language_pro"])
            earned_achievements.add("language_pro")
        
        # Чемпион по дням
        if "streak_champion" not in earned_achievements and user_data.get("streak", 0) >= 7:
            new_achievements.append(self.achievements["streak_champion"])
            earned_achievements.add("streak_champion")
        
        return new_achievements
    
    def get_feedback_message(self, is_correct: bool, user_history: List) -> str:
        """Получить сообщение обратной связи"""
        if is_correct:
            return random.choice(self.feedback_messages["positive"])
        else:
            # Если пользователь часто ошибается, даем более поддерживающее сообщение
            incorrect_count = len([h for h in user_history if not h.get("correct", True)])
            if incorrect_count > 2:
                return random.choice(self.feedback_messages["encouraging"])
            else:
                return random.choice(self.feedback_messages["constructive"])

# Экземпляр модели для использования в боте
adaptive_model = AdaptiveLearningModel()

if __name__ == "__main__":
    # Демонстрация работы модели
    print("Демонстрация адаптивной модели обучения")
    print("=" * 50)
    
    # Получаем контент для начинающего пользователя
    content = adaptive_model.get_adaptive_content("beginner", "history")
    print(f"Контент: {content['title']}")
    print(f"Текст: {content['text']}")
    print()
    
    # Генерируем вопросы
    questions = adaptive_model.generate_questions(content, "beginner", 3)
    print("Сгенерированные вопросы:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q['text']}")
        if q['options']:
            for j, option in enumerate(q['options'], 1):
                print(f"   {j}) {option}")
    print()
    
    # Пример оценки ответа
    sample_answer = "Это произошло в 1465 году"
    is_correct, feedback, new_level = adaptive_model.evaluate_answer(
        questions[0], sample_answer, []
    )
    print(f"Оценка ответа '{sample_answer}':")
    print(f"Правильно: {is_correct}")
    print(f"Обратная связь: {feedback}")
    print(f"Новый уровень: {new_level}")