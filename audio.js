/**
 * Audio Manager for BATYR BOL Game
 * Управляет звуками игровых событий и фоновой музыкой
 */

class AudioManager {
  constructor() {
    this.sounds = {};
    this.backgroundMusic = null;
    this.musicVolume = 0.3; // 30% громкости для музыки
    this.soundVolume = 0.6; // 60% громкости для эффектов
    this.isMusicEnabled = true;
    this.isSoundEnabled = true;

    this.initializeAudio();
  }

  initializeAudio() {
    // Инициализируем звуки игровых событий
    this.sounds = {
      // Звуки действий
      buttonClick: this.createAudio('assets/sounds/click.mp3', this.soundVolume),
      success: this.createAudio('assets/sounds/success.mp3', this.soundVolume),
      error: this.createAudio('assets/sounds/error.mp3', this.soundVolume),
      correct: this.createAudio('assets/sounds/correct-answer.mp3', this.soundVolume),
      incorrect: this.createAudio('assets/sounds/incorrect-answer.mp3', this.soundVolume),

      // Звуки переходов
      levelComplete: this.createAudio('assets/sounds/level-complete.mp3', this.soundVolume),
      gameOver: this.createAudio('assets/sounds/game-over.mp3', this.soundVolume),

      // Звуки наград
      xpGain: this.createAudio('assets/sounds/xp-gain.mp3', this.soundVolume),
      medalWin: this.createAudio('assets/sounds/medal-win.mp3', this.soundVolume),

      // Звуки интерфейса
      uiOpen: this.createAudio('assets/sounds/ui-open.mp3', this.soundVolume * 0.7),
      uiClose: this.createAudio('assets/sounds/ui-close.mp3', this.soundVolume * 0.7),
    };

    // Инициализируем фоновую музыку в казахском стиле
    this.backgroundMusic = this.createAudio('assets/music/background-kazakh.mp3', this.musicVolume);
    if (this.backgroundMusic) {
      this.backgroundMusic.loop = true;
    }

    // Загружаем настройки из localStorage
    this.loadSettings();
  }

  createAudio(src, volume = 1) {
    try {
      const audio = new Audio();
      audio.src = src;
      audio.volume = volume;
      audio.preload = 'auto';
      return audio;
    } catch (error) {
      console.warn(`⚠️ Не удалось загрузить аудио: ${src}`);
      return null;
    }
  }

  /**
   * Воспроизводит фоновую музыку
   */
  playBackgroundMusic() {
    if (!this.isMusicEnabled || !this.backgroundMusic) return;

    try {
      // Останавливаем текущую музыку если играет
      if (this.backgroundMusic && !this.backgroundMusic.paused) {
        this.backgroundMusic.pause();
      }

      this.backgroundMusic.currentTime = 0;
      const playPromise = this.backgroundMusic.play();

      if (playPromise !== undefined) {
        playPromise.catch(error => {
          console.log('🔇 Автозапуск музыки заблокирован браузером:', error);
          // Музыка начнёт играть при первом взаимодействии пользователя
        });
      }
    } catch (error) {
      console.warn('❌ Ошибка при воспроизведении музыки:', error);
    }
  }

  /**
   * Останавливает фоновую музыку
   */
  stopBackgroundMusic() {
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
      this.backgroundMusic.currentTime = 0;
    }
  }

  /**
   * Включает/выключает фоновую музыку
   */
  toggleBackgroundMusic(enabled) {
    this.isMusicEnabled = enabled;
    if (enabled) {
      this.playBackgroundMusic();
    } else {
      this.stopBackgroundMusic();
    }
    this.saveSettings();
  }

  /**
   * Включает/выключает звуки эффектов
   */
  toggleSounds(enabled) {
    this.isSoundEnabled = enabled;
    this.saveSettings();
  }

  /**
   * Воспроизводит звук события
   */
  playSound(soundName) {
    if (!this.isSoundEnabled || !this.sounds[soundName]) {
      return;
    }

    try {
      const sound = this.sounds[soundName];
      if (sound) {
        sound.currentTime = 0;
        const playPromise = sound.play();

        if (playPromise !== undefined) {
          playPromise.catch(error => {
            console.log(`🔇 Звук ${soundName} заблокирован:`, error);
          });
        }
      }
    } catch (error) {
      console.warn(`❌ Ошибка при воспроизведении звука ${soundName}:`, error);
    }
  }

  /**
   * Воспроизводит звук правильного ответа
   */
  playCorrectAnswer() {
    this.playSound('correct');
  }

  /**
   * Воспроизводит звук неправильного ответа
   */
  playIncorrectAnswer() {
    this.playSound('incorrect');
  }

  /**
   * Воспроизводит звук клика кнопки
   */
  playButtonClick() {
    this.playSound('buttonClick');
  }

  /**
   * Воспроизводит звук успеха
   */
  playSuccess() {
    this.playSound('success');
  }

  /**
   * Воспроизводит звук ошибки
   */
  playError() {
    this.playSound('error');
  }

  /**
   * Воспроизводит звук завершения уровня
   */
  playLevelComplete() {
    this.playSound('levelComplete');
  }

  /**
   * Воспроизводит звук конца игры
   */
  playGameOver() {
    this.playSound('gameOver');
  }

  /**
   * Воспроизводит звук получения опыта
   */
  playXpGain() {
    this.playSound('xpGain');
  }

  /**
   * Воспроизводит звук получения медали
   */
  playMedalWin() {
    this.playSound('medalWin');
  }

  /**
   * Воспроизводит звук открытия UI
   */
  playUIOpen() {
    this.playSound('uiOpen');
  }

  /**
   * Воспроизводит звук закрытия UI
   */
  playUIClose() {
    this.playSound('uiClose');
  }

  /**
   * Устанавливает громкость музыки (0-1)
   */
  setMusicVolume(volume) {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    if (this.backgroundMusic) {
      this.backgroundMusic.volume = this.musicVolume;
    }
    this.saveSettings();
  }

  /**
   * Устанавливает громкость звуков (0-1)
   */
  setSoundVolume(volume) {
    this.soundVolume = Math.max(0, Math.min(1, volume));
    Object.values(this.sounds).forEach(sound => {
      if (sound) sound.volume = this.soundVolume;
    });
    this.saveSettings();
  }

  /**
   * Сохраняет настройки в localStorage
   */
  saveSettings() {
    const settings = {
      musicEnabled: this.isMusicEnabled,
      soundEnabled: this.isSoundEnabled,
      musicVolume: this.musicVolume,
      soundVolume: this.soundVolume,
    };
    localStorage.setItem('batyrbol_audio_settings', JSON.stringify(settings));
  }

  /**
   * Загружает настройки из localStorage
   */
  loadSettings() {
    try {
      const saved = localStorage.getItem('batyrbol_audio_settings');
      if (saved) {
        const settings = JSON.parse(saved);
        this.isMusicEnabled = settings.musicEnabled !== false;
        this.isSoundEnabled = settings.soundEnabled !== false;
        this.musicVolume = settings.musicVolume || 0.3;
        this.soundVolume = settings.soundVolume || 0.6;

        if (this.backgroundMusic) {
          this.backgroundMusic.volume = this.musicVolume;
        }
      }
    } catch (error) {
      console.warn('❌ Ошибка при загрузке аудио настроек:', error);
    }
  }

  /**
   * Сбрасывает все звуки (используется при смене страниц)
   */
  stopAll() {
    this.stopBackgroundMusic();
    Object.values(this.sounds).forEach(sound => {
      if (sound) {
        sound.pause();
        sound.currentTime = 0;
      }
    });
  }
}

// Глобальный экземпляр AudioManager
window.audioManager = new AudioManager();

console.log('✅ AudioManager инициализирован');
