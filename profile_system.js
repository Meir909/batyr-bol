/**
 * Profile System - Управление прогрессом, уровнями, достижениями
 */

class ProfileSystem {
  constructor() {
    this.levels = {
      1: { title: 'Жасөспірім', titleRu: 'Новичок', xpRequired: 0 },
      2: { title: 'Оқушы', titleRu: 'Ученик', xpRequired: 100 },
      3: { title: 'Батыр', titleRu: 'Герой', xpRequired: 300 },
      4: { title: 'Жауынгер', titleRu: 'Воин', xpRequired: 600 },
      5: { title: 'Қолбасшы', titleRu: 'Командир', xpRequired: 1000 },
      6: { title: 'Би', titleRu: 'Судья', xpRequired: 1500 },
      7: { title: 'Хан', titleRu: 'Хан', xpRequired: 2100 },
      8: { title: 'Данышпан', titleRu: 'Мудрец', xpRequired: 2800 },
      9: { title: 'Бекзат', titleRu: 'Аристократ', xpRequired: 3600 },
      10: { title: 'Ұлы батыр', titleRu: 'Великий герой', xpRequired: 4500 }
    };

    this.achievements = [
      {
        id: 'first_mission',
        icon: '🏅',
        titleKz: 'Бірінші батыр',
        titleRu: 'Первый батыр',
        description: 'Пройти первую миссию',
        condition: (stats) => stats.completedMissions >= 1
      },
      {
        id: 'perfect_series',
        icon: '🔥',
        titleKz: 'Қатарынан 5 міндеттеме',
        titleRu: '5 миссий подряд',
        description: 'Пройти 5 миссий подряд без потери всех жизней',
        condition: (stats) => stats.maxConsecutiveWins >= 5
      },
      {
        id: 'historian',
        icon: '📚',
        titleKz: 'Тарихшы',
        titleRu: 'Историк',
        description: 'Пройти миссии всех 3 персонажей',
        condition: (stats) => {
          const progress = stats.characterProgress || {};
          return Object.keys(progress).length >= 3 &&
            Object.values(progress).every(p => p.missionsCompleted > 0);
        }
      },
      {
        id: 'level_5_master',
        icon: '⭐',
        titleKz: '5-ші деңгей үстемі',
        titleRu: 'Мастер 5-го уровня',
        description: 'Достичь 5-го уровня',
        condition: (stats) => stats.level >= 5
      },
      {
        id: 'speed_runner',
        icon: '⚡',
        titleKz: 'Жылдам батыр',
        titleRu: 'Быстрый батыр',
        description: 'Завершить миссию менее чем за 3 минуты',
        condition: (stats) => stats.fastestMissionTime <= 180 // seconds
      }
    ];
  }

  /**
   * Load user profile from localStorage
   */
  loadProfile() {
    const saved = localStorage.getItem('batyrbol_user');
    if (!saved) {
      return this.createNewProfile();
    }
    return JSON.parse(saved);
  }

  /**
   * Create new profile for new player
   */
  createNewProfile(name = 'Батыр', email = '') {
    return {
      id: this.generateId(),
      name: name,
      email: email,
      level: 1,
      xp: 0,
      totalXP: 0,
      completedMissions: 0,
      clanName: null,
      lastActive: new Date().toISOString(),
      characterProgress: {
        'Абылай хан': { missionsCompleted: 0, totalXP: 0, successRate: 0, lastMissionDate: null },
        'Абай Кунанбаев': { missionsCompleted: 0, totalXP: 0, successRate: 0, lastMissionDate: null },
        'Айтеке би': { missionsCompleted: 0, totalXP: 0, successRate: 0, lastMissionDate: null }
      },
      analytics: {
        weakAreas: [],
        strongAreas: [],
        averageTimePerMission: 0,
        totalPlayTime: 0,
        maxConsecutiveWins: 0,
        fastestMissionTime: 999999
      },
      achievements: []
    };
  }

  /**
   * Add XP to player and check for level up
   */
  addXP(profile, xpAmount) {
    const oldLevel = profile.level;
    profile.xp += xpAmount;
    profile.totalXP += xpAmount;

    // Check for level up
    while (profile.level < 10 && profile.xp >= this.levels[profile.level + 1].xpRequired) {
      profile.xp -= this.levels[profile.level + 1].xpRequired;
      profile.level++;
    }

    this.saveProfile(profile);

    return {
      xpGained: xpAmount,
      leveledUp: oldLevel < profile.level,
      newLevel: profile.level,
      currentLevelXP: profile.xp,
      nextLevelXP: this.levels[profile.level + 1]?.xpRequired || 999999
    };
  }

  /**
   * Update character progress after mission
   */
  updateCharacterProgress(profile, character, missionResult) {
    if (!profile.characterProgress[character]) {
      profile.characterProgress[character] = {
        missionsCompleted: 0,
        totalXP: 0,
        successRate: 0,
        lastMissionDate: null
      };
    }

    const charProg = profile.characterProgress[character];
    charProg.missionsCompleted++;
    charProg.totalXP += missionResult.xpEarned;
    charProg.lastMissionDate = missionResult.finishedAt;

    // Calculate success rate
    if (!charProg.totalAttempts) charProg.totalAttempts = 0;
    if (!charProg.successfulAttempts) charProg.successfulAttempts = 0;

    charProg.totalAttempts++;
    if (missionResult.success) {
      charProg.successfulAttempts++;
    }
    charProg.successRate = (charProg.successfulAttempts / charProg.totalAttempts * 100).toFixed(1);

    profile.completedMissions++;
    profile.lastActive = new Date().toISOString();

    this.saveProfile(profile);
  }

  /**
   * Update analytics based on mission result
   */
  updateAnalytics(profile, missionResult, timeSpent) {
    const analytics = profile.analytics;

    // Update timing
    if (!analytics.averageTimePerMission) {
      analytics.averageTimePerMission = timeSpent;
    } else {
      analytics.averageTimePerMission = Math.round(
        (analytics.averageTimePerMission + timeSpent) / 2
      );
    }

    // Track fastest mission
    if (timeSpent < (analytics.fastestMissionTime || 999999)) {
      analytics.fastestMissionTime = timeSpent;
    }

    // Update total play time
    analytics.totalPlayTime += timeSpent;

    // Identify weak areas (where success rate is below 70%)
    const charProg = profile.characterProgress[missionResult.character];
    if (charProg.successRate < 70) {
      const weakArea = missionResult.character;
      if (!analytics.weakAreas.includes(weakArea)) {
        analytics.weakAreas.push(weakArea);
      }
    }

    // Identify strong areas
    if (charProg.successRate >= 80) {
      const strongArea = missionResult.character;
      if (!analytics.strongAreas.includes(strongArea)) {
        analytics.strongAreas.push(strongArea);
      }
    }

    this.saveProfile(profile);
  }

  /**
   * Check and unlock achievements
   */
  checkAchievements(profile) {
    const unlockedAchievements = [];

    for (const achievement of this.achievements) {
      // Check if already unlocked
      const isUnlocked = profile.achievements.some(a => a.id === achievement.id);
      if (isUnlocked) continue;

      // Check if condition is met
      if (achievement.condition(profile)) {
        profile.achievements.push({
          id: achievement.id,
          unlockedAt: new Date().toISOString()
        });
        unlockedAchievements.push(achievement);
      }
    }

    if (unlockedAchievements.length > 0) {
      this.saveProfile(profile);
    }

    return unlockedAchievements;
  }

  /**
   * Save profile to localStorage
   */
  saveProfile(profile) {
    localStorage.setItem('batyrbol_user', JSON.stringify(profile));
  }

  /**
   * Get level title in selected language
   */
  getLevelTitle(level, language = 'kk') {
    const levelData = this.levels[level];
    return language === 'kk' ? levelData.title : levelData.titleRu;
  }

  /**
   * Get achievement by ID
   */
  getAchievement(id) {
    return this.achievements.find(a => a.id === id);
  }

  /**
   * Get all achievements with unlock status
   */
  getAllAchievements(profile) {
    return this.achievements.map(achievement => {
      const unlocked = profile.achievements.some(a => a.id === achievement.id);
      return {
        ...achievement,
        unlocked,
        unlockedAt: profile.achievements.find(a => a.id === achievement.id)?.unlockedAt || null
      };
    });
  }

  /**
   * Generate unique ID
   */
  generateId() {
    return 'user_' + Math.random().toString(36).substr(2, 9);
  }
}

// Export for use
window.ProfileSystem = new ProfileSystem();
