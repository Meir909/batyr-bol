// Authentication Manager
class AuthManager {
    constructor() {
        this.sessionId = localStorage.getItem('batyrbol_session_id') || null;
        this.currentUser = null;
        this.checkInterval = null;
        this.init();
    }

    init() {
        // Check session on initialization
        this.checkSession();
        
        // Set up periodic session validation (every 5 minutes)
        this.checkInterval = setInterval(() => {
            this.checkSession();
        }, 5 * 60 * 1000);
    }

    async checkSession() {
        if (!this.sessionId) {
            this.redirectToLanding();
            return;
        }

        try {
            const response = await fetch('/api/check-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.valid) {
                this.currentUser = data.user;
                this.updateUI();
                
                // If we're on landing page, redirect to game
                if (window.location.pathname === '/' || window.location.pathname.endsWith('intro.html')) {
                    window.location.href = '/game';
                }
            } else {
                this.showSessionExpiredModal();
            }
        } catch (error) {
            console.error('Session check failed:', error);
            this.redirectToLanding();
        }
    }

    async login(email, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (data.success) {
                this.sessionId = data.session_id;
                this.currentUser = data.user;
                
                // Save session to localStorage
                localStorage.setItem('batyrbol_session_id', this.sessionId);
                localStorage.setItem('batyrbol_user', JSON.stringify(data.user));
                
                this.updateUI();
                
                // Redirect to game
                window.location.href = '/game';
                
                return { success: true };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('Login failed:', error);
            return { success: false, message: 'Ошибка подключения к серверу' };
        }
    }

    async logout() {
        if (!this.sessionId) {
            this.redirectToLanding();
            return;
        }

        try {
            await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
        } catch (error) {
            console.error('Logout error:', error);
        }

        // Clear local storage
        localStorage.removeItem('batyrbol_session_id');
        localStorage.removeItem('batyrbol_user');
        
        this.sessionId = null;
        this.currentUser = null;
        
        // Clear interval
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
        
        this.redirectToLanding();
    }

    showSessionExpiredModal() {
        // Create modal
        const modal = document.createElement('div');
        modal.id = 'session-expired-modal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4';
        modal.innerHTML = `
            <div class="glass rounded-2xl max-w-md w-full p-6">
                <div class="text-center">
                    <div class="text-6xl mb-4">⏰</div>
                    <h2 class="text-2xl font-bold text-white mb-2">
                        <span class="lang-ru">Время сессии истекло</span>
                        <span class="lang-kz">Сессия уақыты аяқталды</span>
                    </h2>
                    <p class="text-zinc-400 mb-6">
                        <span class="lang-ru">Пожалуйста, войдите снова для продолжения</span>
                        <span class="lang-kz">Жалғастыру үшін қайта кіріңіз</span>
                    </p>
                    
                    <div class="space-y-3">
                        <button onclick="authManager.redirectToLogin()" class="w-full py-3 bg-gold-500 hover:bg-gold-600 text-black font-semibold rounded-xl transition-colors">
                            <span class="lang-ru">Войти снова</span>
                            <span class="lang-kz">Қайта кіру</span>
                        </button>
                        <button onclick="authManager.redirectToLanding()" class="w-full py-3 border border-zinc-600 text-zinc-300 font-medium rounded-xl hover:bg-zinc-800 transition-colors">
                            <span class="lang-ru">На главную</span>
                            <span class="lang-kz">Басты бет</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    redirectToLogin() {
        // Remove modal
        const modal = document.getElementById('session-expired-modal');
        if (modal) {
            modal.remove();
        }
        
        // Redirect to landing with login form
        window.location.href = '/#login';
    }

    redirectToLanding() {
        // Clear session data
        localStorage.removeItem('batyrbol_session_id');
        localStorage.removeItem('batyrbol_user');
        
        // Redirect to landing page
        if (window.location.pathname !== '/' && !window.location.pathname.endsWith('intro.html')) {
            window.location.href = '/';
        }
    }

    updateUI() {
        if (!this.currentUser) return;

        // Update user info in UI
        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('profile-email');
        const userLevel = document.getElementById('user-level');
        const userXP = document.getElementById('user-xp');
        const headerXP = document.getElementById('header-xp');
        const headerStreak = document.getElementById('header-streak');
        const userStreak = document.getElementById('stat-streak');
        const userMissions = document.getElementById('stat-missions');
        const userCorrect = document.getElementById('stat-correct');

        if (userName) userName.textContent = this.currentUser.name || 'Батыр';
        if (userEmail) userEmail.value = this.currentUser.email;
        if (userLevel) userLevel.textContent = this.currentUser.level || 1;
        if (userXP) userXP.textContent = this.currentUser.xp || 0;
        if (headerXP) headerXP.textContent = this.currentUser.xp || 0;
        if (headerStreak) headerStreak.textContent = this.currentUser.streak || 0;
        if (userStreak) userStreak.textContent = this.currentUser.streak || 0;
        if (userMissions) userMissions.textContent = (this.currentUser.completedMissions || []).length;
        if (userCorrect) userCorrect.textContent = this.currentUser.correctAnswers || 0;
    }

    getSessionId() {
        return this.sessionId;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isAuthenticated() {
        return this.sessionId && this.currentUser;
    }
}

// Global instance
window.authManager = new AuthManager();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}
