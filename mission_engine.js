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
    this.missionRule = null;
  }

  /**
   * Start a new mission
   */
  async startMission(character, playerLevel, completedMissions = 0, weakAreas = []) {
    this.missionCharacter = character;
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

    // Load first scenario
    await this.nextScenario(playerLevel, completedMissions, weakAreas);

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
      // Generate scenario using MissionGenerator
      const scenario = await window.MissionGenerator.generateScenario({
        character: this.missionCharacter,
        level: playerLevel,
        scenarioNumber: this.scenarioNumber,
        totalScenarios: this.totalScenarios,
        previousAnswers: this.getPreviousAnswers(),
        rule: this.missionRule,
        completedMissions: completedMissions,
        weakAreas: weakAreas
      });

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
  async processAnswer(selectedAnswerId, playerLevel, completedMissions = 0, weakAreas = []) {
    if (!this.currentScenario) return null;

    const isCorrect = selectedAnswerId === this.currentScenario.correctAnswer;

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

    // Load next scenario if available
    await this.nextScenario(playerLevel, completedMissions, weakAreas);

    return { ...result, missionEnded: false, nextScenario: this.currentScenario };
  }

  /**
   * End mission and calculate rewards
   */
  endMission() {
    const timeSpent = Math.floor((Date.now() - this.startTime) / 1000);
    const xpEarned = window.MissionGenerator.calculateXP(
      this.scenarioNumber,
      this.correctAnswers,
      this.totalScenarios,
      timeSpent
    );

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
