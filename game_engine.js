/**
 * BATYR BOL - Game Engine
 * Система энергии, вопросов с вариантами ответов, озвучка
 * 4 уровня сложности по возрасту
 */

// Уровни сложности
const DIFFICULTY_LEVELS = {
    1: {
        name_kz: 'Бастаушы (Ертегілер)',
        name_ru: 'Начинающий (Сказки)',
        age: '7-10 жас',
        age_ru: '7-10 лет',
        description_kz: 'Қазақ ертегілері мен аңыздары. 5 оңай сұрақ.',
        description_ru: 'Казахские сказки и легенды. 5 легких вопросов.',
        icon: '🌱',
        textLength: 'short',      // 3-4 сөйлем
        optionsCount: 2,          // 2 вариант
        questionsCount: 5,        // 5 сұрақ
        showHints: true,          // Көмек көрсету
        energyBonus: 5            // Бонус энергия
    },
    2: {
        name_kz: 'Орташа',
        name_ru: 'Средний',
        age: '11-14 жас',
        age_ru: '11-14 лет',
        description_kz: 'Орташа мәтіндер, аз көмек',
        description_ru: 'Средние тексты, меньше подсказок',
        icon: '🌿',
        textLength: 'medium',     // 5-6 сөйлем
        optionsCount: 3,          // 3 вариант
        questionsCount: 7,        // 7 сұрақ
        showHints: true,
        energyBonus: 3
    },
    3: {
        name_kz: 'Жоғары',
        name_ru: 'Продвинутый',
        age: '15-17 жас',
        age_ru: '15-17 лет',
        description_kz: 'Үлкен мәтіндер, аз көмек',
        description_ru: 'Большие тексты, мало подсказок',
        icon: '🌳',
        textLength: 'long',       // 7-8 сөйлем
        optionsCount: 4,          // 4 вариант
        questionsCount: 10,       // 10 сұрақ
        showHints: false,
        energyBonus: 2
    },
    4: {
        name_kz: 'Сарапшы (Ресми деректер)',
        name_ru: 'Эксперт (Официальные источники)',
        age: '17+ жас',
        age_ru: '17+ лет',
        description_kz: 'Ресми құжаттар мен деректер. 15 өте қиын сұрақ.',
        description_ru: 'Официальные документы и источники. 15 очень трудных вопросов.',
        icon: '🎯',
        textLength: 'hard_pro',   // 100-150 сөз
        optionsCount: 4,          // 4 вариант
        questionsCount: 15,       // 15 сұрақ
        showHints: false,         // Көмек жоқ
        energyBonus: 10,          // Повышенный бонус за сложность
        isENT: true               // ЕНТ режимі
    }
};

class GameEngine {
    constructor() {
        this.energy = 20;
        this.maxEnergy = 20;
        this.correctStreak = 0;
        this.currentQuestionIndex = 0;
        this.questions = [];
        this.missionText = '';
        this.missionTopic = '';
        this.totalCorrect = 0;
        this.totalWrong = 0;
        this.isSpeaking = false;
        this.language = 'kz';
        
        // Уровень сложности (1-4)
        this.difficultyLevel = this.loadDifficultyLevel();
        
        this.synthesis = window.speechSynthesis;
    }
    
    // Загрузка уровня сложности из localStorage
    loadDifficultyLevel() {
        const saved = localStorage.getItem('batyrbol_difficulty');
        return saved ? parseInt(saved) : null;
    }
    
    // Сохранение уровня сложности
    setDifficultyLevel(level) {
        this.difficultyLevel = level;
        localStorage.setItem('batyrbol_difficulty', level.toString());
    }
    
    // Получение настроек текущего уровня
    getCurrentLevelSettings() {
        return DIFFICULTY_LEVELS[this.difficultyLevel] || DIFFICULTY_LEVELS[1];
    }
    
    // Показать экран выбора уровня
    showLevelSelection() {
        const container = document.getElementById('mission-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="space-y-6">
                <div class="text-center mb-8">
                    <h2 class="text-3xl font-bold text-white mb-2">
                        ${this.language === 'kz' ? 'Деңгейіңді таңдаңыз' : 'Выберите уровень'}
                    </h2>
                    <p class="text-zinc-400">
                        ${this.language === 'kz' ? 'Жасыңызға сәйкес деңгейді таңдаңыз' : 'Выберите уровень по возрасту'}
                    </p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${Object.entries(DIFFICULTY_LEVELS).map(([level, config]) => `
                        <button onclick="gameEngine.selectLevel(${level})" 
                            class="p-6 rounded-2xl border-2 ${level == 4 ? 'border-gold-500/50 bg-gold-500/10' : 'border-white/10 bg-zinc-900/50'} hover:border-gold-500/50 hover:bg-zinc-800/50 transition-all text-left group">
                            <div class="flex items-start gap-4">
                                <div class="text-4xl">${config.icon}</div>
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 mb-1">
                                        <h3 class="text-xl font-bold text-white">
                                            ${this.language === 'kz' ? config.name_kz : config.name_ru}
                                        </h3>
                                        ${level == 4 ? '<span class="px-2 py-0.5 bg-gold-500 text-black text-xs font-bold rounded">ЕНТ</span>' : ''}
                                    </div>
                                    <p class="text-gold-400 text-sm mb-2">
                                        ${this.language === 'kz' ? config.age : config.age_ru}
                                    </p>
                                    <p class="text-zinc-400 text-sm">
                                        ${this.language === 'kz' ? config.description_kz : config.description_ru}
                                    </p>
                                </div>
                            </div>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Выбор уровня
    selectLevel(level) {
        this.setDifficultyLevel(level);
        
        // Показываем подтверждение
        const config = DIFFICULTY_LEVELS[level];
        const container = document.getElementById('mission-content');
        
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="text-6xl mb-6">${config.icon}</div>
                <h3 class="text-2xl font-bold text-white mb-2">
                    ${this.language === 'kz' ? config.name_kz : config.name_ru}
                </h3>
                <p class="text-gold-400 mb-6">${this.language === 'kz' ? config.age : config.age_ru}</p>
                
                <div class="max-w-md mx-auto bg-zinc-900/50 rounded-2xl p-6 border border-white/10 mb-8">
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div class="text-left">
                            <span class="text-zinc-500">${this.language === 'kz' ? 'Сұрақтар' : 'Вопросов'}:</span>
                            <span class="text-white font-medium ml-2">${config.questionsCount}</span>
                        </div>
                        <div class="text-left">
                            <span class="text-zinc-500">${this.language === 'kz' ? 'Варианттар' : 'Вариантов'}:</span>
                            <span class="text-white font-medium ml-2">${config.optionsCount}</span>
                        </div>
                        <div class="text-left">
                            <span class="text-zinc-500">${this.language === 'kz' ? 'Көмек' : 'Подсказки'}:</span>
                            <span class="text-white font-medium ml-2">${config.showHints ? '✅' : '❌'}</span>
                        </div>
                        <div class="text-left">
                            <span class="text-zinc-500">${this.language === 'kz' ? 'Бонус' : 'Бонус'}:</span>
                            <span class="text-white font-medium ml-2">+${config.energyBonus} ⚡</span>
                        </div>
                    </div>
                </div>
                
                <button onclick="window.gameIntegration && window.gameIntegration.getMissions()" class="px-8 py-4 btn-primary rounded-2xl font-semibold text-lg">
                    ${this.language === 'kz' ? 'Миссияны бастау' : 'Начать миссию'}
                </button>
            </div>
        `;
    }
    
    // Инициализация миссии
    startMission(missionData) {
        this.energy = 20;
        this.correctStreak = 0;
        this.currentQuestionIndex = 0;
        this.totalCorrect = 0;
        this.totalWrong = 0;
        this.missionText = missionData.text || '';
        this.missionTopic = missionData.topic || '';
        
        // Генерируем вопросы с вариантами ответов
        this.questions = this.generateQuestionsWithOptions(missionData.questions || []);
        
        this.updateEnergyUI();
        this.renderMissionText();
    }
    
    // Генерация вариантов ответов для вопросов на основе контекста и уровня сложности
    generateQuestionsWithOptions(rawQuestions) {
        const levelSettings = this.getCurrentLevelSettings();
        const questionsCount = levelSettings.questionsCount;
        const optionsCount = levelSettings.optionsCount;
        
        // Ограничиваем количество вопросов по уровню
        const limitedQuestions = rawQuestions.slice(0, questionsCount);
        
        return limitedQuestions.map((q, idx) => {
            const questionText = typeof q === 'string' ? q : q.text;
            const { correctAnswer, wrongAnswers } = this.getContextualAnswers(questionText);
            const options = this.buildOptions(correctAnswer, wrongAnswers, optionsCount);
            
            return {
                id: `q_${idx}`,
                text: questionText,
                options: options,
                correctIndex: options.findIndex(o => o.isCorrect),
                answered: false,
                wasCorrect: null,
                hint: levelSettings.showHints ? this.generateHint(questionText, correctAnswer) : null
            };
        });
    }
    
    // Генерация подсказки для младших уровней
    generateHint(questionText, correctAnswer) {
        if (!correctAnswer) return null;
        
        // Показываем первую букву или часть ответа
        const firstPart = correctAnswer.substring(0, Math.ceil(correctAnswer.length / 3));
        return `${firstPart}...`;
    }
    
    // Получение контекстных ответов на основе вопроса и текста миссии
    getContextualAnswers(questionText) {
        const q = questionText.toLowerCase();
        const text = this.missionText.toLowerCase();
        
        // База знаний с правильными и неправильными ответами
        const knowledgeBase = {
            // Абылай хан
            'абылай хан қай жылдары': {
                correct: '1711-1781 жылдары',
                wrong: ['1680-1718 жылдары', '1465-1480 жылдары', '1730-1797 жылдары']
            },
            'абылай хан қандай лауазым': {
                correct: 'Хан, дипломат және қолбасшы',
                wrong: ['Би және ақын', 'Батыр және аңшы', 'Сауда керуенбасы']
            },
            'қандай шапқыншылыққа': {
                correct: 'Жоңғар шапқыншылығына',
                wrong: ['Моңғол шапқыншылығына', 'Орыс шапқыншылығына', 'Қытай шапқыншылығына']
            },
            'қай жылы ресми түрде хан': {
                correct: '1771 жылы',
                wrong: ['1756 жылы', '1780 жылы', '1765 жылы']
            },
            'саясаты неге бағытталды': {
                correct: 'Қазақстанның тәуелсіздігін сақтауға',
                wrong: ['Сауданы дамытуға', 'Жер аумағын кеңейтуге', 'Діни реформаларға']
            },
            
            // Қазақ хандығы
            'қазақ хандығы қай жылы құрылды': {
                correct: '1465 жылы',
                wrong: ['1480 жылы', '1500 жылы', '1420 жылы']
            },
            'хандығын кімдер құрды': {
                correct: 'Керей мен Жәнібек хандар',
                wrong: ['Абылай мен Тәуке хандар', 'Қасым мен Хақназар хандар', 'Есім мен Жәңгір хандар']
            },
            'неше жүзге бөлінді': {
                correct: 'Үш жүзге',
                wrong: ['Екі жүзге', 'Төрт жүзге', 'Бес жүзге']
            },
            'үш жүздің атаулары': {
                correct: 'Ұлы жүз, Орта жүз, Кіші жүз',
                wrong: ['Батыс, Шығыс, Оңтүстік жүз', 'Алтын, Күміс, Қола жүз', 'Бірінші, Екінші, Үшінші жүз']
            },
            'қандай өмір салтын': {
                correct: 'Көшпелі өмір салтын',
                wrong: ['Отырықшы өмір салтын', 'Балықшы өмір салтын', 'Қала өмір салтын']
            },
            
            // Тәуке хан
            'тәуке хан қай жылдары': {
                correct: '1680-1718 жылдары',
                wrong: ['1711-1781 жылдары', '1465-1480 жылдары', '1730-1797 жылдары']
            },
            'қандай заңдар жинағын': {
                correct: '«Жеті Жарғы» заңдар жинағын',
                wrong: ['«Қасым ханның қасқа жолы»', '«Есім ханның ескі жолы»', '«Ата заңы»']
            },
            'жеті жарғы нені реттеді': {
                correct: 'Қазақ қоғамының өмірін',
                wrong: ['Тек сауда қатынастарын', 'Тек әскери істерді', 'Тек діни мәселелерді']
            },
            'тәуке хан неге тырысты': {
                correct: 'Үш жүзді біріктіруге',
                wrong: ['Жаңа жерлер жаулап алуға', 'Сауданы дамытуға', 'Қалалар салуға']
            },
            'тәуке ханды қалай атады': {
                correct: '«Заңгер хан» деп',
                wrong: ['«Батыр хан» деп', '«Данышпан хан» деп', '«Жеңімпаз хан» деп']
            },
            
            // Қазақстан тәуелсіздігі
            'тәуелсіздік қай жылы': {
                correct: '1991 жылы 16 желтоқсанда',
                wrong: ['1990 жылы 25 қазанда', '1992 жылы 1 қаңтарда', '1989 жылы 10 желтоқсанда']
            },
            'тұңғыш президент': {
                correct: 'Нұрсұлтан Назарбаев',
                wrong: ['Қасым-Жомарт Тоқаев', 'Дінмұхамед Қонаев', 'Абылай хан']
            },
            'астана қаласы': {
                correct: 'Астана (бұрынғы Ақмола)',
                wrong: ['Алматы', 'Шымкент', 'Қарағанды']
            },
            
            // Жалпы сұрақтар
            'қай ғасырда': {
                correct: text.includes('xv') || text.includes('15') ? 'XV ғасырда' : 
                         text.includes('xviii') || text.includes('18') ? 'XVIII ғасырда' : 'XVII ғасырда',
                wrong: ['XIV ғасырда', 'XIX ғасырда', 'XVI ғасырда']
            }
        };
        
        // Іздеу
        for (const [key, value] of Object.entries(knowledgeBase)) {
            if (q.includes(key) || key.split(' ').every(word => q.includes(word))) {
                return { correctAnswer: value.correct, wrongAnswers: value.wrong };
            }
        }
        
        // Мәтіннен жауап табу
        return this.extractAnswerFromText(questionText);
    }
    
    // Мәтіннен жауап алу
    extractAnswerFromText(questionText) {
        const text = this.missionText;
        const q = questionText.toLowerCase();
        
        // Жылдар
        if (q.includes('жыл') || q.includes('қашан')) {
            const years = text.match(/\d{4}/g);
            if (years && years.length > 0) {
                const correct = years[0] + ' жылы';
                const wrongYears = ['1465', '1718', '1771', '1991', '1680'].filter(y => !years.includes(y));
                return {
                    correctAnswer: correct,
                    wrongAnswers: wrongYears.slice(0, 3).map(y => y + ' жылы')
                };
            }
        }
        
        // Адамдар
        if (q.includes('кім') || q.includes('кімдер')) {
            const people = ['Абылай хан', 'Тәуке хан', 'Керей хан', 'Жәнібек хан', 'Қабанбай батыр'];
            const found = people.find(p => text.toLowerCase().includes(p.toLowerCase()));
            if (found) {
                return {
                    correctAnswer: found,
                    wrongAnswers: people.filter(p => p !== found).slice(0, 3)
                };
            }
        }
        
        // Әдепкі жауап
        return {
            correctAnswer: 'Иә, дұрыс',
            wrongAnswers: ['Жоқ, бұрыс', 'Белгісіз', 'Басқа жауап']
        };
    }
    
    // Нұсқаларды құру
    buildOptions(correctAnswer, wrongAnswers, count) {
        const options = [{ text: correctAnswer, isCorrect: true }];
        
        const shuffledWrong = wrongAnswers.sort(() => Math.random() - 0.5);
        for (let i = 0; i < count - 1 && i < shuffledWrong.length; i++) {
            options.push({ text: shuffledWrong[i], isCorrect: false });
        }
        
        return options.sort(() => Math.random() - 0.5);
    }
    
    // Ответ на вопрос
    answerQuestion(questionIndex, selectedOptionIndex) {
        if (questionIndex !== this.currentQuestionIndex) return null;
        if (this.energy <= 0) return { gameOver: true, reason: 'no_energy' };
        
        const question = this.questions[questionIndex];
        if (!question || question.answered) return null;
        
        // Тратим энергию за вопрос
        this.energy -= 1;
        
        const isCorrect = selectedOptionIndex === question.correctIndex;
        question.answered = true;
        question.wasCorrect = isCorrect;
        
        if (isCorrect) {
            this.totalCorrect++;
            this.correctStreak++;
            
            // Бонус за 3 правильных подряд
            if (this.correctStreak >= 3 && this.correctStreak % 3 === 0) {
                this.energy = Math.min(this.maxEnergy, this.energy + 3);
                this.showStreakBonus();
            }
        } else {
            this.totalWrong++;
            this.correctStreak = 0;
            // Дополнительная потеря энергии за неправильный ответ
            this.energy -= 1;
        }
        
        this.updateEnergyUI();
        
        // Проверяем конец игры
        if (this.energy <= 0) {
            return { 
                gameOver: true, 
                reason: 'no_energy',
                correct: this.totalCorrect,
                wrong: this.totalWrong
            };
        }
        
        // Переходим к следующему вопросу
        this.currentQuestionIndex++;
        
        if (this.currentQuestionIndex >= this.questions.length) {
            return {
                missionComplete: true,
                correct: this.totalCorrect,
                wrong: this.totalWrong,
                energyLeft: this.energy
            };
        }
        
        return {
            isCorrect,
            nextQuestion: this.currentQuestionIndex,
            streak: this.correctStreak,
            energy: this.energy
        };
    }
    
    // Показать бонус за серию
    showStreakBonus() {
        const bonus = document.createElement('div');
        bonus.className = 'fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-gold-500 text-black px-8 py-4 rounded-2xl font-bold text-xl animate-bounce';
        bonus.innerHTML = `🔥 +3 ${this.language === 'kz' ? 'энергия!' : 'энергии!'}`;
        document.body.appendChild(bonus);
        
        setTimeout(() => bonus.remove(), 2000);
    }
    
    // Обновление UI энергии
    updateEnergyUI() {
        const energyBar = document.getElementById('energy-bar');
        const energyText = document.getElementById('energy-text');
        const energyContainer = document.getElementById('energy-container');
        
        if (energyBar) {
            const percent = (this.energy / this.maxEnergy) * 100;
            energyBar.style.width = `${percent}%`;
            
            // Цвет в зависимости от уровня
            if (percent > 50) {
                energyBar.className = 'h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-300';
            } else if (percent > 25) {
                energyBar.className = 'h-full bg-gradient-to-r from-yellow-500 to-yellow-400 rounded-full transition-all duration-300';
            } else {
                energyBar.className = 'h-full bg-gradient-to-r from-red-500 to-red-400 rounded-full transition-all duration-300 animate-pulse';
            }
        }
        
        if (energyText) {
            energyText.textContent = `${this.energy}/${this.maxEnergy}`;
        }
    }
    
    // Рендер текста миссии с кнопкой озвучки
    renderMissionText() {
        const container = document.getElementById('mission-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="relative">
                <!-- Заголовок -->
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-2xl font-bold text-white">${this.missionTopic}</h3>
                    <button id="speak-btn" onclick="gameEngine.speakText()" class="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-xl transition-colors">
                        <iconify-icon id="speak-icon" icon="lucide:volume-2" class="text-gold-400" width="20"></iconify-icon>
                        <span class="text-sm text-zinc-300">${this.language === 'kz' ? 'Тыңдау' : 'Слушать'}</span>
                    </button>
                </div>
                
                <!-- Текст миссии -->
                <div class="bg-zinc-900/50 rounded-2xl p-6 border border-white/10 mb-6">
                    <p id="mission-text-content" class="text-zinc-300 text-lg leading-relaxed">${this.missionText}</p>
                </div>
                
                <!-- Кнопка начать вопросы -->
                <button id="start-questions-btn" onclick="gameEngine.showCurrentQuestion()" class="w-full py-4 btn-primary rounded-xl text-base font-semibold flex items-center justify-center gap-2">
                    <iconify-icon icon="lucide:play" width="20"></iconify-icon>
                    ${this.language === 'kz' ? 'Сұрақтарға өту' : 'Перейти к вопросам'}
                </button>
            </div>
        `;
    }
    
    // Озвучка текста
    speakText() {
        if (!this.synthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }
        
        const speakBtn = document.getElementById('speak-btn');
        const speakIcon = document.getElementById('speak-icon');
        
        if (this.isSpeaking) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            if (speakIcon) speakIcon.setAttribute('icon', 'lucide:volume-2');
            if (speakBtn) speakBtn.classList.remove('bg-gold-500');
            return;
        }
        
        const utterance = new SpeechSynthesisUtterance(this.missionText);
        utterance.lang = this.language === 'kz' ? 'kk-KZ' : 'ru-RU';
        utterance.rate = 0.9;
        
        utterance.onstart = () => {
            this.isSpeaking = true;
            if (speakIcon) speakIcon.setAttribute('icon', 'lucide:volume-x');
            if (speakBtn) speakBtn.classList.add('bg-gold-500', 'text-black');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            if (speakIcon) speakIcon.setAttribute('icon', 'lucide:volume-2');
            if (speakBtn) speakBtn.classList.remove('bg-gold-500', 'text-black');
        };
        
        this.synthesis.speak(utterance);
    }
    
    // Показать текущий вопрос
    showCurrentQuestion() {
        const container = document.getElementById('mission-content');
        if (!container) return;
        
        if (this.currentQuestionIndex >= this.questions.length) {
            this.showMissionComplete();
            return;
        }
        
        const question = this.questions[this.currentQuestionIndex];
        const levelSettings = this.getCurrentLevelSettings();
        
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Заголовок вопроса -->
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-500 to-gold-600 flex items-center justify-center text-black font-bold text-xl">
                            ${this.currentQuestionIndex + 1}
                        </div>
                        <div>
                            <span class="text-zinc-400 text-sm">${this.language === 'kz' ? 'Сұрақ' : 'Вопрос'}</span>
                            <span class="text-white font-medium"> ${this.currentQuestionIndex + 1} / ${this.questions.length}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-3">
                        <!-- Уровень -->
                        <div class="px-3 py-1.5 bg-zinc-800 rounded-lg text-sm">
                            <span class="text-zinc-400">${levelSettings.icon}</span>
                            <span class="text-white ml-1">${this.language === 'kz' ? levelSettings.name_kz : levelSettings.name_ru}</span>
                        </div>
                        ${this.correctStreak >= 2 ? `
                            <div class="flex items-center gap-2 px-4 py-2 bg-orange-500/20 rounded-xl">
                                <span class="text-orange-400 font-bold">🔥 ${this.correctStreak}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Вопрос -->
                <div class="bg-zinc-900/50 rounded-2xl p-6 border border-white/10">
                    <div class="flex items-start gap-3 mb-4">
                        <p class="text-white text-xl flex-1 leading-relaxed">${question.text}</p>
                        <button onclick="gameEngine.speakQuestion()" class="p-3 rounded-xl bg-zinc-800 hover:bg-zinc-700 transition-colors flex-shrink-0">
                            <iconify-icon icon="lucide:volume-2" class="text-gold-400" width="22"></iconify-icon>
                        </button>
                    </div>
                    
                    ${question.hint ? `
                        <div class="mb-4 px-4 py-2 bg-gold-500/10 rounded-xl border border-gold-500/20">
                            <span class="text-gold-400 text-sm">💡 ${this.language === 'kz' ? 'Көмек' : 'Подсказка'}: ${question.hint}</span>
                        </div>
                    ` : ''}
                    
                    <!-- Варианты ответов -->
                    <div class="space-y-3" id="options-container">
                        ${question.options.map((opt, idx) => `
                            <button onclick="gameEngine.selectAnswer(${idx})" 
                                class="option-btn w-full p-5 text-left rounded-2xl border-2 border-white/10 bg-zinc-800/50 hover:bg-zinc-700/50 hover:border-gold-500/50 transition-all flex items-center gap-4 group"
                                data-index="${idx}">
                                <span class="w-10 h-10 rounded-xl bg-zinc-700 group-hover:bg-gold-500 flex items-center justify-center text-base font-bold text-zinc-400 group-hover:text-black transition-all">
                                    ${String.fromCharCode(65 + idx)}
                                </span>
                                <span class="text-white text-lg">${opt.text}</span>
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Озвучка вопроса
    speakQuestion() {
        if (!this.synthesis) return;
        
        const question = this.questions[this.currentQuestionIndex];
        if (!question) return;
        
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(question.text);
        utterance.lang = this.language === 'kz' ? 'kk-KZ' : 'ru-RU';
        utterance.rate = 0.9;
        
        this.synthesis.speak(utterance);
    }
    
    // Выбор ответа
    selectAnswer(optionIndex) {
        const result = this.answerQuestion(this.currentQuestionIndex - 1 + 1, optionIndex);
        if (!result) return;
        
        // Звуковые эффекты
        if (typeof soundEffects !== 'undefined') {
            if (result.isCorrect) {
                soundEffects.correct();
                if (this.correctStreak >= 3) soundEffects.streak();
            } else {
                soundEffects.wrong();
            }
        }
        
        // Обновляем статистику
        if (typeof userStats !== 'undefined') {
            userStats.updateStreak(this.correctStreak);
        }
        
        const question = this.questions[this.currentQuestionIndex - 1];
        const buttons = document.querySelectorAll('.option-btn');
        
        // Показываем правильный/неправильный ответ
        buttons.forEach((btn, idx) => {
            btn.disabled = true;
            btn.classList.remove('hover:bg-zinc-700/50', 'hover:border-gold-500/50');
            
            if (idx === question.correctIndex) {
                btn.classList.add('bg-green-500/20', 'border-green-500');
                btn.querySelector('span:first-child').classList.add('bg-green-500', 'text-white');
            } else if (idx === optionIndex && !result.isCorrect) {
                btn.classList.add('bg-red-500/20', 'border-red-500');
                btn.querySelector('span:first-child').classList.add('bg-red-500', 'text-white');
            }
        });
        
        // Показываем результат
        const feedback = document.createElement('div');
        feedback.className = `mt-4 p-4 rounded-xl ${result.isCorrect ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'} flex items-center gap-3`;
        feedback.innerHTML = `
            <iconify-icon icon="${result.isCorrect ? 'lucide:check-circle' : 'lucide:x-circle'}" width="24"></iconify-icon>
            <span class="font-medium">${result.isCorrect 
                ? (this.language === 'kz' ? 'Дұрыс!' : 'Правильно!') 
                : (this.language === 'kz' ? 'Қате!' : 'Неправильно!')}</span>
            ${!result.isCorrect ? `<span class="text-sm opacity-70">-2 ${this.language === 'kz' ? 'энергия' : 'энергии'}</span>` : ''}
        `;
        
        document.getElementById('options-container').appendChild(feedback);
        
        // Переход к следующему вопросу или завершение
        setTimeout(() => {
            if (result.gameOver) {
                this.showGameOver();
            } else if (result.missionComplete) {
                this.showMissionComplete();
            } else {
                this.showCurrentQuestion();
            }
        }, 1500);
    }
    
    // Конец игры (нет энергии)
    showGameOver() {
        const container = document.getElementById('mission-content');
        if (!container) return;
        
        const accuracy = this.questions.length > 0 ? Math.round((this.totalCorrect / (this.totalCorrect + this.totalWrong)) * 100) : 0;
        
        container.innerHTML = `
            <div class="text-center py-8">
                <!-- Иконка -->
                <div class="w-24 h-24 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-red-500/20 to-orange-500/20 flex items-center justify-center">
                    <iconify-icon icon="lucide:battery-low" class="text-red-400" width="48"></iconify-icon>
                </div>
                
                <h3 class="text-3xl font-bold text-white mb-2">${this.language === 'kz' ? 'Энергия бітті!' : 'Энергия закончилась!'}</h3>
                <p class="text-zinc-400 mb-8">${this.language === 'kz' ? 'Келесі жолы сәттілік тілейміз!' : 'Удачи в следующий раз!'}</p>
                
                <!-- Статистика -->
                <div class="grid grid-cols-3 gap-4 max-w-md mx-auto mb-8">
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-12 h-12 mx-auto mb-2 rounded-xl bg-green-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:check" class="text-green-400" width="24"></iconify-icon>
                        </div>
                        <div class="text-2xl font-bold text-green-400">${this.totalCorrect}</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Дұрыс' : 'Верно'}</div>
                    </div>
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-12 h-12 mx-auto mb-2 rounded-xl bg-red-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:x" class="text-red-400" width="24"></iconify-icon>
                        </div>
                        <div class="text-2xl font-bold text-red-400">${this.totalWrong}</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Қате' : 'Ошибок'}</div>
                    </div>
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-12 h-12 mx-auto mb-2 rounded-xl bg-gold-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:percent" class="text-gold-400" width="24"></iconify-icon>
                        </div>
                        <div class="text-2xl font-bold text-gold-400">${accuracy}%</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Дәлдік' : 'Точность'}</div>
                    </div>
                </div>
                
                <button onclick="gameEngine.restartMission()" class="px-8 py-4 btn-primary rounded-2xl font-semibold text-lg flex items-center gap-3 mx-auto">
                    <iconify-icon icon="lucide:refresh-cw" width="20"></iconify-icon>
                    ${this.language === 'kz' ? 'Қайта бастау' : 'Начать заново'}
                </button>
            </div>
        `;
    }
    
    // Миссия завершена
    showMissionComplete() {
        const container = document.getElementById('mission-content');
        if (!container) return;
        
        const stars = this.totalCorrect >= this.questions.length ? 3 
            : this.totalCorrect >= this.questions.length * 0.7 ? 2 
            : this.totalCorrect >= this.questions.length * 0.5 ? 1 : 0;
        
        const accuracy = this.questions.length > 0 ? Math.round((this.totalCorrect / this.questions.length) * 100) : 0;
        const xpEarned = this.totalCorrect * 10 + (stars * 15);
        
        // Звук победы
        if (typeof soundEffects !== 'undefined') {
            soundEffects.victory();
        }
        
        // Записываем статистику
        if (typeof userStats !== 'undefined') {
            userStats.recordMission(this.missionTopic, this.totalCorrect, this.totalWrong, xpEarned);
        }
        
        // Обновляем лидерборд
        if (typeof leaderboard !== 'undefined') {
            const savedUser = localStorage.getItem('batyrbol_user');
            if (savedUser) {
                const user = JSON.parse(savedUser);
                const totalXP = (userStats?.stats?.totalXP || 0);
                leaderboard.updatePlayer(user.name || 'Батыр', totalXP, Math.floor(totalXP / 100) + 1);
            }
        }
        
        // Обновляем достижения
        if (typeof onMissionComplete === 'function') {
            onMissionComplete(this.missionTopic, this.totalCorrect, this.questions.length);
        }
        
        container.innerHTML = `
            <div class="text-center py-8">
                <!-- Звёзды с анимацией -->
                <div class="flex justify-center gap-4 mb-6">
                    ${[1, 2, 3].map(i => `
                        <div class="relative ${i <= stars ? 'animate-bounce' : ''}" style="animation-delay: ${i * 0.1}s">
                            <div class="w-16 h-16 rounded-2xl ${i <= stars ? 'bg-gradient-to-br from-gold-400 to-gold-600' : 'bg-zinc-800'} flex items-center justify-center">
                                <iconify-icon icon="lucide:star" width="32" class="${i <= stars ? 'text-white' : 'text-zinc-600'}"></iconify-icon>
                            </div>
                            ${i <= stars ? '<div class="absolute inset-0 rounded-2xl bg-gold-400/30 animate-ping"></div>' : ''}
                        </div>
                    `).join('')}
                </div>
                
                <h3 class="text-3xl font-bold text-white mb-2">${this.language === 'kz' ? 'Тамаша!' : 'Отлично!'}</h3>
                <p class="text-zinc-400 mb-2">${this.missionTopic}</p>
                
                <!-- XP заработанный -->
                <div class="inline-flex items-center gap-2 px-6 py-3 bg-gold-500/20 rounded-2xl mb-8">
                    <iconify-icon icon="lucide:zap" class="text-gold-400" width="24"></iconify-icon>
                    <span class="text-gold-400 font-bold text-xl">+${xpEarned} XP</span>
                </div>
                
                <!-- Статистика -->
                <div class="grid grid-cols-4 gap-3 max-w-lg mx-auto mb-8">
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-10 h-10 mx-auto mb-2 rounded-xl bg-green-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:check" class="text-green-400" width="20"></iconify-icon>
                        </div>
                        <div class="text-xl font-bold text-green-400">${this.totalCorrect}</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Дұрыс' : 'Верно'}</div>
                    </div>
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-10 h-10 mx-auto mb-2 rounded-xl bg-red-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:x" class="text-red-400" width="20"></iconify-icon>
                        </div>
                        <div class="text-xl font-bold text-red-400">${this.totalWrong}</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Қате' : 'Ошибок'}</div>
                    </div>
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-10 h-10 mx-auto mb-2 rounded-xl bg-gold-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:percent" class="text-gold-400" width="20"></iconify-icon>
                        </div>
                        <div class="text-xl font-bold text-gold-400">${accuracy}%</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Дәлдік' : 'Точность'}</div>
                    </div>
                    <div class="bg-zinc-900/50 rounded-2xl p-4 border border-white/10">
                        <div class="w-10 h-10 mx-auto mb-2 rounded-xl bg-blue-500/20 flex items-center justify-center">
                            <iconify-icon icon="lucide:battery-charging" class="text-blue-400" width="20"></iconify-icon>
                        </div>
                        <div class="text-xl font-bold text-blue-400">${this.energy}</div>
                        <div class="text-xs text-zinc-500">${this.language === 'kz' ? 'Энергия' : 'Энергия'}</div>
                    </div>
                </div>
                
                <button onclick="window.gameIntegration && window.gameIntegration.getMissions()" class="px-8 py-4 btn-primary rounded-2xl font-semibold text-lg flex items-center gap-3 mx-auto">
                    <iconify-icon icon="lucide:arrow-right" width="20"></iconify-icon>
                    ${this.language === 'kz' ? 'Келесі миссия' : 'Следующая миссия'}
                </button>
            </div>
        `;
    }
    
    // Перезапуск миссии
    restartMission() {
        this.energy = 20;
        this.correctStreak = 0;
        this.currentQuestionIndex = 0;
        this.totalCorrect = 0;
        this.totalWrong = 0;
        
        // Сбрасываем ответы
        this.questions.forEach(q => {
            q.answered = false;
            q.wasCorrect = null;
        });
        
        this.updateEnergyUI();
        this.renderMissionText();
    }
    
    setLanguage(lang) {
        this.language = lang;
    }
}

// Глобальный экземпляр
let gameEngine = new GameEngine();
