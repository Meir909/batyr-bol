/**
 * BATYR BOL - Additional Features
 * Лидерборд, ежедневные награды, звуковые эффекты, статистика
 */

// ==================== ЗВУКОВЫЕ ЭФФЕКТЫ ====================
class SoundEffects {
    constructor() {
        this.enabled = localStorage.getItem('batyrbol_sounds') !== 'false';
        this.audioContext = null;
        this.sounds = {};
        this.init();
    }
    
    init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Audio not supported');
        }
    }
    
    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('batyrbol_sounds', this.enabled.toString());
        return this.enabled;
    }
    
    // Генерация звука через Web Audio API
    playTone(frequency, duration, type = 'sine', volume = 0.3) {
        if (!this.enabled || !this.audioContext) return;
        
        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = type;
            gainNode.gain.value = volume;
            
            oscillator.start();
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            oscillator.stop(this.audioContext.currentTime + duration);
        } catch (e) {}
    }
    
    // Звук правильного ответа
    correct() {
        this.playTone(523.25, 0.1); // C5
        setTimeout(() => this.playTone(659.25, 0.1), 100); // E5
        setTimeout(() => this.playTone(783.99, 0.2), 200); // G5
    }
    
    // Звук неправильного ответа
    wrong() {
        this.playTone(200, 0.3, 'square', 0.2);
    }
    
    // Звук клика
    click() {
        this.playTone(800, 0.05, 'sine', 0.1);
    }
    
    // Звук победы
    victory() {
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, i) => {
            setTimeout(() => this.playTone(freq, 0.2), i * 150);
        });
    }
    
    // Звук бонуса
    bonus() {
        this.playTone(880, 0.1);
        setTimeout(() => this.playTone(1108.73, 0.15), 100);
    }
    
    // Звук streak
    streak() {
        this.playTone(659.25, 0.1);
        setTimeout(() => this.playTone(783.99, 0.1), 80);
        setTimeout(() => this.playTone(987.77, 0.15), 160);
    }
}

// ==================== ЕЖЕДНЕВНЫЕ НАГРАДЫ ====================
class DailyRewards {
    constructor() {
        this.rewards = [
            { day: 1, xp: 10, energy: 5, icon: '🎁' },
            { day: 2, xp: 20, energy: 5, icon: '🎁' },
            { day: 3, xp: 30, energy: 10, icon: '🎁' },
            { day: 4, xp: 40, energy: 10, icon: '🎁' },
            { day: 5, xp: 50, energy: 15, icon: '🎁' },
            { day: 6, xp: 75, energy: 15, icon: '🎁' },
            { day: 7, xp: 100, energy: 20, icon: '🏆' }
        ];
        this.loadData();
    }
    
    loadData() {
        const saved = localStorage.getItem('batyrbol_daily');
        if (saved) {
            const data = JSON.parse(saved);
            this.lastClaim = data.lastClaim ? new Date(data.lastClaim) : null;
            this.currentStreak = data.currentStreak || 0;
        } else {
            this.lastClaim = null;
            this.currentStreak = 0;
        }
    }
    
    saveData() {
        localStorage.setItem('batyrbol_daily', JSON.stringify({
            lastClaim: this.lastClaim ? this.lastClaim.toISOString() : null,
            currentStreak: this.currentStreak
        }));
    }
    
    canClaim() {
        if (!this.lastClaim) return true;
        
        const now = new Date();
        const lastDate = new Date(this.lastClaim);
        
        // Сбрасываем время для сравнения только дат
        now.setHours(0, 0, 0, 0);
        lastDate.setHours(0, 0, 0, 0);
        
        const diffDays = Math.floor((now - lastDate) / (1000 * 60 * 60 * 24));
        
        return diffDays >= 1;
    }
    
    claim() {
        if (!this.canClaim()) return null;
        
        const now = new Date();
        const lastDate = this.lastClaim ? new Date(this.lastClaim) : null;
        
        if (lastDate) {
            lastDate.setHours(0, 0, 0, 0);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const diffDays = Math.floor((today - lastDate) / (1000 * 60 * 60 * 24));
            
            if (diffDays > 1) {
                // Пропустил день - сброс streak
                this.currentStreak = 1;
            } else {
                this.currentStreak = Math.min(this.currentStreak + 1, 7);
            }
        } else {
            this.currentStreak = 1;
        }
        
        this.lastClaim = now;
        this.saveData();
        
        const reward = this.rewards[this.currentStreak - 1];
        return {
            ...reward,
            streak: this.currentStreak
        };
    }
    
    getCurrentReward() {
        const nextDay = this.canClaim() ? this.currentStreak + 1 : this.currentStreak;
        return this.rewards[Math.min(nextDay, 7) - 1];
    }
    
    showRewardModal() {
        const canClaim = this.canClaim();
        const currentReward = this.getCurrentReward();
        const lang = document.body.dataset.language || 'kz';
        
        let modal = document.getElementById('daily-reward-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'daily-reward-modal';
            modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="glass rounded-2xl max-w-md w-full p-6 text-center">
                <h2 class="text-2xl font-bold text-white mb-4">
                    ${lang === 'kz' ? '🎁 Күнделікті сыйлық' : '🎁 Ежедневная награда'}
                </h2>
                
                <!-- Streak дни -->
                <div class="flex justify-center gap-2 mb-6">
                    ${this.rewards.map((r, i) => `
                        <div class="w-10 h-10 rounded-lg ${i < this.currentStreak ? 'bg-gold-500' : 'bg-zinc-800'} flex items-center justify-center text-sm ${i < this.currentStreak ? 'text-black' : 'text-zinc-500'}">
                            ${i + 1}
                        </div>
                    `).join('')}
                </div>
                
                ${canClaim ? `
                    <div class="bg-gold-500/20 rounded-2xl p-6 mb-6">
                        <div class="text-5xl mb-4">${currentReward.icon}</div>
                        <p class="text-gold-400 font-bold text-xl mb-2">
                            ${lang === 'kz' ? `${this.currentStreak + 1}-күн` : `День ${this.currentStreak + 1}`}
                        </p>
                        <div class="flex justify-center gap-6">
                            <div>
                                <span class="text-2xl font-bold text-white">+${currentReward.xp}</span>
                                <span class="text-zinc-400 text-sm ml-1">XP</span>
                            </div>
                            <div>
                                <span class="text-2xl font-bold text-green-400">+${currentReward.energy}</span>
                                <span class="text-zinc-400 text-sm ml-1">⚡</span>
                            </div>
                        </div>
                    </div>
                    <button onclick="dailyRewards.claimAndClose()" class="w-full py-4 btn-primary rounded-xl font-semibold">
                        ${lang === 'kz' ? 'Алу' : 'Получить'}
                    </button>
                ` : `
                    <div class="bg-zinc-800/50 rounded-2xl p-6 mb-6">
                        <iconify-icon icon="lucide:clock" class="text-zinc-500" width="48"></iconify-icon>
                        <p class="text-zinc-400 mt-4">
                            ${lang === 'kz' ? 'Келесі сыйлық ертең қолжетімді болады' : 'Следующая награда будет доступна завтра'}
                        </p>
                    </div>
                    <button onclick="dailyRewards.closeModal()" class="w-full py-4 bg-zinc-700 hover:bg-zinc-600 rounded-xl font-semibold text-white transition-colors">
                        ${lang === 'kz' ? 'Жабу' : 'Закрыть'}
                    </button>
                `}
            </div>
        `;
        
        modal.classList.remove('hidden');
    }
    
    claimAndClose() {
        const reward = this.claim();
        if (reward && typeof soundEffects !== 'undefined') {
            soundEffects.bonus();
        }
        
        // Показываем анимацию получения
        const modal = document.getElementById('daily-reward-modal');
        if (modal) {
            modal.innerHTML = `
                <div class="glass rounded-2xl max-w-md w-full p-6 text-center">
                    <div class="text-6xl mb-4 animate-bounce">🎉</div>
                    <h2 class="text-2xl font-bold text-white mb-2">
                        ${document.body.dataset.language === 'kz' ? 'Сыйлық алынды!' : 'Награда получена!'}
                    </h2>
                    <p class="text-gold-400 text-xl mb-6">+${reward.xp} XP, +${reward.energy} ⚡</p>
                </div>
            `;
            
            setTimeout(() => this.closeModal(), 2000);
        }
    }
    
    closeModal() {
        const modal = document.getElementById('daily-reward-modal');
        if (modal) modal.classList.add('hidden');
    }
}

// ==================== ЛИДЕРБОРД ====================
class Leaderboard {
    constructor() {
        this.players = this.loadPlayers();
    }
    
    loadPlayers() {
        // Загружаем из localStorage или создаём демо-данные
        const saved = localStorage.getItem('batyrbol_leaderboard');
        if (saved) {
            return JSON.parse(saved);
        }
        
        // Демо-данные для лидерборда
        return [
            { name: 'Арман', xp: 2500, level: 12, avatar: '🦁' },
            { name: 'Айгерім', xp: 2200, level: 11, avatar: '🦊' },
            { name: 'Нұрсұлтан', xp: 1900, level: 10, avatar: '🐺' },
            { name: 'Дана', xp: 1700, level: 9, avatar: '🦅' },
            { name: 'Ерлан', xp: 1500, level: 8, avatar: '🐎' },
            { name: 'Мадина', xp: 1300, level: 7, avatar: '🦋' },
            { name: 'Асқар', xp: 1100, level: 6, avatar: '🐻' },
            { name: 'Жансая', xp: 900, level: 5, avatar: '🦌' },
            { name: 'Бауыржан', xp: 700, level: 4, avatar: '🐯' },
            { name: 'Әсел', xp: 500, level: 3, avatar: '🦢' }
        ];
    }
    
    savePlayers() {
        localStorage.setItem('batyrbol_leaderboard', JSON.stringify(this.players));
    }
    
    updatePlayer(name, xp, level) {
        const existing = this.players.find(p => p.name === name);
        if (existing) {
            existing.xp = xp;
            existing.level = level;
        } else {
            this.players.push({ name, xp, level, avatar: '🎮' });
        }
        
        // Сортируем по XP
        this.players.sort((a, b) => b.xp - a.xp);
        this.players = this.players.slice(0, 100); // Топ 100
        this.savePlayers();
    }
    
    getPlayerRank(name) {
        const index = this.players.findIndex(p => p.name === name);
        return index >= 0 ? index + 1 : null;
    }
    
    showLeaderboardModal() {
        const lang = document.body.dataset.language || 'kz';
        
        let modal = document.getElementById('leaderboard-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'leaderboard-modal';
            modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4';
            document.body.appendChild(modal);
        }
        
        const top10 = this.players.slice(0, 10);
        
        modal.innerHTML = `
            <div class="glass rounded-2xl max-w-lg w-full max-h-[80vh] overflow-hidden">
                <div class="p-6 border-b border-white/10 flex justify-between items-center">
                    <h2 class="text-xl font-bold text-white">
                        🏆 ${lang === 'kz' ? 'Үздіктер тізімі' : 'Таблица лидеров'}
                    </h2>
                    <button onclick="leaderboard.closeModal()" class="text-zinc-400 hover:text-white">
                        <iconify-icon icon="lucide:x" width="24"></iconify-icon>
                    </button>
                </div>
                
                <div class="p-4 overflow-y-auto max-h-[60vh]">
                    <!-- Топ 3 -->
                    <div class="flex justify-center gap-4 mb-6">
                        ${top10.slice(0, 3).map((p, i) => `
                            <div class="text-center ${i === 0 ? 'order-2' : i === 1 ? 'order-1' : 'order-3'}">
                                <div class="w-16 h-16 mx-auto rounded-2xl ${i === 0 ? 'bg-gold-500' : i === 1 ? 'bg-zinc-400' : 'bg-amber-700'} flex items-center justify-center text-3xl mb-2 ${i === 0 ? 'scale-110' : ''}">
                                    ${p.avatar}
                                </div>
                                <div class="text-white font-bold">${p.name}</div>
                                <div class="text-gold-400 text-sm">${p.xp} XP</div>
                                <div class="text-2xl mt-1">${i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉'}</div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <!-- Остальные -->
                    <div class="space-y-2">
                        ${top10.slice(3).map((p, i) => `
                            <div class="flex items-center gap-4 p-3 bg-zinc-800/50 rounded-xl">
                                <span class="w-8 text-center text-zinc-500 font-bold">${i + 4}</span>
                                <div class="w-10 h-10 rounded-xl bg-zinc-700 flex items-center justify-center text-xl">
                                    ${p.avatar}
                                </div>
                                <div class="flex-1">
                                    <div class="text-white font-medium">${p.name}</div>
                                    <div class="text-zinc-500 text-xs">${lang === 'kz' ? 'Деңгей' : 'Уровень'} ${p.level}</div>
                                </div>
                                <div class="text-gold-400 font-bold">${p.xp} XP</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }
    
    closeModal() {
        const modal = document.getElementById('leaderboard-modal');
        if (modal) modal.classList.add('hidden');
    }
}

// ==================== СТАТИСТИКА ПРОГРЕССА ====================
class UserStats {
    constructor() {
        this.loadStats();
    }
    
    loadStats() {
        const saved = localStorage.getItem('batyrbol_stats');
        if (saved) {
            this.stats = JSON.parse(saved);
        } else {
            this.stats = {
                totalMissions: 0,
                totalCorrect: 0,
                totalWrong: 0,
                totalXP: 0,
                bestStreak: 0,
                playTime: 0, // в минутах
                topicsCompleted: [],
                dailyStats: {},
                startDate: new Date().toISOString()
            };
        }
    }
    
    saveStats() {
        localStorage.setItem('batyrbol_stats', JSON.stringify(this.stats));
    }
    
    recordMission(topic, correct, wrong, xp) {
        this.stats.totalMissions++;
        this.stats.totalCorrect += correct;
        this.stats.totalWrong += wrong;
        this.stats.totalXP += xp;
        
        if (!this.stats.topicsCompleted.includes(topic)) {
            this.stats.topicsCompleted.push(topic);
        }
        
        // Дневная статистика
        const today = new Date().toISOString().split('T')[0];
        if (!this.stats.dailyStats[today]) {
            this.stats.dailyStats[today] = { missions: 0, xp: 0 };
        }
        this.stats.dailyStats[today].missions++;
        this.stats.dailyStats[today].xp += xp;
        
        this.saveStats();
    }
    
    updateStreak(streak) {
        if (streak > this.stats.bestStreak) {
            this.stats.bestStreak = streak;
            this.saveStats();
        }
    }
    
    getAccuracy() {
        const total = this.stats.totalCorrect + this.stats.totalWrong;
        return total > 0 ? Math.round((this.stats.totalCorrect / total) * 100) : 0;
    }
    
    showStatsModal() {
        const lang = document.body.dataset.language || 'kz';
        const accuracy = this.getAccuracy();
        
        let modal = document.getElementById('stats-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'stats-modal';
            modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="glass rounded-2xl max-w-lg w-full p-6">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-xl font-bold text-white">
                        📊 ${lang === 'kz' ? 'Менің статистикам' : 'Моя статистика'}
                    </h2>
                    <button onclick="userStats.closeModal()" class="text-zinc-400 hover:text-white">
                        <iconify-icon icon="lucide:x" width="24"></iconify-icon>
                    </button>
                </div>
                
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div class="bg-zinc-800/50 rounded-xl p-4 text-center">
                        <iconify-icon icon="lucide:target" class="text-gold-400" width="32"></iconify-icon>
                        <div class="text-2xl font-bold text-white mt-2">${this.stats.totalMissions}</div>
                        <div class="text-zinc-500 text-sm">${lang === 'kz' ? 'Миссиялар' : 'Миссий'}</div>
                    </div>
                    <div class="bg-zinc-800/50 rounded-xl p-4 text-center">
                        <iconify-icon icon="lucide:zap" class="text-gold-400" width="32"></iconify-icon>
                        <div class="text-2xl font-bold text-white mt-2">${this.stats.totalXP}</div>
                        <div class="text-zinc-500 text-sm">XP</div>
                    </div>
                    <div class="bg-zinc-800/50 rounded-xl p-4 text-center">
                        <iconify-icon icon="lucide:percent" class="text-green-400" width="32"></iconify-icon>
                        <div class="text-2xl font-bold text-white mt-2">${accuracy}%</div>
                        <div class="text-zinc-500 text-sm">${lang === 'kz' ? 'Дәлдік' : 'Точность'}</div>
                    </div>
                    <div class="bg-zinc-800/50 rounded-xl p-4 text-center">
                        <iconify-icon icon="lucide:flame" class="text-orange-400" width="32"></iconify-icon>
                        <div class="text-2xl font-bold text-white mt-2">${this.stats.bestStreak}</div>
                        <div class="text-zinc-500 text-sm">${lang === 'kz' ? 'Үздік серия' : 'Лучшая серия'}</div>
                    </div>
                </div>
                
                <div class="bg-zinc-800/50 rounded-xl p-4">
                    <h3 class="text-white font-medium mb-3">${lang === 'kz' ? 'Өтілген тақырыптар' : 'Пройденные темы'}</h3>
                    <div class="flex flex-wrap gap-2">
                        ${this.stats.topicsCompleted.length > 0 
                            ? this.stats.topicsCompleted.map(t => `<span class="px-3 py-1 bg-gold-500/20 text-gold-400 rounded-full text-sm">${t}</span>`).join('')
                            : `<span class="text-zinc-500">${lang === 'kz' ? 'Әлі жоқ' : 'Пока нет'}</span>`
                        }
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }
    
    closeModal() {
        const modal = document.getElementById('stats-modal');
        if (modal) modal.classList.add('hidden');
    }
}

// ==================== ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ ====================
let soundEffects = new SoundEffects();
let dailyRewards = new DailyRewards();
let leaderboard = new Leaderboard();
let userStats = new UserStats();

// Проверяем ежедневную награду при загрузке
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (dailyRewards.canClaim() && document.getElementById('game') && !document.getElementById('game').classList.contains('hidden')) {
            dailyRewards.showRewardModal();
        }
    }, 1000);
});
