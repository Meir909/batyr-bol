#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batyr Bol Adventure - Простая версия игры на Python
Работает без установки дополнительных библиотек
"""

import os
import sys
import time
import random

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03):
    """Построчный вывод текста с задержкой"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_title():
    """Вывод заголовка игры"""
    clear_screen()
    print(f"{Colors.GREEN}{'='*40}{Colors.RESET}")
    print(f"{Colors.GREEN}{'        BATYR BOL ADVENTURE':^40}{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*40}{Colors.RESET}")
    print()
    slow_print("Добро пожаловать в приключение Батыра Бола!")
    slow_print("Нажмите Enter для начала...")
    input()

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.experience = 0
        self.level = 1
        self.inventory = []
    
    def add_item(self, item):
        self.inventory.append(item)
        slow_print(f"Вы получили: {item}")
    
    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
    
    def has_item(self, item):
        return item in self.inventory
    
    def add_experience(self, exp):
        self.experience += exp
        old_level = self.level
        self.level = (self.experience // 100) + 1
        if self.level > old_level:
            slow_print(f"{Colors.YELLOW}ВЫ ПОВЫСИЛИ УРОВЕНЬ! Теперь у вас уровень {self.level}!{Colors.RESET}")
            self.health = 100
    
    def show_status(self):
        print(f"{Colors.CYAN}=== {self.name} ==={Colors.RESET}")
        print(f"Здоровье: {self.health}/100")
        print(f"Опыт: {self.experience}")
        print(f"Уровень: {self.level}")
    
    def show_inventory(self):
        print(f"\n{Colors.CYAN}=== ИНВЕНТАРЬ ==={Colors.RESET}")
        if not self.inventory:
            print("Инвентарь пуст.")
        else:
            for i, item in enumerate(self.inventory, 1):
                print(f"{i}. {item}")

class Location:
    def __init__(self, name, description, exits):
        self.name = name
        self.description = description
        self.exits = exits
    
    def show_info(self):
        print(f"{Colors.YELLOW}=== {self.name} ==={Colors.RESET}")
        print(self.description)
        if self.exits:
            print(f"\nВыходы: {', '.join(self.exits.keys())}")

class Game:
    def __init__(self):
        self.player = Player("Герой")
        self.locations = {}
        self.current_location = None
        self.game_running = True
        self.init_locations()
    
    def init_locations(self):
        """Инициализация локаций"""
        self.locations = {
            "start": Location(
                "Начальная деревня",
                "Вы находитесь в небольшой деревне у подножия гор. Старик рассказывает вам о легендарном сокровище Батыра Бола, спрятанном в древней крепости.",
                {"север": "forest", "восток": "river", "запад": "mountains"}
            ),
            "forest": Location(
                "Тёмный лес",
                "Вы вошли в густой лес. Деревья здесь такие высокие, что закрывают солнце. Вдалеке слышен странный звук.",
                {"юг": "start", "север": "cave", "восток": "river"}
            ),
            "river": Location(
                "Река",
                "Быстрая река преграждает вам путь. Через реку перекинут старый деревянный мост. На другом берегу виднеется тропинка.",
                {"запад": "start", "юг": "castle", "восток": "forest"}
            ),
            "mountains": Location(
                "Горы",
                "Вы стоите у подножия высоких гор. Здесь очень холодно и ветрено. Наверху виднеется пещера.",
                {"восток": "start", "вверх": "cave"}
            ),
            "cave": Location(
                "Пещера",
                "Тёмная пещера с таинственными надписями на стенах. В центре пещеры стоит древний алтарь.",
                {"юг": "forest", "вниз": "mountains"}
            ),
            "castle": Location(
                "Древняя крепость",
                "Вы пришли к древней крепости Батыра Бола. Ворота заперты, но вы видите небольшую боковую дверь.",
                {"север": "river", "внутрь": "throne"}
            ),
            "throne": Location(
                "Тронный зал",
                "Вы в тронном зале крепости. На троне сидит призрак Батыра Бола! Он предлагает вам испытание.",
                {"снаружи": "castle"}
            )
        }
        self.current_location = self.locations["start"]
    
    def start(self):
        """Начало игры"""
        while self.game_running:
            clear_screen()
            self.current_location.show_info()
            print()
            self.player.show_status()
            print()
            self.show_menu()
            
            choice = input("\nВаш выбор: ").strip().lower()
            self.process_command(choice)
    
    def show_menu(self):
        """Показать меню действий"""
        print("Что вы хотите сделать?")
        print("1. Осмотреться")
        print("2. Переместиться")
        print("3. Взять предмет")
        print("4. Использовать предмет")
        print("5. Поговорить")
        print("6. Показать инвентарь")
        print("7. Выйти из игры")
    
    def process_command(self, command):
        """Обработка команд"""
        if command in ["1", "осмотреться"]:
            self.look_around()
        elif command in ["2", "переместиться"]:
            self.move()
        elif command in ["3", "взять"]:
            self.take_item()
        elif command in ["4", "использовать"]:
            self.use_item()
        elif command in ["5", "поговорить"]:
            self.talk()
        elif command in ["6", "инвентарь"]:
            self.show_inventory()
        elif command in ["7", "выйти"]:
            self.quit_game()
        else:
            slow_print("Неизвестная команда. Попробуйте снова.")
            time.sleep(1.5)
    
    def look_around(self):
        """Осмотреться"""
        slow_print("\nВы внимательно осматриваетесь вокруг...")
        time.sleep(1)
        
        if self.current_location.name == "Пещера":
            slow_print("Вы замечаете свиток на алтаре и странные символы на стенах.")
            if not self.player.has_item("Святой свиток"):
                slow_print("На алтаре лежит Святой свиток!")
        elif self.current_location.name == "Тронный зал":
            slow_print("Призрак Батыра Бола смотрит на вас с ожиданием.")
            slow_print("За троном виднеется сундук с сокровищами.")
        elif self.current_location.name == "Река":
            slow_print("Вы замечаете рыбу в воде и красивые камни на берегу.")
        
        input("\nНажмите Enter для продолжения...")
    
    def move(self):
        """Перемещение"""
        direction = input("\nКуда хотите пойти? ").strip().lower()
        
        if direction in self.current_location.exits:
            next_location_name = self.current_location.exits[direction]
            self.current_location = self.locations[next_location_name]
            slow_print(f"Вы перемещаетесь в {self.current_location.name}...")
            time.sleep(1)
            self.check_special_events()
        else:
            slow_print("Туда нельзя пройти.")
            time.sleep(1.5)
    
    def take_item(self):
        """Взять предмет"""
        if self.current_location.name == "Пещера" and not self.player.has_item("Святой свиток"):
            self.player.add_item("Святой свиток")
            self.player.add_experience(50)
            slow_print("Получено 50 опыта!")
        elif self.current_location.name == "Река":
            self.player.add_item("Магический камень")
        else:
            slow_print("Здесь нечего брать.")
        
        time.sleep(2)
    
    def use_item(self):
        """Использовать предмет"""
        if not self.player.inventory:
            slow_print("У вас нет предметов.")
            time.sleep(1.5)
            return
        
        print("\nКакой предмет использовать?")
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{i}. {item}")
        
        try:
            choice = int(input("Ваш выбор: ")) - 1
            if 0 <= choice < len(self.player.inventory):
                item = self.player.inventory[choice]
                self.use_specific_item(item)
            else:
                slow_print("Неверный выбор.")
                time.sleep(1.5)
        except ValueError:
            slow_print("Неверный выбор.")
            time.sleep(1.5)
    
    def use_specific_item(self, item):
        """Использовать конкретный предмет"""
        if item == "Святой свиток":
            if self.current_location.name == "Тронный зал":
                slow_print("Вы читаете Святой свиток. Призрак Батыра Бола одобрительно кивает!")
                slow_print("Вы прошли испытание! Получено 200 опыта!")
                self.player.add_experience(200)
                self.player.remove_item("Святой свиток")
            else:
                slow_print("Святой свиток светится, но здесь его использовать нельзя.")
        elif item == "Магический камень":
            slow_print("Магический камень начинает светиться и восстанавливает ваше здоровье!")
            self.player.health = min(100, self.player.health + 30)
            slow_print(f"Здоровье восстановлено до {self.player.health}!")
            self.player.remove_item("Магический камень")
        else:
            slow_print("Вы не можете использовать этот предмет здесь.")
        
        time.sleep(2)
    
    def talk(self):
        """Поговорить"""
        if self.current_location.name == "Тронный зал":
            slow_print("\nПризрак Батыра Бола говорит:")
            slow_print("'Добро пожаловать, искатель приключений! Я - Батыр Бол, великий воин прошлого.'")
            slow_print("'Чтобы доказать свою доблесть, принеси мне Святой свиток из древней пещеры.'")
            slow_print("'Тогда я открою тебе доступ к сокровищам и поделюсь мудростью.'")
            
            if self.player.has_item("Святой свиток"):
                slow_print("\nПризрак замечает свиток в ваших руках и улыбается.")
                slow_print("'Отлично! Ты доказал свою доблесть!'")
                slow_print("Призрак исчезает, оставляя после себя сундук с сокровищами!")
                self.player.add_item("Золотой ключ")
                self.player.add_experience(300)
                self.win_game()
        elif self.current_location.name == "Начальная деревня":
            slow_print("\nСтарик в деревне говорит:")
            slow_print("'Слышал я, ты ищешь сокровища Батыра Бола. Будь осторожен, молодой герой!'")
            slow_print("'Говорят, что в пещере спрятан Святой свиток, который поможет тебе.'")
        else:
            slow_print("Здесь не с кем говорить.")
        
        time.sleep(3)
    
    def show_inventory(self):
        """Показать инвентарь"""
        self.player.show_inventory()
        input("\nНажмите Enter для продолжения...")
    
    def check_special_events(self):
        """Проверка случайных событий"""
        if random.randint(1, 10) == 1:  # 10% шанс
            slow_print("\nВнезапное событие!")
            slow_print("Вы натыкаетесь на дикое животное!")
            print("1. Сражаться")
            print("2. Убежать")
            
            choice = input("Ваш выбор: ").strip()
            
            if choice == "1":
                slow_print("Вы храбро сражаетесь и побеждаете животное!")
                self.player.add_experience(25)
                self.player.health -= 10
                slow_print("Получено 25 опыта, но потеряно 10 здоровья.")
            else:
                slow_print("Вы убегаете от животного.")
                self.player.health -= 5
                slow_print("Потеряно 5 здоровья.")
            
            time.sleep(2)
    
    def quit_game(self):
        """Выйти из игры"""
        self.game_running = False
        slow_print("Спасибо за игру! До свидания!")
        time.sleep(2)
    
    def win_game(self):
        """Победа в игре"""
        clear_screen()
        print(f"{Colors.YELLOW}{'='*40}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'        ПОБЕДА!':^40}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*40}{Colors.RESET}")
        slow_print("\nПоздравляю! Вы завершили приключение Батыра Бола!")
        slow_print("Вы нашли все сокровища и доказали свою доблесть!")
        
        print(f"\nФинальная статистика:")
        print(f"Уровень: {self.player.level}")
        print(f"Опыт: {self.player.experience}")
        print(f"Здоровье: {self.player.health}/100")
        print(f"Предметы в инвентаре: {len(self.player.inventory)}")
        
        self.game_running = False
        input("\nНажмите Enter для выхода...")

def main():
    """Главная функция"""
    try:
        print_title()
        game = Game()
        game.start()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.YELLOW}Игра прервана. До свидания!{Colors.RESET}")
    except Exception as e:
        clear_screen()
        print(f"{Colors.RED}Произошла ошибка: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
