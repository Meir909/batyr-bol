using System;
using System.Collections.Generic;
using System.Threading;

namespace BatyrBolGame
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.Title = "Batyr Bol Adventure";
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("========================================");
            Console.WriteLine("        BATYR BOL ADVENTURE           ");
            Console.WriteLine("========================================");
            Console.ResetColor();
            
            Console.WriteLine("\nДобро пожаловать в приключение Батыра Бола!");
            Console.WriteLine("Нажмите любую клавишу для начала...");
            Console.ReadKey();
            Console.Clear();
            
            Game game = new Game();
            game.Start();
        }
    }

    class Game
    {
        private Player player;
        private Location currentLocation;
        private Dictionary<string, Location> locations;
        private bool gameRunning = true;
        
        public Game()
        {
            InitializeGame();
        }
        
        private void InitializeGame()
        {
            // Создаем локации
            locations = new Dictionary<string, Location>();
            
            locations["start"] = new Location(
                "Начальная деревня", 
                "Вы находитесь в небольшой деревне у подножия гор. Старик рассказывает вам о легендарном сокровище Батыра Бола, спрятанном в древней крепости.",
                new Dictionary<string, string>
                {
                    {"north", "forest"},
                    {"east", "river"},
                    {"west", "mountains"}
                }
            );
            
            locations["forest"] = new Location(
                "Тёмный лес", 
                "Вы вошли в густой лес. Деревья здесь такие высокие, что закрывают солнце. Вдалеке слышен странный звук.",
                new Dictionary<string, string>
                {
                    {"south", "start"},
                    {"north", "cave"},
                    {"east", "river"}
                }
            );
            
            locations["river"] = new Location(
                "Река", 
                "Быстрая река преграждает вам путь. Через реку перекинут старый деревянный мост. На другом берегу виднеется тропинка.",
                new Dictionary<string, string>
                {
                    {"west", "start"},
                    {"south", "castle"},
                    {"east", "forest"}
                }
            );
            
            locations["mountains"] = new Location(
                "Горы", 
                "Вы стоите у подножия высоких гор. Здесь очень холодно и ветрено. Наверху виднеется пещера.",
                new Dictionary<string, string>
                {
                    {"east", "start"},
                    {"up", "cave"}
                }
            );
            
            locations["cave"] = new Location(
                "Пещера", 
                "Тёмная пещера с таинственными надписями на стенах. В центре пещеры стоит древний алтарь.",
                new Dictionary<string, string>
                {
                    {"south", "forest"},
                    {"down", "mountains"}
                }
            );
            
            locations["castle"] = new Location(
                "Древняя крепость", 
                "Вы пришли к древней крепости Батыра Бола. Ворота заперты, но вы видите небольшую боковую дверь.",
                new Dictionary<string, string>
                {
                    {"north", "river"},
                    {"inside", "throne"}
                }
            );
            
            locations["throne"] = new Location(
                "Тронный зал", 
                "Вы в тронном зале крепости. На троне сидит призрак Батыра Бола! Он предлагает вам испытание.",
                new Dictionary<string, string>
                {
                    {"outside", "castle"}
                }
            );
            
            // Устанавливаем начальную локацию
            currentLocation = locations["start"];
            
            // Создаем игрока
            player = new Player("Герой");
        }
        
        public void Start()
        {
            while (gameRunning)
            {
                Console.Clear();
                DisplayCurrentLocation();
                DisplayPlayerStatus();
                Console.WriteLine("\nЧто вы хотите сделать?");
                Console.WriteLine("1. Осмотреться");
                Console.WriteLine("2. Переместиться (север/юг/восток/запад/вверх/вниз/внутрь/снаружи)");
                Console.WriteLine("3. Взять предмет");
                Console.WriteLine("4. Использовать предмет");
                Console.WriteLine("5. Поговорить");
                Console.WriteLine("6. Показать инвентарь");
                Console.WriteLine("7. Выйти из игры");
                
                Console.Write("\nВаш выбор: ");
                string choice = Console.ReadLine()?.ToLower();
                
                ProcessCommand(choice);
            }
        }
        
        private void DisplayCurrentLocation()
        {
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine($"=== {currentLocation.Name} ===");
            Console.ResetColor();
            Console.WriteLine(currentLocation.Description);
            
            if (currentLocation.Exits.Count > 0)
            {
                Console.WriteLine("\nВыходы: " + string.Join(", ", currentLocation.Exits.Keys));
            }
        }
        
        private void DisplayPlayerStatus()
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine($"\n=== {player.Name} ===");
            Console.WriteLine($"Здоровье: {player.Health}/100");
            Console.WriteLine($"Опыт: {player.Experience}");
            Console.WriteLine($"Уровень: {player.Level}");
            Console.ResetColor();
        }
        
        private void ProcessCommand(string command)
        {
            switch (command)
            {
                case "1":
                case "осмотреться":
                    LookAround();
                    break;
                case "2":
                case "переместиться":
                    Move();
                    break;
                case "3":
                case "взять":
                    TakeItem();
                    break;
                case "4":
                case "использовать":
                    UseItem();
                    break;
                case "5":
                case "поговорить":
                    Talk();
                    break;
                case "6":
                case "инвентарь":
                    ShowInventory();
                    break;
                case "7":
                case "выйти":
                    gameRunning = false;
                    Console.WriteLine("Спасибо за игру! До свидания!");
                    Thread.Sleep(2000);
                    break;
                default:
                    Console.WriteLine("Неизвестная команда. Попробуйте снова.");
                    Thread.Sleep(1500);
                    break;
            }
        }
        
        private void LookAround()
        {
            Console.WriteLine("\nВы внимательно осматриваетесь вокруг...");
            Thread.Sleep(1000);
            
            if (currentLocation.Name == "Пещера")
            {
                Console.WriteLine("Вы замечаете свиток на алтаре и странные символы на стенах.");
                if (!player.HasItem("Святой свиток"))
                {
                    Console.WriteLine("На алтаре лежит Святой свиток!");
                }
            }
            else if (currentLocation.Name == "Тронный зал")
            {
                Console.WriteLine("Призрак Батыра Бола смотрит на вас с ожиданием.");
                Console.WriteLine("За троном виднеется сундук с сокровищами.");
            }
            else if (currentLocation.Name == "Река")
            {
                Console.WriteLine("Вы замечаете рыбу в воде и красивые камни на берегу.");
            }
            
            Console.WriteLine("\nНажмите любую клавишу для продолжения...");
            Console.ReadKey();
        }
        
        private void Move()
        {
            Console.Write("\nКуда хотите пойти? ");
            string direction = Console.ReadLine()?.ToLower();
            
            if (currentLocation.Exits.ContainsKey(direction))
            {
                string nextLocationName = currentLocation.Exits[direction];
                currentLocation = locations[nextLocationName];
                
                Console.WriteLine($"Вы перемещаетесь в {currentLocation.Name}...");
                Thread.Sleep(1000);
                
                // Проверяем особые события
                CheckSpecialEvents();
            }
            else
            {
                Console.WriteLine("Туда нельзя пройти.");
                Thread.Sleep(1500);
            }
        }
        
        private void TakeItem()
        {
            if (currentLocation.Name == "Пещера" && !player.HasItem("Святой свиток"))
            {
                player.AddItem("Святой свиток");
                player.AddExperience(50);
                Console.WriteLine("Вы взяли Святой свиток! Получено 50 опыта.");
                Thread.Sleep(2000);
            }
            else if (currentLocation.Name == "Река")
            {
                player.AddItem("Магический камень");
                Console.WriteLine("Вы нашли Магический камень у реки!");
                Thread.Sleep(2000);
            }
            else
            {
                Console.WriteLine("Здесь нечего брать.");
                Thread.Sleep(1500);
            }
        }
        
        private void UseItem()
        {
            if (player.Inventory.Count == 0)
            {
                Console.WriteLine("У вас нет предметов.");
                Thread.Sleep(1500);
                return;
            }
            
            Console.WriteLine("\nКакой предмет использовать?");
            for (int i = 0; i < player.Inventory.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {player.Inventory[i]}");
            }
            
            Console.Write("Ваш выбор: ");
            if (int.TryParse(Console.ReadLine(), out int choice) && choice > 0 && choice <= player.Inventory.Count)
            {
                string item = player.Inventory[choice - 1];
                UseSpecificItem(item);
            }
            else
            {
                Console.WriteLine("Неверный выбор.");
                Thread.Sleep(1500);
            }
        }
        
        private void UseSpecificItem(string item)
        {
            switch (item)
            {
                case "Святой свиток":
                    if (currentLocation.Name == "Тронный зал")
                    {
                        Console.WriteLine("Вы читаете Святой свиток. Призрак Батыра Бола одобрительно кивает!");
                        Console.WriteLine("Вы прошли испытание! Получено 200 опыта!");
                        player.AddExperience(200);
                        player.RemoveItem("Святой свиток");
                    }
                    else
                    {
                        Console.WriteLine("Святой свиток светится, но здесь его использовать нельзя.");
                    }
                    break;
                case "Магический камень":
                    Console.WriteLine("Магический камень начинает светиться и восстанавливает ваше здоровье!");
                    player.Health = Math.Min(100, player.Health + 30);
                    Console.WriteLine($"Здоровье восстановлено до {player.Health}!");
                    player.RemoveItem("Магический камень");
                    break;
                default:
                    Console.WriteLine("Вы не можете использовать этот предмет здесь.");
                    break;
            }
            Thread.Sleep(2000);
        }
        
        private void Talk()
        {
            if (currentLocation.Name == "Тронный зал")
            {
                Console.WriteLine("\nПризрак Батыра Бола говорит:");
                Console.WriteLine("'Добро пожаловать, искатель приключений! Я - Батыр Бол, великий воин прошлого.");
                Console.WriteLine("Чтобы доказать свою доблесть, принеси мне Святой свиток из древней пещеры.");
                Console.WriteLine("Тогда я открою тебе доступ к сокровищам и поделюсь мудростью.'");
                
                if (player.HasItem("Святой свиток"))
                {
                    Console.WriteLine("\nПризрак замечает свиток в ваших руках и улыбается.");
                    Console.WriteLine("'Отлично! Ты доказал свою доблесть!'");
                    Console.WriteLine("Призрак исчезает, оставляя после себя сундук с сокровищами!");
                    player.AddItem("Золотой ключ");
                    player.AddExperience(300);
                    WinGame();
                }
            }
            else if (currentLocation.Name == "Начальная деревня")
            {
                Console.WriteLine("\nСтарик в деревне говорит:");
                Console.WriteLine("'Слышал я, ты ищешь сокровища Батыра Бола. Будь осторожен, молодой герой!'");
                Console.WriteLine("'Говорят, что в пещере спрятан Святой свиток, который поможет тебе.'");
            }
            else
            {
                Console.WriteLine("Здесь не с кем говорить.");
            }
            Thread.Sleep(3000);
        }
        
        private void ShowInventory()
        {
            Console.WriteLine("\n=== ИНВЕНТАРЬ ===");
            if (player.Inventory.Count == 0)
            {
                Console.WriteLine("Инвентарь пуст.");
            }
            else
            {
                for (int i = 0; i < player.Inventory.Count; i++)
                {
                    Console.WriteLine($"{i + 1}. {player.Inventory[i]}");
                }
            }
            Console.WriteLine("\nНажмите любую клавишу для продолжения...");
            Console.ReadKey();
        }
        
        private void CheckSpecialEvents()
        {
            // Случайные события
            Random random = new Random();
            if (random.Next(1, 10) == 1) // 10% шанс
            {
                Console.WriteLine("\nВнезапное событие!");
                Console.WriteLine("Вы натыкаетесь на дикое животное!");
                Console.WriteLine("1. Сражаться");
                Console.WriteLine("2. Убежать");
                
                Console.Write("Ваш выбор: ");
                string choice = Console.ReadLine();
                
                if (choice == "1")
                {
                    Console.WriteLine("Вы храбро сражаетесь и побеждаете животное!");
                    player.AddExperience(25);
                    player.Health -= 10;
                    Console.WriteLine("Получено 25 опыта, но потеряно 10 здоровья.");
                }
                else
                {
                    Console.WriteLine("Вы убегаете от животного.");
                    player.Health -= 5;
                    Console.WriteLine("Потеряно 5 здоровья.");
                }
                Thread.Sleep(2000);
            }
        }
        
        private void WinGame()
        {
            Console.Clear();
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("========================================");
            Console.WriteLine("        ПОБЕДА!                       ");
            Console.WriteLine("========================================");
            Console.ResetColor();
            Console.WriteLine("\nПоздравляю! Вы завершили приключение Батыра Бола!");
            Console.WriteLine("Вы нашли все сокровища и доказали свою доблесть!");
            Console.WriteLine($"\nФинальная статистика:");
            Console.WriteLine($"Уровень: {player.Level}");
            Console.WriteLine($"Опыт: {player.Experience}");
            Console.WriteLine($"Здоровье: {player.Health}/100");
            Console.WriteLine($"Предметы в инвентаре: {player.Inventory.Count}");
            
            gameRunning = false;
            Console.WriteLine("\nНажмите любую клавишу для выхода...");
            Console.ReadKey();
        }
    }
    
    class Player
    {
        public string Name { get; private set; }
        public int Health { get; set; }
        public int Experience { get; private set; }
        public int Level { get; private set; }
        public List<string> Inventory { get; private set; }
        
        public Player(string name)
        {
            Name = name;
            Health = 100;
            Experience = 0;
            Level = 1;
            Inventory = new List<string>();
        }
        
        public void AddItem(string item)
        {
            Inventory.Add(item);
        }
        
        public void RemoveItem(string item)
        {
            Inventory.Remove(item);
        }
        
        public bool HasItem(string item)
        {
            return Inventory.Contains(item);
        }
        
        public void AddExperience(int exp)
        {
            Experience += exp;
            
            // Проверка повышения уровня
            int newLevel = (Experience / 100) + 1;
            if (newLevel > Level)
            {
                Level = newLevel;
                Health = 100; // Полное восстановление здоровья при повышении уровня
                Console.WriteLine($"\nВЫ ПОВЫСИЛИ УРОВЕНЬ! Теперь у вас уровень {Level}!");
            }
        }
    }
    
    class Location
    {
        public string Name { get; private set; }
        public string Description { get; private set; }
        public Dictionary<string, string> Exits { get; private set; }
        
        public Location(string name, string description, Dictionary<string, string> exits)
        {
            Name = name;
            Description = description;
            Exits = exits;
        }
    }
}
