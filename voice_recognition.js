/**
 * BATYR BOL - Voice Recognition Module
 * Распознавание голоса и речи для игры
 */

class VoiceRecognition {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.language = 'ru-RU'; // Default Russian, can switch to 'kk-KZ'
        this.onResultCallback = null;
        this.onErrorCallback = null;
        
        this.init();
    }
    
    init() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn('Speech Recognition not supported in this browser');
            return false;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = this.language;
        
        this.recognition.onresult = (event) => {
            const result = event.results[event.results.length - 1];
            const transcript = result[0].transcript;
            const isFinal = result.isFinal;
            
            if (this.onResultCallback) {
                this.onResultCallback(transcript, isFinal);
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            
            if (this.onErrorCallback) {
                this.onErrorCallback(event.error);
            }
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
        };
        
        return true;
    }
    
    setLanguage(lang) {
        // 'kk' for Kazakh, 'ru' for Russian
        if (lang === 'kk') {
            this.language = 'kk-KZ';
        } else {
            this.language = 'ru-RU';
        }
        
        if (this.recognition) {
            this.recognition.lang = this.language;
        }
    }
    
    startListening(onResult, onError) {
        if (!this.recognition) {
            if (onError) onError('not_supported');
            return false;
        }
        
        if (this.isListening) {
            return false;
        }
        
        this.onResultCallback = onResult;
        this.onErrorCallback = onError;
        this.isListening = true;
        
        try {
            this.recognition.start();
            return true;
        } catch (e) {
            console.error('Failed to start recognition:', e);
            this.isListening = false;
            return false;
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }
    
    speak(text, lang = null) {
        if (!this.synthesis) {
            console.warn('Speech synthesis not supported');
            return false;
        }
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || this.language;
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        this.synthesis.speak(utterance);
        return true;
    }
    
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }
    
    isSupported() {
        return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    }
    
    isSpeechSupported() {
        return !!window.speechSynthesis;
    }
}

// Voice Answer Checker - проверка устных ответов
class VoiceAnswerChecker {
    constructor(voiceRecognition) {
        this.voice = voiceRecognition;
        this.currentQuestion = null;
        this.correctAnswer = null;
        this.attempts = 0;
        this.maxAttempts = 3;
    }
    
    setQuestion(question, correctAnswer) {
        this.currentQuestion = question;
        this.correctAnswer = correctAnswer.toLowerCase().trim();
        this.attempts = 0;
    }
    
    checkAnswer(spokenText) {
        if (!this.correctAnswer) return { correct: false, similarity: 0 };
        
        const spoken = spokenText.toLowerCase().trim();
        const correct = this.correctAnswer;
        
        // Exact match
        if (spoken === correct) {
            return { correct: true, similarity: 1.0 };
        }
        
        // Contains match
        if (spoken.includes(correct) || correct.includes(spoken)) {
            return { correct: true, similarity: 0.8 };
        }
        
        // Similarity check (Levenshtein-based)
        const similarity = this.calculateSimilarity(spoken, correct);
        
        return {
            correct: similarity > 0.7,
            similarity: similarity
        };
    }
    
    calculateSimilarity(str1, str2) {
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) return 1.0;
        
        const editDistance = this.levenshteinDistance(longer, shorter);
        return (longer.length - editDistance) / longer.length;
    }
    
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
}

// UI Component for Voice Input
class VoiceInputUI {
    constructor(containerId, voiceRecognition) {
        this.container = document.getElementById(containerId);
        this.voice = voiceRecognition;
        this.answerChecker = new VoiceAnswerChecker(voiceRecognition);
        this.onAnswerCallback = null;
    }
    
    render() {
        if (!this.container) return;
        
        const isSupported = this.voice.isSupported();
        
        this.container.innerHTML = `
            <div class="voice-input-wrapper p-4 bg-zinc-900/50 rounded-xl border border-white/10">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm text-zinc-400">
                        <span class="lang-ru">Голосовой ответ</span>
                        <span class="lang-kz">Дауыспен жауап</span>
                    </span>
                    ${isSupported ? '' : '<span class="text-xs text-red-400">Не поддерживается</span>'}
                </div>
                
                <div class="flex items-center gap-3">
                    <button id="voice-btn" class="w-14 h-14 rounded-full ${isSupported ? 'bg-gold-500 hover:bg-gold-400' : 'bg-zinc-700 cursor-not-allowed'} flex items-center justify-center transition-all" ${isSupported ? '' : 'disabled'}>
                        <svg id="mic-icon" class="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        </svg>
                        <svg id="mic-listening" class="w-6 h-6 text-black hidden animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10"/>
                        </svg>
                    </button>
                    
                    <div class="flex-1">
                        <div id="voice-transcript" class="text-white min-h-[40px] p-2 bg-zinc-800/50 rounded-lg text-sm">
                            <span class="text-zinc-500">
                                <span class="lang-ru">Нажмите на микрофон и говорите...</span>
                                <span class="lang-kz">Микрофонды басып, сөйлеңіз...</span>
                            </span>
                        </div>
                    </div>
                </div>
                
                <div id="voice-feedback" class="mt-3 hidden">
                    <div class="text-sm p-2 rounded-lg"></div>
                </div>
            </div>
        `;
        
        this.attachEvents();
    }
    
    attachEvents() {
        const btn = document.getElementById('voice-btn');
        if (!btn) return;
        
        btn.addEventListener('click', () => {
            if (this.voice.isListening) {
                this.stopListening();
            } else {
                this.startListening();
            }
        });
    }
    
    startListening() {
        const btn = document.getElementById('voice-btn');
        const micIcon = document.getElementById('mic-icon');
        const micListening = document.getElementById('mic-listening');
        const transcript = document.getElementById('voice-transcript');
        
        btn.classList.add('ring-4', 'ring-gold-500/50');
        micIcon.classList.add('hidden');
        micListening.classList.remove('hidden');
        
        transcript.innerHTML = '<span class="text-gold-400 animate-pulse">Слушаю...</span>';
        
        this.voice.startListening(
            (text, isFinal) => {
                transcript.innerHTML = `<span class="${isFinal ? 'text-white' : 'text-zinc-400'}">${text}</span>`;
                
                if (isFinal && this.onAnswerCallback) {
                    this.onAnswerCallback(text);
                }
            },
            (error) => {
                this.showFeedback('error', 'Ошибка распознавания: ' + error);
                this.stopListening();
            }
        );
    }
    
    stopListening() {
        const btn = document.getElementById('voice-btn');
        const micIcon = document.getElementById('mic-icon');
        const micListening = document.getElementById('mic-listening');
        
        btn.classList.remove('ring-4', 'ring-gold-500/50');
        micIcon.classList.remove('hidden');
        micListening.classList.add('hidden');
        
        this.voice.stopListening();
    }
    
    showFeedback(type, message) {
        const feedback = document.getElementById('voice-feedback');
        if (!feedback) return;
        
        const inner = feedback.querySelector('div');
        feedback.classList.remove('hidden');
        
        if (type === 'success') {
            inner.className = 'text-sm p-2 rounded-lg bg-green-500/20 text-green-400';
        } else if (type === 'error') {
            inner.className = 'text-sm p-2 rounded-lg bg-red-500/20 text-red-400';
        } else {
            inner.className = 'text-sm p-2 rounded-lg bg-zinc-500/20 text-zinc-400';
        }
        
        inner.textContent = message;
    }
    
    setOnAnswer(callback) {
        this.onAnswerCallback = callback;
    }
    
    checkVoiceAnswer(spokenText, correctAnswer) {
        this.answerChecker.setQuestion('', correctAnswer);
        const result = this.answerChecker.checkAnswer(spokenText);
        
        if (result.correct) {
            this.showFeedback('success', `Правильно! (${Math.round(result.similarity * 100)}% совпадение)`);
        } else {
            this.showFeedback('error', `Попробуйте ещё раз (${Math.round(result.similarity * 100)}% совпадение)`);
        }
        
        return result;
    }
}

// Global instance
let voiceRecognition = null;
let voiceInputUI = null;

function initVoiceRecognition(containerId = 'voice-input-container') {
    voiceRecognition = new VoiceRecognition();
    
    if (containerId && document.getElementById(containerId)) {
        voiceInputUI = new VoiceInputUI(containerId, voiceRecognition);
        voiceInputUI.render();
    }
    
    return { voiceRecognition, voiceInputUI };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VoiceRecognition, VoiceAnswerChecker, VoiceInputUI, initVoiceRecognition };
}
