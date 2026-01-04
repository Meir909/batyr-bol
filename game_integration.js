// Интеграция адаптивной модели обучения с веб-игрой
class GameIntegration {
    constructor() {
        this.userProfile = {
            id: null,
            name: '',
            email: '',
            avatarUrl: null,
            xp: 0,
            level: 1,
            language: 'kk',
            completedMissions: [],
            skillLevel: 'beginner',
            historyAnswers: [],
            voiceMissionsCompleted: 0,
            streak: 1,
            createdAt: null,
            lastLogin: null
        };

        this.currentContent = null;
        this.currentQuestions = [];
        this.adaptiveModel = null;
        
        this.geminiApiKey = '';
        this.geminiApiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

        this.loadGeminiApiKey();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUserProfile();
        this.updateUI();
    }

    async loadGeminiApiKey() {
        if (typeof window !== 'undefined' && window.GEMINI_API_KEY) {
            this.geminiApiKey = window.GEMINI_API_KEY;
        }
    }

    setupEventListeners() {
        const attachListener = (selector, event, handler) => {
            const element = document.getElementById(selector);
            if (element) {
                if (!element.hasAttribute('data-listener-attached')) {
                    element.addEventListener(event, handler);
                    element.setAttribute('data-listener-attached', 'true');
                }
                return true;
            }
            return false;
        };

        attachListener('btn-kz-game', 'click', () => this.switchLanguage('kk'));
        attachListener('btn-ru-game', 'click', () => this.switchLanguage('ru'));

        const setupMissionButton = () => {
            if (!attachListener('missions-btn', 'click', () => this.getMissions())) {
                setTimeout(setupMissionButton, 500);
            }
        };
        setupMissionButton();

        attachListener('answer-form', 'submit', (e) => this.submitAnswer(e));
        attachListener('upload-avatar-btn', 'click', () => this.uploadAvatar());
        attachListener('batyr-avatar-btn', 'click', () => this.generateBatyrAvatar());
        attachListener('profile-avatar-file', 'change', () => this.previewSelectedAvatar());
    }

    loadUserProfile() {
        const savedProfile = localStorage.getItem('batyrBolUserProfile');
        if (savedProfile) {
            this.userProfile = { ...this.userProfile, ...JSON.parse(savedProfile) };
            if (this.userProfile.id && this.userProfile.email) {
                this.userProfile.lastLogin = new Date().toISOString();
                this.saveUserProfile();
                this.showGameScreen();
            }
        }
    }

    async registerUser(name, email, password) {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || 'Ошибка регистрации');
        }

        this.userProfile = { ...this.userProfile, ...data.user };
        this.saveUserProfile();
        return true;
    }

    async loginUser(email, password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || 'Ошибка входа');
        }

        this.userProfile = { ...this.userProfile, ...data.user };
        this.saveUserProfile();
        return true;
    }

    logoutUser() {
        this.userProfile = {
            id: null,
            name: '',
            email: '',
            avatarUrl: null,
            xp: 0,
            level: 1,
            language: 'kk',
            completedMissions: [],
            skillLevel: 'beginner',
            historyAnswers: [],
            voiceMissionsCompleted: 0,
            streak: 1,
            createdAt: null,
            lastLogin: null
        };
        this.saveUserProfile();
        this.showAuthScreen();
    }

    async updateUserProfile(name, email, password) {
        const requestData = { email: this.userProfile.email };
        if (name) requestData.name = name;
        if (email && email !== this.userProfile.email) requestData.new_email = email;
        if (password) requestData.password = password;

        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || 'Ошибка обновления профиля');
        }

        this.userProfile = { ...this.userProfile, ...data.user };
        this.saveUserProfile();
        this.updateProfileInfo();
        return true;
    }

    showAuthScreen() {
        document.getElementById('auth').classList.remove('hidden');
        document.getElementById('game').classList.add('hidden');
    }

    showGameScreen() {
        document.getElementById('auth').classList.add('hidden');
        document.getElementById('game').classList.remove('hidden');
        this.updateProfileInfo();
        this.updateLanguageUI();
    }

    saveUserProfile() {
        localStorage.setItem('batyrBolUserProfile', JSON.stringify(this.userProfile));
    }

    switchLanguage(lang) {
        this.userProfile.language = lang;
        this.saveUserProfile();
        this.updateLanguageUI();
        this.updateUI();
    }

    updateLanguageUI() {
        const kzBtn = document.getElementById('btn-kz-game');
        const ruBtn = document.getElementById('btn-ru-game');

        if (kzBtn && ruBtn) {
            if (this.userProfile.language === 'kk') {
                kzBtn.classList.add('bg-white', 'text-black');
                kzBtn.classList.remove('text-zinc-400', 'hover:text-white');
                ruBtn.classList.remove('bg-white', 'text-black');
                ruBtn.classList.add('text-zinc-400', 'hover:text-white');
            } else {
                ruBtn.classList.add('bg-white', 'text-black');
                ruBtn.classList.remove('text-zinc-400', 'hover:text-white');
                kzBtn.classList.remove('bg-white', 'text-black');
                kzBtn.classList.add('text-zinc-400', 'hover:text-white');
            }
        }
    }

    async getMissions() {
        try {
            const content = await this.fetchAdaptiveContent();
            this.currentContent = content;
            this.currentQuestions = content.questions || [];

            this.displayContent(content);
            this.hideQuestions();
            this.saveGameState();
            this.showMessage('Жаңа миссиялар алынды! / Новые миссии получены!', 'success');
        } catch (error) {
            console.error('Ошибка получения миссий:', error);
            this.showMessage('Миссияларды алу кезінде қате пайда болды', 'error');
        }
    }

    async fetchAdaptiveContent() {
        const topics = [
            'Абылай хан',
            'Қазақ хандығы',
            'Тәуке хан',
            'Қазақстан тәуелсіздігі'
        ];

        const randomTopic = topics[Math.floor(Math.random() * topics.length)];

        const response = await fetch('/api/content/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: randomTopic })
        });

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || 'Ошибка генерации контента');
        }

        const content = data.content;
        let text = content.text_kz;
        let questions = (content.questions_kz || []).map((q, idx) => ({
            id: `srv_q_${Date.now()}_${idx}`,
            text: q,
            type: 'open'
        }));

        if (this.userProfile.language === 'ru') {
            const tResp = await fetch('/api/content/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text_kz: text })
            });
            const tData = await tResp.json();
            if (tData.success && tData.text_ru) {
                text = tData.text_ru;
            }

            if (questions.length > 0) {
                const joined = questions.map(q => q.text).join('\n');
                const qResp = await fetch('/api/content/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text_kz: joined })
                });
                const qData = await qResp.json();
                if (qData.success && qData.text_ru) {
                    const parts = qData.text_ru.split('\n').map(s => s.trim()).filter(Boolean);
                    questions = parts.map((qq, idx) => ({
                        id: `srv_q_${Date.now()}_${idx}`,
                        text: qq,
                        type: 'open'
                    }));
                }
            }
        }

        return {
            title: randomTopic,
            text,
            difficulty: this.userProfile.skillLevel,
            keyFacts: [],
            keywords: [randomTopic],
            sources: content.sources || [],
            questions,
            image_url: content.image_url || null
        };
    }

    displayContent(content) {
        // Используем новый игровой движок
        if (typeof gameEngine !== 'undefined') {
            gameEngine.setLanguage(this.userProfile.language === 'kk' ? 'kz' : 'ru');
            gameEngine.startMission({
                text: content.text,
                topic: content.title,
                questions: content.questions || []
            });
            return;
        }
        
        // Fallback к старому методу
        const contentContainer = document.getElementById('mission-content');
        if (contentContainer) {
            contentContainer.innerHTML = `
                <h3 class="text-xl text-white mb-2">${content.title}</h3>
                <p class="text-zinc-300 mb-4">${content.text}</p>
                <button id="read-complete-btn" class="mt-4 px-4 py-2 bg-gold-500 hover:bg-gold-600 text-black rounded-full transition-colors font-medium">
                    ${this.userProfile.language === 'kk' ? 'Оқыдым' : 'Прочитал'}
                </button>
            `;

            const readBtn = document.getElementById('read-complete-btn');
            if (readBtn) {
                readBtn.addEventListener('click', () => {
                    this.showQuestions();
                    readBtn.style.display = 'none';
                });
            }
        }
    }

    displayQuestions(questions) {
        const questionsContainer = document.getElementById('mission-questions');
        if (questionsContainer) {
            questionsContainer.innerHTML = '';

            questions.forEach((q, index) => {
                const questionElement = document.createElement('div');
                questionElement.className = 'mb-4 p-3 bg-zinc-800/30 rounded-lg border border-white/10';
                questionElement.innerHTML = `
                    <div class="flex items-start gap-2">
                        <span class="text-gold-400 font-medium">${index + 1}.</span>
                        <div class="flex-1">
                            <p class="text-white mb-2">${q.text}</p>
                            <textarea id="text-answer-${q.id}" 
                                     class="w-full px-3 py-2 bg-zinc-800/50 border border-white/10 rounded-lg text-white outline-none focus:border-gold-500/50 transition-colors" 
                                     rows="3" 
                                     placeholder="${this.userProfile.language === 'kk' ? 'Жауабыңызды жазыңыз...' : 'Введите ваш ответ...'}"></textarea>
                        </div>
                    </div>
                `;
                questionsContainer.appendChild(questionElement);
            });
        }
    }

    hideQuestions() {
        const questionsContainer = document.getElementById('mission-questions');
        if (questionsContainer) {
            questionsContainer.style.display = 'none';
        }

        const answerForm = document.getElementById('answer-form');
        if (answerForm) {
            answerForm.style.display = 'none';
        }
    }

    showQuestions() {
        const questionsContainer = document.getElementById('mission-questions');
        if (questionsContainer) {
            questionsContainer.style.display = 'block';
            this.displayQuestions(this.currentQuestions);
        }

        const answerForm = document.getElementById('answer-form');
        if (answerForm) {
            answerForm.style.display = 'block';
        }
    }

    updateUI() {
        this.updateProfileInfo();
        this.updateLanguageUI();
    }

    updateProfileInfo() {
        const xpElement = document.getElementById('user-xp');
        const levelElement = document.getElementById('user-level');
        const streakElement = document.getElementById('user-streak');
        const userNameElement = document.getElementById('user-name');

        const userAvatarImg = document.getElementById('user-avatar');
        const userAvatarFallback = document.getElementById('user-avatar-fallback');
        const modalAvatarImg = document.getElementById('profile-avatar-preview');
        const modalAvatarFallback = document.getElementById('profile-avatar-fallback');

        if (xpElement) xpElement.textContent = this.userProfile.xp;
        if (levelElement) levelElement.textContent = this.userProfile.level;
        if (streakElement) streakElement.textContent = this.userProfile.streak;
        if (userNameElement) userNameElement.textContent = this.userProfile.name || 'Batyr #001';

        if (this.userProfile.avatarUrl) {
            if (userAvatarImg && userAvatarFallback) {
                userAvatarImg.src = this.userProfile.avatarUrl;
                userAvatarImg.classList.remove('hidden');
                userAvatarFallback.classList.add('hidden');
            }
            if (modalAvatarImg && modalAvatarFallback) {
                modalAvatarImg.src = this.userProfile.avatarUrl;
                modalAvatarImg.classList.remove('hidden');
                modalAvatarFallback.classList.add('hidden');
            }
        } else {
            if (userAvatarImg && userAvatarFallback) {
                userAvatarImg.removeAttribute('src');
                userAvatarImg.classList.add('hidden');
                userAvatarFallback.classList.remove('hidden');
            }
        }
    }

    previewSelectedAvatar() {
        const avatarFileInput = document.getElementById('profile-avatar-file');
        const previewImg = document.getElementById('profile-avatar-preview');
        const fallbackIcon = document.getElementById('profile-avatar-fallback');
        
        if (!avatarFileInput || !previewImg || !fallbackIcon) return;
        
        const file = avatarFileInput.files && avatarFileInput.files[0];
        if (!file) return;
        
        const objectUrl = URL.createObjectURL(file);
        previewImg.src = objectUrl;
        previewImg.classList.remove('hidden');
        fallbackIcon.classList.add('hidden');
    }

    async uploadAvatar() {
        try {
            if (!this.userProfile.email) {
                throw new Error('Сначала войдите в систему');
            }

            const avatarFileInput = document.getElementById('profile-avatar-file');
            if (!avatarFileInput || !avatarFileInput.files || !avatarFileInput.files[0]) {
                throw new Error('Выберите файл аватара');
            }

            const formData = new FormData();
            formData.append('email', this.userProfile.email);
            formData.append('avatar', avatarFileInput.files[0]);

            const response = await fetch('/api/profile/avatar', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Ошибка загрузки аватара');
            }

            this.userProfile = { ...this.userProfile, ...data.user };
            this.saveUserProfile();
            this.updateProfileInfo();
            this.showMessage('Аватар обновлен!', 'success');
        } catch (error) {
            this.showMessage(error.message || 'Ошибка загрузки аватара', 'error');
        }
    }

    async generateBatyrAvatar() {
        try {
            if (!this.userProfile.email) {
                throw new Error('Сначала войдите в систему');
            }

            const response = await fetch('/api/profile/avatar/batyr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: this.userProfile.email })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Ошибка генерации аватара');
            }

            this.userProfile = { ...this.userProfile, ...data.user };
            this.saveUserProfile();
            this.updateProfileInfo();
            this.showMessage('Батыр-аватар создан!', 'success');
        } catch (error) {
            this.showMessage(error.message || 'Ошибка генерации аватара', 'error');
        }
    }
    
    showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('game-messages');
        if (messageContainer) {
            const messageElement = document.createElement('div');
            messageElement.className = `p-3 rounded-lg mb-2 ${
                type === 'success' ? 'bg-green-900/50 border border-green-500/30' :
                type === 'error' ? 'bg-red-900/50 border border-red-500/30' :
                type === 'achievement' ? 'bg-purple-900/50 border border-purple-500/30' :
                'bg-blue-900/50 border border-blue-500/30'
            }`;
            messageElement.textContent = message;
            
            messageContainer.appendChild(messageElement);
            
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 5000);
        }
    }
    
    saveGameState() {
        const gameState = {
            userProfile: this.userProfile,
            currentContent: this.currentContent,
            currentQuestions: this.currentQuestions
        };
        localStorage.setItem('batyrBolGameState', JSON.stringify(gameState));
    }
    
    loadGameState() {
        const savedState = localStorage.getItem('batyrBolGameState');
        if (savedState) {
            const state = JSON.parse(savedState);
            this.userProfile = state.userProfile || this.userProfile;
            this.currentContent = state.currentContent || null;
            this.currentQuestions = state.currentQuestions || [];
            
            if (this.currentContent) {
                this.displayContent(this.currentContent);
            }
            
            if (this.currentQuestions.length > 0) {
                this.displayQuestions(this.currentQuestions);
            }
            
            this.updateUI();
        }
    }
}

// Инициализация интеграции при загрузке страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.gameIntegration = new GameIntegration();
    });
} else {
    window.gameIntegration = new GameIntegration();
}
