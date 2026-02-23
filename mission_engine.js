/**
 * Mission Engine - Главная логика системы миссий
 * Управляет сценариями, жизнями, XP и прогрессом
 */

class MissionEngine {
  constructor() {
    this.currentMission = null;
    this.currentScenario = null;
    this.scenarioNumber = 0;
    this.totalScenarios = 6;
    this.lives = 3;
    this.maxLives = 3;
    this.correctAnswers = 0;
    this.startTime = null;
    this.scenarios = [];
    this.missionCharacter = null;
    this.playerLevel = 1;  // Default player level
    this.missionRule = null;
  }

  /**
   * Start a new mission
   */
  async startMission(character, playerLevel, completedMissions = 0, weakAreas = []) {
    this.missionCharacter = character;
    this.playerLevel = playerLevel;  // Save player level for later use
    this.scenarioNumber = 0;
    this.lives = this.maxLives;
    this.correctAnswers = 0;
    this.scenarios = [];
    this.startTime = Date.now();

    // Get rule for character
    const rules = {
      'Абылай хан': 'Помочь народу выиграть на войне и масштабировать территорию',
      'Абай Кунанбаев': 'Учить детей писать стихи, создавать произведения, развивать образование',
      'Айтеке би': 'Справедливо судить, решать конфликты, поддерживать мир'
    };
    this.missionRule = rules[character];

    // Note: First scenario will be loaded by igra.html via loadNextScenario()
    // Don't load here to avoid issues with MissionGenerator initialization

    return this.currentScenario;
  }

  /**
   * Load next scenario
   */
  async nextScenario(playerLevel, completedMissions = 0, weakAreas = []) {
    if (this.scenarioNumber >= this.totalScenarios) {
      return this.endMission();
    }

    this.scenarioNumber++;

    try {
      // Generate scenario using MissionGenerator instance from igra.html
      if (!window.missionGenerator) {
        throw new Error('MissionGenerator not initialized');
      }

      const scenario = await window.missionGenerator.generateScenario(
        this.missionCharacter,
        this.scenarioNumber,
        playerLevel,
        'ru'  // Language will be handled by igra.html
      );

      this.currentScenario = scenario;
      this.scenarios.push(scenario);

      return scenario;
    } catch (error) {
      console.error('Error loading scenario:', error);
      return null;
    }
  }

  /**
   * Process player answer
   */
  async processAnswer(optionIndex, isCorrect) {
    if (!this.currentScenario) return null;

    // Update stats
    if (isCorrect) {
      this.correctAnswers++;
      // Restore a life if it was lost
      if (this.lives < this.maxLives) {
        this.lives++;
      }
    } else {
      this.lives--;
    }

    // Prepare result
    const result = {
      isCorrect,
      lives: this.lives,
      correctAnswer: this.currentScenario.correctAnswer,
      consequence: isCorrect
        ? this.currentScenario.correctConsequence
        : this.currentScenario.wrongConsequence,
      historicalContext: this.currentScenario.historicalContext,
      nextScenarioSetup: this.currentScenario.nextScenarioSetup
    };

    // Check if mission ends
    if (this.lives <= 0) {
      return { ...result, missionEnded: true, missionSuccess: false };
    }

    // Check if all scenarios completed
    if (this.scenarioNumber >= this.totalScenarios) {
      return { ...result, missionEnded: true, missionSuccess: true };
    }

    // Note: Next scenario will be loaded by igra.html via loadNextScenario()
    return { ...result, missionEnded: false };
  }

  /**
   * End mission and calculate rewards
   */
  endMission() {
    const timeSpent = Math.floor((Date.now() - this.startTime) / 1000);

    // Calculate XP: base 100 XP per correct answer, time bonus, life bonus
    const baseXP = this.correctAnswers * 100;
    const timeBonus = Math.max(0, 300 - timeSpent) > 0 ? 50 : 0;  // 50 XP bonus if done under 5 min
    const lifeBonus = (this.lives / this.maxLives) * 50;  // Bonus for remaining lives
    const xpEarned = Math.floor(baseXP + timeBonus + lifeBonus);

    const success = this.lives > 0;

    return {
      missionEnded: true,
      success,
      scenariosCompleted: this.scenarioNumber,
      totalScenarios: this.totalScenarios,
      correctAnswers: this.correctAnswers,
      totalQuestions: this.scenarioNumber,
      timeSpent: timeSpent,
      successRate: (this.correctAnswers / this.scenarioNumber * 100).toFixed(1),
      xpEarned: xpEarned,
      character: this.missionCharacter,
      finishedAt: new Date().toISOString()
    };
  }

  /**
   * Get previous answers for context
   */
  getPreviousAnswers() {
    return this.scenarios
      .slice(0, this.scenarioNumber - 1)
      .map((s, i) => `Q${i + 1}: ${s.selectedAnswer || '?'}`);
  }

  /**
   * Get mission status
   */
  getStatus() {
    return {
      character: this.missionCharacter,
      scenarioNumber: this.scenarioNumber,
      totalScenarios: this.totalScenarios,
      lives: this.lives,
      maxLives: this.maxLives,
      correctAnswers: this.correctAnswers,
      currentScenario: this.currentScenario
    };
  }

  /**
   * Format time spent
   */
  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
}

// Export for use
window.MissionEngine = new MissionEngine();
