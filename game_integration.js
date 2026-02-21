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

        // NOTE: missions-btn is handled by igra.html onclick="openCharacterSelection()"
        // Disabled old getMissions() to use new mission system
        // const setupMissionButton = () => {
        //     if (!attachListener('missions-btn', 'click', () => this.getMissions())) {
        //         setTimeout(setupMissionButton, 500);
        //     }
        // };
        // setupMissionButton();

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
        try {
            const data = await this.requestJson('/api/register', {
                method: 'POST',
                body: { name, email, password }
            });
            if (!data || !data.success) {
                throw new Error((data && data.message) || 'Ошибка регистрации');
            }
            this.userProfile = { ...this.userProfile, ...data.user };
        } catch (err) {
            // Offline fallback: register locally via localStorage
            if (window.location.protocol === 'file:' || err.message === 'Request timeout' || err.message.includes('Failed to fetch')) {
                const users = JSON.parse(localStorage.getItem('batyrbol_users') || '{}');
                if (users[email]) {
                    throw new Error('Бұл email тіркелген / Этот email уже зарегистрирован');
                }
                users[email] = { name, email, password, xp: 0, level: 1, createdAt: new Date().toISOString() };
                localStorage.setItem('batyrbol_users', JSON.stringify(users));
                this.userProfile = {
                    ...this.userProfile,
                    id: email,
                    name,
                    email,
                    xp: 0,
                    level: 1,
                    createdAt: new Date().toISOString(),
                    lastLogin: new Date().toISOString()
                };
            } else {
                throw err;
            }
        }
        this.saveUserProfile();
        localStorage.setItem('batyrbol_user', JSON.stringify({ name: this.userProfile.name, xp: this.userProfile.xp }));
        return true;
    }

    async loginUser(email, password) {
        try {
            const data = await this.requestJson('/api/login', {
                method: 'POST',
                body: { email, password }
            });
            if (!data || !data.success) {
                throw new Error((data && data.message) || 'Ошибка входа');
            }
            this.userProfile = { ...this.userProfile, ...data.user };
        } catch (err) {
            // Offline fallback: login locally via localStorage
            if (window.location.protocol === 'file:' || err.message === 'Request timeout' || err.message.includes('Failed to fetch')) {
                const users = JSON.parse(localStorage.getItem('batyrbol_users') || '{}');
                const user = users[email];
                if (!user || user.password !== password) {
                    throw new Error('Қате email немесе құпия сөз / Неверный email или пароль');
                }
                this.userProfile = {
                    ...this.userProfile,
                    id: email,
                    name: user.name,
                    email,
                    xp: user.xp || 0,
                    level: user.level || 1,
                    lastLogin: new Date().toISOString()
                };
            } else {
                throw err;
            }
        }
        this.saveUserProfile();
        localStorage.setItem('batyrbol_user', JSON.stringify({ name: this.userProfile.name, xp: this.userProfile.xp }));
        return true;
    }

    // Alias for backward compatibility
    async login(email, password) {
        return await this.loginUser(email, password);
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

        const data = await this.requestJson('/api/profile', {
            method: 'PUT',
            body: requestData
        });
        if (!data || !data.success) {
            throw new Error((data && data.message) || 'Ошибка обновления профиля');
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

    async requestJson(url, { method = 'GET', body, headers = {}, timeoutMs = 20000 } = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        try {
            const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
            const isPlainObjectBody = body && !isFormData && typeof body === 'object';
            const finalHeaders = { ...headers };
            let finalBody = body;

            if (isPlainObjectBody) {
                finalBody = JSON.stringify(body);
                if (!finalHeaders['Content-Type']) finalHeaders['Content-Type'] = 'application/json';
            }

            const response = await fetch(url, {
                method,
                headers: finalHeaders,
                body: finalBody,
                signal: controller.signal
            });

            const contentType = response.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');

            const data = isJson
                ? await response.json().catch(() => null)
                : await response.text().catch(() => '');

            if (!response.ok) {
                const message =
                    (data && typeof data === 'object' && (data.message || data.error)) ||
                    (typeof data === 'string' && data) ||
                    response.statusText ||
                    `HTTP ${response.status}`;
                throw new Error(message);
            }

            return data;
        } catch (error) {
            if (error && error.name === 'AbortError') throw new Error('Request timeout');
            throw error;
        } finally {
            clearTimeout(timeoutId);
        }
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


    markMissionStarted() {
        // Save mission start time for penalty tracking
        const missionState = {
            startedAt: new Date().toISOString(),
            missionId: Date.now(),
            completed: false
        };
        localStorage.setItem('batyrbol_current_mission', JSON.stringify(missionState));
    }

    markMissionCompleted() {
        // Clear incomplete mission flag
        localStorage.removeItem('batyrbol_current_mission');

        // Record successful completion for clan
        const clanData = JSON.parse(localStorage.getItem('batyrbol_clan_data') || '{"readToday": []}');
        if (!clanData.readToday.includes(this.userProfile.email)) {
            clanData.readToday.push(this.userProfile.email);
            localStorage.setItem('batyrbol_clan_data', JSON.stringify(clanData));
        }

        // Track mission completion with server
        this.trackClanActivity(true, false);
    }

    checkIncompleteMission() {
        const incompleteMission = localStorage.getItem('batyrbol_current_mission');

        if (incompleteMission) {
            try {
                const missionData = JSON.parse(incompleteMission);
                const startedAt = new Date(missionData.startedAt);
                const now = new Date();
                const hoursSince = (now - startedAt) / (1000 * 60 * 60);

                // If mission was started more than 1 hour ago and not completed
                if (hoursSince > 1 && !missionData.completed) {
                    // Apply clan penalty
                    this.applyClanPenalty();
                    
                    // Track mission skip with server
                    this.trackClanActivity(false, true);
                    
                    localStorage.removeItem('batyrbol_current_mission');
                }
            } catch (error) {
                console.error('Error checking incomplete mission:', error);
            }
        }
    }

    async trackClanActivity(missionCompleted = false, missionSkipped = false) {
        try {
            const userEmail = this.userProfile.email;
            if (!userEmail) return;

            const response = await this.requestJson('/api/clans/activity', {
                method: 'POST',
                body: {
                    email: userEmail,
                    mission_completed: missionCompleted,
                    mission_skipped: missionSkipped
                }
            });

            if (response.success) {
                console.log('Clan activity tracked successfully');
            }
        } catch (error) {
            console.error('Error tracking clan activity:', error);
        }
    }

    async updateClanLeaderboard() {
        try {
            // Trigger leaderboard update on server
            const response = await this.requestJson('/api/clans/leaderboard', {
                method: 'GET'
            });

            if (response.success) {
                console.log('Clan leaderboard updated successfully');
                
                // If user is on clan page, refresh the data
                if (window.location.pathname.includes('clan.html') || 
                    window.location.href.includes('clan.html')) {
                    // Trigger refresh if clan page functions are available
                    if (typeof loadClanLeaderboard === 'function') {
                        loadClanLeaderboard();
                    }
                }
            }
        } catch (error) {
            console.error('Error updating clan leaderboard:', error);
        }
    }

    applyClanPenalty() {
        const clanData = JSON.parse(localStorage.getItem('batyrbol_clan_data') || '{"xp": 0, "penalties": 0}');

        clanData.xp = (clanData.xp || 0) - 10;
        clanData.penalties = (clanData.penalties || 0) + 1;
        clanData.lastPenalty = new Date().toISOString();

        localStorage.setItem('batyrbol_clan_data', JSON.stringify(clanData));

        // Show penalty notification
        const message = this.userProfile.language === 'kk'
            ? '⚠️ Сенің кланың -10 XP жоғалтты! Миссияны аяқтамадыңыз.'
            : '⚠️ Ваш клан потерял -10 XP! Вы не завершили миссию.';

        this.showMessage(message, 'warning');
    }


    displayContent(content) {
        // AI badge indicator
        const aiBadge = content.ai_generated && content.personalized
            ? `<span class="inline-flex items-center gap-1 px-3 py-1 bg-gold-500/20 text-gold-400 text-xs rounded-full border border-gold-500/30">
                <span>✨</span>
                <span>${this.userProfile.language === 'kk' ? 'AI жасаған миссия' : 'AI миссия'}</span>
               </span>`
            : '';

        // Используем новый игровой движок
        if (typeof gameEngine !== 'undefined') {
            gameEngine.setLanguage(this.userProfile.language === 'kk' ? 'kz' : 'ru');
            gameEngine.startMission({
                text: content.text,
                topic: content.title,
                questions: content.questions || [],
                aiBadge: aiBadge
            });
            return;
        }

        // Fallback к старому методу с принудительным чтением
        const contentContainer = document.getElementById('mission-content');
        if (contentContainer) {
            const missionText = content.text_kz || content.text || '';
            const wordCount = this.countWords(missionText);
            const readingTimeSeconds = Math.max(10, Math.ceil(wordCount / 3)); // минимум 10 секунд

            contentContainer.innerHTML = `
                <div class="mb-3">${aiBadge}</div>
                <h3 class="text-xl text-white mb-2">${content.title || content.topic || 'Миссия'}</h3>

                <!-- Mission Text -->
                <div class="bg-zinc-900/50 border border-white/10 rounded-xl p-6 mb-6">
                    <!-- Audio Button -->
                    <div class="flex items-center justify-between mb-4">
                        <h4 class="text-sm font-medium text-zinc-400">
                            ${this.userProfile.language === 'kk' ? 'Миссия мәтіні' : 'Текст миссии'}
                        </h4>
                        <button id="speak-text-btn" class="flex items-center gap-2 px-3 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition-colors">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
                            </svg>
                            <span id="speak-btn-text">${this.userProfile.language === 'kk' ? 'Тыңдау' : 'Слушать'}</span>
                        </button>
                    </div>
                    <p id="mission-text-content" class="text-zinc-300 leading-relaxed text-base">${missionText}</p>
                </div>

                <!-- Reading Timer -->
                <div id="reading-timer" class="mb-6">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-zinc-400">
                            ${this.userProfile.language === 'kk' ? 'Оқу уақыты' : 'Время чтения'}
                        </span>
                        <span class="text-sm text-gold-400 font-medium" id="timer-text">
                            ${this.formatTime(readingTimeSeconds)}
                        </span>
                    </div>
                    <div class="h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div id="reading-progress-bar" class="h-full progress-bar rounded-full transition-all" style="width: 0%"></div>
                    </div>
                    <p class="text-xs text-zinc-500 mt-2">
                        ${this.userProfile.language === 'kk'
                            ? 'Мәтінді мұқият оқыңыз. Сұрақтарға жауап беру үшін оқуды аяқтау керек.'
                            : 'Внимательно читайте текст. Нужно дочитать до конца, чтобы ответить на вопросы.'}
                    </p>
                </div>

                <!-- Questions Button (locked initially) -->
                <button id="read-complete-btn" disabled class="w-full px-6 py-4 bg-zinc-700 text-zinc-500 rounded-xl font-medium cursor-not-allowed flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                    </svg>
                    <span>${this.userProfile.language === 'kk' ? 'Сұрақтарды көру' : 'Показать вопросы'}</span>
                </button>
            `;

            // Start reading timer
            this.startReadingTimer(readingTimeSeconds);

            // Setup audio button
            this.setupTextToSpeech(missionText);
        }
    }

    setupTextToSpeech(text) {
        const speakBtn = document.getElementById('speak-text-btn');
        const speakBtnText = document.getElementById('speak-btn-text');

        if (!speakBtn || !('speechSynthesis' in window)) {
            // Hide button if speech synthesis not supported
            if (speakBtn) speakBtn.style.display = 'none';
            return;
        }

        let isSpeaking = false;
        let utterance = null;

        speakBtn.addEventListener('click', () => {
            if (isSpeaking) {
                // Stop speaking
                window.speechSynthesis.cancel();
                isSpeaking = false;
                speakBtnText.textContent = this.userProfile.language === 'kk' ? 'Тыңдау' : 'Слушать';
                speakBtn.classList.remove('bg-gold-500', 'text-black');
                speakBtn.classList.add('bg-zinc-800', 'text-zinc-300');
            } else {
                // Start speaking
                utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'kk-KZ'; // Kazakh language
                utterance.rate = 0.9; // Slightly slower for better comprehension
                utterance.pitch = 1.0;

                utterance.onstart = () => {
                    isSpeaking = true;
                    speakBtnText.textContent = this.userProfile.language === 'kk' ? 'Тоқтату' : 'Остановить';
                    speakBtn.classList.add('bg-gold-500', 'text-black');
                    speakBtn.classList.remove('bg-zinc-800', 'text-zinc-300');
                };

                utterance.onend = () => {
                    isSpeaking = false;
                    speakBtnText.textContent = this.userProfile.language === 'kk' ? 'Тыңдау' : 'Слушать';
                    speakBtn.classList.remove('bg-gold-500', 'text-black');
                    speakBtn.classList.add('bg-zinc-800', 'text-zinc-300');
                };

                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event);
                    isSpeaking = false;
                    speakBtnText.textContent = this.userProfile.language === 'kk' ? 'Тыңдау' : 'Слушать';
                    speakBtn.classList.remove('bg-gold-500', 'text-black');
                    speakBtn.classList.add('bg-zinc-800', 'text-zinc-300');
                };

                window.speechSynthesis.speak(utterance);
            }
        });
    }

    countWords(text) {
        // Count words in text
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (mins > 0) {
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        return `${secs} сек`;
    }

    startReadingTimer(totalSeconds) {
        let remainingSeconds = totalSeconds;
        const progressBar = document.getElementById('reading-progress-bar');
        const timerText = document.getElementById('timer-text');
        const readBtn = document.getElementById('read-complete-btn');

        if (!progressBar || !timerText || !readBtn) return;

        const interval = setInterval(() => {
            remainingSeconds--;
            const progress = ((totalSeconds - remainingSeconds) / totalSeconds) * 100;

            progressBar.style.width = `${progress}%`;
            timerText.textContent = this.formatTime(remainingSeconds);

            if (remainingSeconds <= 0) {
                clearInterval(interval);
                // Unlock button with animation
                readBtn.disabled = false;
                readBtn.className = 'w-full px-6 py-4 btn-primary rounded-xl font-medium flex items-center justify-center gap-2 animate-pulse';
                readBtn.innerHTML = `
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                    <span>${this.userProfile.language === 'kk' ? 'Сұрақтарды көру' : 'Показать вопросы'}</span>
                `;

                timerText.textContent = this.userProfile.language === 'kk' ? 'Дайын!' : 'Готово!';
                timerText.className = 'text-sm text-green-400 font-medium';

                // Remove pulse after 3 seconds
                setTimeout(() => {
                    if (readBtn) {
                        readBtn.classList.remove('animate-pulse');
                    }
                }, 3000);

                // Add click handler
                readBtn.addEventListener('click', () => {
                    // Mark mission as completed (no clan penalty)
                    this.markMissionCompleted();

                    this.showQuestions();
                    document.getElementById('reading-timer').style.display = 'none';
                    readBtn.style.display = 'none';
                }, { once: true });
            }
        }, 1000);
    }

    displayQuestions(questions) {
        const questionsContainer = document.getElementById('mission-questions-list');
        if (questionsContainer) {
            questionsContainer.innerHTML = '';

            questions.forEach((q, index) => {
                const questionElement = document.createElement('div');
                questionElement.className = 'mb-4 p-3 bg-zinc-800/30 rounded-lg border border-white/10';
                
                if (q.type === 'multiple_choice' && q.options && q.options.length > 0) {
                    // Multiple choice question
                    questionElement.innerHTML = `
                        <div class="flex items-start gap-2">
                            <span class="text-gold-400 font-medium">${index + 1}.</span>
                            <div class="flex-1">
                                <p class="text-white mb-3">${q.text}</p>
                                <div class="space-y-2">
                                    ${q.options.map((option, optIndex) => `
                                        <label class="flex items-center gap-3 p-3 rounded-lg border border-white/10 hover:bg-white/5 cursor-pointer transition-colors">
                                            <input type="radio" name="question-${q.id}" value="${optIndex}" class="w-4 h-4 text-gold-500">
                                            <span class="text-zinc-300">${String.fromCharCode(65 + optIndex)}. ${option}</span>
                                        </label>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    // Open question
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
                }
                
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

            const data = await this.requestJson('/api/profile/avatar', {
                method: 'POST',
                body: formData
            });
            if (!data || !data.success) {
                throw new Error((data && data.message) || 'Ошибка загрузки аватара');
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

            const data = await this.requestJson('/api/profile/avatar/batyr', {
                method: 'POST',
                body: { email: this.userProfile.email }
            });
            if (!data || !data.success) {
                throw new Error((data && data.message) || 'Ошибка генерации аватара');
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
            messageElement.className = `p-3 rounded-lg mb-2 ${type === 'success' ? 'bg-green-900/50 border border-green-500/30' :
                    type === 'error' ? 'bg-red-900/50 border border-red-500/30' :
                    type === 'warning' ? 'bg-yellow-900/50 border border-yellow-500/30' :
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

    async submitAnswer(event) {
        event.preventDefault();
        
        try {
            const results = [];
            let totalScore = 0;
            let correctCount = 0;
            
            // Check each answer using Groq API
            for (const question of this.currentQuestions) {
                let userAnswer = '';
                
                if (question.type === 'multiple_choice' && question.options && question.options.length > 0) {
                    // Get selected radio button value
                    const selectedOption = document.querySelector(`input[name="question-${question.id}"]:checked`);
                    if (selectedOption) {
                        userAnswer = selectedOption.value;
                    } else {
                        this.showMessage('Пожалуйста, выберите ответ на все вопросы с вариантами', 'warning');
                        return;
                    }
                } else {
                    // Get textarea value for open questions
                    const answerElement = document.getElementById(`text-answer-${question.id}`);
                    userAnswer = answerElement ? answerElement.value.trim() : '';
                    
                    if (!userAnswer) {
                        this.showMessage('Пожалуйста, ответьте на все открытые вопросы', 'warning');
                        return;
                    }
                }
                
                // Use Groq API to check answer
                const data = await this.requestJson('/api/answer/check', {
                    method: 'POST',
                    body: {
                        question: question.text,
                        user_answer: userAnswer,
                        correct_answer: question.correctAnswer,
                        context: this.currentContent ? this.currentContent.text : null
                    }
                });
                if (!data || !data.success) {
                    throw new Error((data && data.message) || 'Ошибка проверки ответа');
                }
                
                // Show warning if fallback was used
                if (data.warning) {
                    this.showMessage(data.warning, 'warning');
                }
                
                const result = data.result;
                results.push({
                    question: question.text,
                    userAnswer: userAnswer,
                    result: result
                });
                
                totalScore += result.score || 0;
                if (result.is_correct) {
                    correctCount++;
                }
            }
            
            // Calculate XP and update profile
            const xpGained = Math.round(totalScore / this.currentQuestions.length);
            this.userProfile.xp += xpGained;
            this.userProfile.completedMissions.push({
                topic: this.currentContent.title,
                score: totalScore,
                completedAt: new Date().toISOString()
            });
            
            // Update streak
            if (totalScore > 70) { // If score is good enough
                this.userProfile.streak += 1;
            } else {
                this.userProfile.streak = Math.max(1, this.userProfile.streak - 1);
            }
            
            this.saveUserProfile();
            this.updateProfileInfo();
            
            // Update clan leaderboard after mission completion
            this.updateClanLeaderboard();
            
            // Display results
            this.displayResults(results, totalScore, correctCount, xpGained);
            
        } catch (error) {
            console.error('Error submitting answers:', error);
            this.showMessage('Ошибка при отправке ответов: ' + error.message, 'error');
        }
    }

    displayResults(results, totalScore, correctCount, xpGained) {
        const questionsContainer = document.getElementById('mission-questions');
        if (!questionsContainer) return;

        const percentage = Math.round((correctCount / results.length) * 100);
        const isPerfect = correctCount === results.length;
        const isGood = percentage >= 70;

        questionsContainer.innerHTML = `
            <div class="text-center mb-8">
                <!-- Success Icon with Animation -->
                <div class="inline-flex items-center justify-center w-20 h-20 sm:w-24 sm:h-24 rounded-full mb-6"
                     style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); animation: bounce 1s ease-in-out 3;">
                    <svg class="w-10 h-10 sm:w-12 sm:h-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                </div>

                <!-- Title -->
                <h3 class="text-2xl sm:text-3xl font-bold text-white mb-4">
                    ${isPerfect
                        ? (this.userProfile.language === 'kk' ? '🎉 Керемет!' : '🎉 Отлично!')
                        : (this.userProfile.language === 'kk' ? 'Миссия аяқталды!' : 'Миссия завершена!')}
                </h3>

                <!-- Stats Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 max-w-2xl mx-auto mb-6">
                    <!-- Score -->
                    <div class="glass rounded-xl p-4">
                        <div class="text-gold-400 text-3xl sm:text-4xl font-bold mb-1">${percentage}%</div>
                        <div class="text-zinc-400 text-sm">
                            ${this.userProfile.language === 'kk' ? 'Нәтиже' : 'Результат'}
                        </div>
                    </div>

                    <!-- Correct Answers -->
                    <div class="glass rounded-xl p-4">
                        <div class="text-green-400 text-3xl sm:text-4xl font-bold mb-1">${correctCount}/${results.length}</div>
                        <div class="text-zinc-400 text-sm">
                            ${this.userProfile.language === 'kk' ? 'Дұрыс' : 'Правильно'}
                        </div>
                    </div>

                    <!-- XP Gained -->
                    <div class="glass rounded-xl p-4">
                        <div class="text-blue-400 text-3xl sm:text-4xl font-bold mb-1">+${xpGained}</div>
                        <div class="text-zinc-400 text-sm">XP</div>
                    </div>
                </div>

                <!-- Performance Message -->
                <p class="text-base sm:text-lg ${isGood ? 'text-green-400' : 'text-yellow-400'} mb-2">
                    ${isPerfect
                        ? (this.userProfile.language === 'kk' ? 'Барлық жауаптар дұрыс! Сіз батырсыз! 🏆' : 'Все ответы правильные! Вы батыр! 🏆')
                        : isGood
                        ? (this.userProfile.language === 'kk' ? 'Жақсы нәтиже! Жалғастырыңыз! 💪' : 'Хороший результат! Продолжайте! 💪')
                        : (this.userProfile.language === 'kk' ? 'Мәтінді мұқият оқыңыз 📖' : 'Читайте текст внимательно 📖')}
                </p>
            </div>
            <div class="space-y-4">
                ${results.map((result, index) => `
                    <div class="p-4 rounded-lg border ${result.result.is_correct ? 'bg-green-900/20 border-green-500/30' : 'bg-red-900/20 border-red-500/30'}">
                        <div class="flex items-start gap-3">
                            <div class="flex-shrink-0">
                                <iconify-icon icon="${result.result.is_correct ? 'lucide:check-circle' : 'lucide:x-circle'}" 
                                    class="${result.result.is_correct ? 'text-green-400' : 'text-red-400'}" width="24"></iconify-icon>
                            </div>
                            <div class="flex-1">
                                <p class="text-white font-medium mb-2">${index + 1}. ${result.question}</p>
                                ${result.question.type === 'multiple_choice' && result.question.options ? `
                                    <p class="text-zinc-300 text-sm mb-2">
                                        ${this.userProfile.language === 'kk' ? 'Сіздің таңдауыңыз:' : 'Ваш выбор:'} 
                                        ${result.question.options[result.userAnswer] ? `${String.fromCharCode(65 + parseInt(result.userAnswer))}. ${result.question.options[result.userAnswer]}` : result.userAnswer}
                                    </p>
                                ` : `
                                    <p class="text-zinc-300 text-sm mb-2">
                                        ${this.userProfile.language === 'kk' ? 'Сіздің жауабыңыз:' : 'Ваш ответ:'} ${result.userAnswer}
                                    </p>
                                `}
                                ${result.result.feedback ? `
                                    <p class="text-zinc-400 text-sm mb-1">${result.result.feedback}</p>
                                ` : ''}
                                ${result.result.explanation ? `
                                    <p class="text-blue-300 text-sm">${result.result.explanation}</p>
                                ` : ''}
                                ${result.result.score !== undefined ? `
                                    <div class="mt-2">
                                        <div class="flex justify-between text-xs mb-1">
                                            <span class="text-zinc-500">${this.userProfile.language === 'kk' ? 'Ұпай:' : 'Баллы:'}</span>
                                            <span class="text-gold-400">${result.result.score}/100</span>
                                        </div>
                                        <div class="h-2 bg-zinc-800 rounded-full overflow-hidden">
                                            <div class="h-full bg-gradient-to-r from-gold-500 to-gold-400 rounded-full transition-all" 
                                                style="width: ${result.result.score}%"></div>
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="mt-6 text-center">
                <button onclick="openCharacterSelection()"
                    class="px-6 py-3 bg-gold-500 hover:bg-gold-600 text-black rounded-lg font-medium transition-colors">
                    ${this.userProfile.language === 'kk' ? 'Келесі миссия' : 'Следующая миссия'}
                </button>
            </div>
        `;
        
        // Hide answer form
        const answerForm = document.getElementById('answer-form');
        if (answerForm) {
            answerForm.style.display = 'none';
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
// DISABLED: Using new mission system instead
// Старая система использовала /api/mission/personalized которая больше не нужна
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         window.gameIntegration = new GameIntegration();
//     });
// } else {
//     window.gameIntegration = new GameIntegration();
// }
