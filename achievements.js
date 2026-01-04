/**
 * BATYR BOL - Achievements & Rating System
 * Система достижений и рейтинга
 */

class AchievementsSystem {
    constructor() {
        this.achievements = this.getDefaultAchievements();
        this.userAchievements = this.loadUserAchievements();
        this.userStats = this.loadUserStats();
    }
    
    getDefaultAchievements() {
        return [
            // Миссии
            { id: 'first_mission', name_ru: 'Первые шаги', name_kz: 'Алғашқы қадамдар', desc_ru: 'Завершите первую миссию', desc_kz: 'Бірінші миссияны аяқтаңыз', icon: '🎯', points: 10, condition: { type: 'missions_completed', value: 1 } },
            { id: 'mission_5', name_ru: 'Начинающий батыр', name_kz: 'Жас батыр', desc_ru: 'Завершите 5 миссий', desc_kz: '5 миссияны аяқтаңыз', icon: '⚔️', points: 25, condition: { type: 'missions_completed', value: 5 } },
            { id: 'mission_10', name_ru: 'Опытный воин', name_kz: 'Тәжірибелі жауынгер', desc_ru: 'Завершите 10 миссий', desc_kz: '10 миссияны аяқтаңыз', icon: '🛡️', points: 50, condition: { type: 'missions_completed', value: 10 } },
            { id: 'mission_25', name_ru: 'Мастер истории', name_kz: 'Тарих шебері', desc_ru: 'Завершите 25 миссий', desc_kz: '25 миссияны аяқтаңыз', icon: '📚', points: 100, condition: { type: 'missions_completed', value: 25 } },
            { id: 'mission_50', name_ru: 'Легенда степи', name_kz: 'Дала аңызы', desc_ru: 'Завершите 50 миссий', desc_kz: '50 миссияны аяқтаңыз', icon: '👑', points: 250, condition: { type: 'missions_completed', value: 50 } },
            
            // Правильные ответы
            { id: 'correct_10', name_ru: 'Умник', name_kz: 'Ақылды', desc_ru: '10 правильных ответов', desc_kz: '10 дұрыс жауап', icon: '💡', points: 15, condition: { type: 'correct_answers', value: 10 } },
            { id: 'correct_50', name_ru: 'Эрудит', name_kz: 'Эрудит', desc_ru: '50 правильных ответов', desc_kz: '50 дұрыс жауап', icon: '🧠', points: 75, condition: { type: 'correct_answers', value: 50 } },
            { id: 'correct_100', name_ru: 'Гений', name_kz: 'Дана', desc_ru: '100 правильных ответов', desc_kz: '100 дұрыс жауап', icon: '🌟', points: 150, condition: { type: 'correct_answers', value: 100 } },
            
            // Серии
            { id: 'streak_3', name_ru: 'Хорошее начало', name_kz: 'Жақсы бастама', desc_ru: '3 правильных ответа подряд', desc_kz: '3 дұрыс жауап қатарынан', icon: '🔥', points: 20, condition: { type: 'streak', value: 3 } },
            { id: 'streak_5', name_ru: 'В ударе', name_kz: 'Серпінде', desc_ru: '5 правильных ответов подряд', desc_kz: '5 дұрыс жауап қатарынан', icon: '⚡', points: 40, condition: { type: 'streak', value: 5 } },
            { id: 'streak_10', name_ru: 'Непобедимый', name_kz: 'Жеңілмес', desc_ru: '10 правильных ответов подряд', desc_kz: '10 дұрыс жауап қатарынан', icon: '💎', points: 100, condition: { type: 'streak', value: 10 } },
            
            // Темы
            { id: 'topic_ablai', name_ru: 'Знаток Абылай хана', name_kz: 'Абылай хан білгірі', desc_ru: 'Изучите все миссии об Абылай хане', desc_kz: 'Абылай хан туралы барлық миссияларды оқыңыз', icon: '🏇', points: 50, condition: { type: 'topic_completed', value: 'Абылай хан' } },
            { id: 'topic_khanate', name_ru: 'Историк ханства', name_kz: 'Хандық тарихшысы', desc_ru: 'Изучите все миссии о Казахском ханстве', desc_kz: 'Қазақ хандығы туралы барлық миссияларды оқыңыз', icon: '🏰', points: 50, condition: { type: 'topic_completed', value: 'Қазақ хандығы' } },
            
            // Голосовые
            { id: 'voice_first', name_ru: 'Голос батыра', name_kz: 'Батыр дауысы', desc_ru: 'Первый голосовой ответ', desc_kz: 'Бірінші дауыспен жауап', icon: '🎤', points: 15, condition: { type: 'voice_answers', value: 1 } },
            { id: 'voice_10', name_ru: 'Оратор', name_kz: 'Шешен', desc_ru: '10 голосовых ответов', desc_kz: '10 дауыспен жауап', icon: '🗣️', points: 50, condition: { type: 'voice_answers', value: 10 } },
            
            // Время
            { id: 'daily_login', name_ru: 'Ежедневный визит', name_kz: 'Күнделікті кіру', desc_ru: 'Заходите 7 дней подряд', desc_kz: '7 күн қатарынан кіріңіз', icon: '📅', points: 30, condition: { type: 'daily_streak', value: 7 } },
            { id: 'speed_demon', name_ru: 'Молниеносный', name_kz: 'Найзағай', desc_ru: 'Ответьте за 5 секунд', desc_kz: '5 секундта жауап беріңіз', icon: '⏱️', points: 25, condition: { type: 'fast_answer', value: 5 } },
            
            // Особые
            { id: 'perfect_mission', name_ru: 'Идеальная миссия', name_kz: 'Мінсіз миссия', desc_ru: 'Завершите миссию без ошибок', desc_kz: 'Миссияны қатесіз аяқтаңыз', icon: '✨', points: 35, condition: { type: 'perfect_mission', value: 1 } },
            { id: 'polyglot', name_ru: 'Полиглот', name_kz: 'Полиглот', desc_ru: 'Играйте на обоих языках', desc_kz: 'Екі тілде ойнаңыз', icon: '🌍', points: 40, condition: { type: 'both_languages', value: true } }
        ];
    }
    
    loadUserAchievements() {
        try {
            const saved = localStorage.getItem('batyrbol_achievements');
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            return [];
        }
    }
    
    saveUserAchievements() {
        localStorage.setItem('batyrbol_achievements', JSON.stringify(this.userAchievements));
    }
    
    loadUserStats() {
        try {
            const saved = localStorage.getItem('batyrbol_stats');
            return saved ? JSON.parse(saved) : this.getDefaultStats();
        } catch (e) {
            return this.getDefaultStats();
        }
    }
    
    getDefaultStats() {
        return {
            missions_completed: 0,
            correct_answers: 0,
            wrong_answers: 0,
            current_streak: 0,
            best_streak: 0,
            voice_answers: 0,
            total_points: 0,
            level: 1,
            topics_completed: {},
            daily_logins: 0,
            last_login: null,
            languages_used: [],
            perfect_missions: 0,
            fastest_answer: null
        };
    }
    
    saveUserStats() {
        localStorage.setItem('batyrbol_stats', JSON.stringify(this.userStats));
    }
    
    updateStats(statName, value = 1) {
        if (statName in this.userStats) {
            if (typeof this.userStats[statName] === 'number') {
                this.userStats[statName] += value;
            } else {
                this.userStats[statName] = value;
            }
        }
        
        this.saveUserStats();
        this.checkAchievements();
        this.updateLevel();
    }
    
    recordCorrectAnswer() {
        this.userStats.correct_answers++;
        this.userStats.current_streak++;
        
        if (this.userStats.current_streak > this.userStats.best_streak) {
            this.userStats.best_streak = this.userStats.current_streak;
        }
        
        this.saveUserStats();
        this.checkAchievements();
    }
    
    recordWrongAnswer() {
        this.userStats.wrong_answers++;
        this.userStats.current_streak = 0;
        this.saveUserStats();
    }
    
    recordMissionComplete(topic, isPerfect = false) {
        this.userStats.missions_completed++;
        
        if (!this.userStats.topics_completed[topic]) {
            this.userStats.topics_completed[topic] = 0;
        }
        this.userStats.topics_completed[topic]++;
        
        if (isPerfect) {
            this.userStats.perfect_missions++;
        }
        
        this.saveUserStats();
        this.checkAchievements();
        this.updateLevel();
    }
    
    recordVoiceAnswer() {
        this.userStats.voice_answers++;
        this.saveUserStats();
        this.checkAchievements();
    }
    
    recordLanguageUsed(lang) {
        if (!this.userStats.languages_used.includes(lang)) {
            this.userStats.languages_used.push(lang);
            this.saveUserStats();
            this.checkAchievements();
        }
    }
    
    checkAchievements() {
        const newAchievements = [];
        
        for (const achievement of this.achievements) {
            if (this.userAchievements.includes(achievement.id)) continue;
            
            let unlocked = false;
            const cond = achievement.condition;
            
            switch (cond.type) {
                case 'missions_completed':
                    unlocked = this.userStats.missions_completed >= cond.value;
                    break;
                case 'correct_answers':
                    unlocked = this.userStats.correct_answers >= cond.value;
                    break;
                case 'streak':
                    unlocked = this.userStats.best_streak >= cond.value;
                    break;
                case 'voice_answers':
                    unlocked = this.userStats.voice_answers >= cond.value;
                    break;
                case 'perfect_mission':
                    unlocked = this.userStats.perfect_missions >= cond.value;
                    break;
                case 'both_languages':
                    unlocked = this.userStats.languages_used.length >= 2;
                    break;
                case 'topic_completed':
                    unlocked = (this.userStats.topics_completed[cond.value] || 0) >= 3;
                    break;
            }
            
            if (unlocked) {
                this.userAchievements.push(achievement.id);
                this.userStats.total_points += achievement.points;
                newAchievements.push(achievement);
            }
        }
        
        this.saveUserAchievements();
        this.saveUserStats();
        
        // Show notifications for new achievements
        newAchievements.forEach(a => this.showAchievementNotification(a));
        
        return newAchievements;
    }
    
    updateLevel() {
        const points = this.userStats.total_points;
        const levels = [0, 50, 150, 300, 500, 800, 1200, 1700, 2300, 3000];
        
        let newLevel = 1;
        for (let i = levels.length - 1; i >= 0; i--) {
            if (points >= levels[i]) {
                newLevel = i + 1;
                break;
            }
        }
        
        if (newLevel > this.userStats.level) {
            this.userStats.level = newLevel;
            this.showLevelUpNotification(newLevel);
        }
        
        this.saveUserStats();
    }
    
    showAchievementNotification(achievement) {
        const lang = document.body.dataset.language || 'ru';
        const name = lang === 'kz' ? achievement.name_kz : achievement.name_ru;
        const desc = lang === 'kz' ? achievement.desc_kz : achievement.desc_ru;
        
        const notification = document.createElement('div');
        notification.className = 'fixed top-20 right-4 z-50 bg-gradient-to-r from-gold-600 to-gold-400 text-black p-4 rounded-xl shadow-2xl animate-slide-in max-w-sm';
        notification.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="text-3xl">${achievement.icon}</span>
                <div>
                    <div class="font-bold">${name}</div>
                    <div class="text-sm opacity-80">${desc}</div>
                    <div class="text-xs mt-1">+${achievement.points} очков</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('animate-slide-out');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    showLevelUpNotification(level) {
        const lang = document.body.dataset.language || 'ru';
        const titles = {
            1: { ru: 'Новичок', kz: 'Жаңадан бастаушы' },
            2: { ru: 'Ученик', kz: 'Шәкірт' },
            3: { ru: 'Воин', kz: 'Жауынгер' },
            4: { ru: 'Батыр', kz: 'Батыр' },
            5: { ru: 'Герой', kz: 'Қаһарман' },
            6: { ru: 'Мастер', kz: 'Шебер' },
            7: { ru: 'Легенда', kz: 'Аңыз' },
            8: { ru: 'Хан', kz: 'Хан' },
            9: { ru: 'Великий Хан', kz: 'Ұлы Хан' },
            10: { ru: 'Бессмертный', kz: 'Мәңгілік' }
        };
        
        const title = titles[level] ? titles[level][lang] : `Уровень ${level}`;
        
        const notification = document.createElement('div');
        notification.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/80';
        notification.innerHTML = `
            <div class="text-center animate-scale-in">
                <div class="text-6xl mb-4">🎉</div>
                <div class="text-gold-400 text-2xl font-bold mb-2">${lang === 'kz' ? 'Жаңа деңгей!' : 'Новый уровень!'}</div>
                <div class="text-white text-4xl font-bold">${title}</div>
                <div class="text-zinc-400 mt-2">${lang === 'kz' ? 'Деңгей' : 'Уровень'} ${level}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    getProgress() {
        const total = this.achievements.length;
        const unlocked = this.userAchievements.length;
        return { unlocked, total, percentage: Math.round((unlocked / total) * 100) };
    }
    
    getRank() {
        const level = this.userStats.level;
        const ranks = ['Новичок', 'Ученик', 'Воин', 'Батыр', 'Герой', 'Мастер', 'Легенда', 'Хан', 'Великий Хан', 'Бессмертный'];
        return ranks[Math.min(level - 1, ranks.length - 1)];
    }
}

// UI Component for Achievements Panel
class AchievementsUI {
    constructor(system) {
        this.system = system;
    }
    
    render(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const lang = document.body.dataset.language || 'ru';
        const stats = this.system.userStats;
        const progress = this.system.getProgress();
        
        container.innerHTML = `
            <div class="achievements-panel bg-zinc-900/80 rounded-2xl p-6 border border-white/10">
                <!-- Stats Header -->
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h3 class="text-xl font-bold text-white">${lang === 'kz' ? 'Жетістіктер' : 'Достижения'}</h3>
                        <p class="text-zinc-500 text-sm">${progress.unlocked}/${progress.total} (${progress.percentage}%)</p>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold text-gold-400">${stats.total_points}</div>
                        <div class="text-xs text-zinc-500">${lang === 'kz' ? 'ұпай' : 'очков'}</div>
                    </div>
                </div>
                
                <!-- Level Progress -->
                <div class="mb-6 p-4 bg-zinc-800/50 rounded-xl">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gold-400 font-medium">${lang === 'kz' ? 'Деңгей' : 'Уровень'} ${stats.level}</span>
                        <span class="text-zinc-500 text-sm">${this.system.getRank()}</span>
                    </div>
                    <div class="h-2 bg-zinc-700 rounded-full overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-gold-600 to-gold-400 rounded-full" style="width: ${this.getLevelProgress()}%"></div>
                    </div>
                </div>
                
                <!-- Quick Stats -->
                <div class="grid grid-cols-3 gap-3 mb-6">
                    <div class="text-center p-3 bg-zinc-800/50 rounded-lg">
                        <div class="text-xl font-bold text-white">${stats.missions_completed}</div>
                        <div class="text-xs text-zinc-500">${lang === 'kz' ? 'Миссия' : 'Миссий'}</div>
                    </div>
                    <div class="text-center p-3 bg-zinc-800/50 rounded-lg">
                        <div class="text-xl font-bold text-green-400">${stats.correct_answers}</div>
                        <div class="text-xs text-zinc-500">${lang === 'kz' ? 'Дұрыс' : 'Верных'}</div>
                    </div>
                    <div class="text-center p-3 bg-zinc-800/50 rounded-lg">
                        <div class="text-xl font-bold text-gold-400">${stats.best_streak}</div>
                        <div class="text-xs text-zinc-500">${lang === 'kz' ? 'Серия' : 'Серия'}</div>
                    </div>
                </div>
                
                <!-- Achievements Grid -->
                <div class="grid grid-cols-4 gap-2">
                    ${this.renderAchievementIcons()}
                </div>
            </div>
        `;
    }
    
    getLevelProgress() {
        const points = this.system.userStats.total_points;
        const levels = [0, 50, 150, 300, 500, 800, 1200, 1700, 2300, 3000];
        const currentLevel = this.system.userStats.level;
        
        if (currentLevel >= levels.length) return 100;
        
        const currentLevelPoints = levels[currentLevel - 1];
        const nextLevelPoints = levels[currentLevel];
        const progress = ((points - currentLevelPoints) / (nextLevelPoints - currentLevelPoints)) * 100;
        
        return Math.min(100, Math.max(0, progress));
    }
    
    renderAchievementIcons() {
        return this.system.achievements.map(a => {
            const unlocked = this.system.userAchievements.includes(a.id);
            const lang = document.body.dataset.language || 'ru';
            const name = lang === 'kz' ? a.name_kz : a.name_ru;
            
            return `
                <div class="relative group cursor-pointer">
                    <div class="w-12 h-12 rounded-lg ${unlocked ? 'bg-gold-500/20' : 'bg-zinc-800/50'} flex items-center justify-center text-2xl ${unlocked ? '' : 'grayscale opacity-50'}">
                        ${a.icon}
                    </div>
                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                        ${name}
                    </div>
                </div>
            `;
        }).join('');
    }
}

// CSS for animations
const achievementStyles = document.createElement('style');
achievementStyles.textContent = `
    @keyframes slide-in {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slide-out {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    @keyframes scale-in {
        from { transform: scale(0.5); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    .animate-slide-in { animation: slide-in 0.3s ease-out; }
    .animate-slide-out { animation: slide-out 0.3s ease-out; }
    .animate-scale-in { animation: scale-in 0.5s ease-out; }
`;
document.head.appendChild(achievementStyles);

// Global instance
let achievementsSystem = null;
let achievementsUI = null;

function initAchievements() {
    achievementsSystem = new AchievementsSystem();
    achievementsUI = new AchievementsUI(achievementsSystem);
    return { achievementsSystem, achievementsUI };
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AchievementsSystem, AchievementsUI, initAchievements };
}
