/**
 * Mission Generator - AI-powered mission generation system
 * Generates personalized missions based on player level, weak areas, and character
 */

class MissionGenerator {
  constructor() {
    this.apiBase = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';
    this.model = 'gpt-4o-mini';
  }

  /**
   * Generate a single scenario for a mission
   * @param {Object} config - Configuration object
   * @returns {Promise<Object>} - Single scenario data
   */
  async generateScenario(config) {
    const {
      character,
      level = 1,
      scenarioNumber = 1,
      prompt,
      language = 'kk'
    } = config;

    try {
      const response = await fetch(`${this.apiBase}/api/mission/generate-scenario`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          character,
          level,
          scenarioNumber,
          prompt,
          language
        })
      });

      const data = await response.json();

      if (data.success) {
        return {
          success: true,
          scenario: data.scenario,
          fallback: data.fallback || false
        };
      } else {
        return {
          success: false,
          error: data.message || 'Failed to generate scenario'
        };
      }
    } catch (error) {
      console.error('Mission generation error:', error);
      return {
        success: false,
        error: error.message || 'Network error'
      };
    }
  }

  /**
   * Generate complete mission with multiple scenarios
   * @param {Object} config - Mission configuration
   * @returns {Promise<Object>} - Complete mission data
   */
  async generateMission(config) {
    const { character, level = 1, scenarioCount = 5, language = 'kk' } = config;
    const scenarios = [];

    for (let i = 1; i <= scenarioCount; i++) {
      const prompt = this._buildScenarioPrompt(character, level, i, language);
      const result = await this.generateScenario({
        character,
        level,
        scenarioNumber: i,
        prompt,
        language
      });

      if (result.success) {
        scenarios.push(result.scenario);
      } else {
        console.error(`Failed to generate scenario ${i}:`, result.error);
        // Use fallback scenario
        scenarios.push(this._getFallbackScenario(character, i, language));
      }
    }

    return {
      success: true,
      mission: {
        character,
        level,
        scenarios,
        totalScenarios: scenarioCount
      }
    };
  }

  /**
   * Build prompt for scenario generation
   * @private
   */
  _buildScenarioPrompt(character, level, scenarioNumber, language) {
    const characterContexts = {
      'Абылай хан': 'великий хан, военный стратег, объединитель казахских земель',
      'Абай': 'великий поэт, философ, просветитель',
      'Айтеке би': 'мудрый бий, справедливый судья, разрешитель конфликтов'
    };

    const context = characterContexts[character] || 'историческая личность';

    return language === 'kk' ? 
      `Создай сценарий для образовательной миссии по истории Казахстана.
      
Персонаж: ${character} (${context})
Уровень сложности: ${level} из 10
Номер сценария: ${scenarioNumber}

Создай интерактивную ситуацию с выбором, где игрок должен принять правильное решение.

Формат ответа (JSON):
{
  "scenario": ${scenarioNumber},
  "text": "Описание ситуации на казахском языке (100-150 слов)",
  "options": [
    {"id": "A", "text": "Вариант ответа А", "isCorrect": false},
    {"id": "B", "text": "Правильный вариант ответа", "isCorrect": true},
    {"id": "C", "text": "Вариант ответа В", "isCorrect": false},
    {"id": "D", "text": "Вариант ответа Г", "isCorrect": false}
  ],
  "correctAnswer": "B",
  "wrongConsequence": "Последствия неправильного выбора на казахском языке",
  "correctConsequence": "Последствия правильного выбора на казахском языке",
  "historicalContext": "Исторический контекст на казахском языке",
  "nextScenarioSetup": "Подготовка к следующему сценарию"
}

Требования:
1. Историческая точность
2. Образовательная ценность
3. Один правильный ответ
4. Понятные последствия выбора
5. Адаптация под уровень сложности` :

      `Create a scenario for an educational mission about Kazakhstan history.
      
Character: ${character} (${context})
Difficulty level: ${level} out of 10
Scenario number: ${scenarioNumber}

Create an interactive decision-making situation.

Response format (JSON):
{
  "scenario": ${scenarioNumber},
  "text": "Situation description in Russian (100-150 words)",
  "options": [
    {"id": "A", "text": "Answer option A", "isCorrect": false},
    {"id": "B", "text": "Correct answer option", "isCorrect": true},
    {"id": "C", "text": "Answer option C", "isCorrect": false},
    {"id": "D", "text": "Answer option D", "isCorrect": false}
  ],
  "correctAnswer": "B",
  "wrongConsequence": "Consequences of wrong choice in Russian",
  "correctConsequence": "Consequences of correct choice in Russian", 
  "historicalContext": "Historical context in Russian",
  "nextScenarioSetup": "Setup for next scenario"
}

Requirements:
1. Historical accuracy
2. Educational value
3. One correct answer
4. Clear consequences
5. Adapted to difficulty level`;
  }

  /**
   * Get fallback scenario when AI generation fails
   * @private
   */
  _getFallbackScenario(character, scenarioNumber, language) {
    const fallbacks = {
      'Абылай хан': [
        {
          scenario: 1,
          text: language === 'kk' ? 'Жоңғар сарбаздары қазақ жерінің шегіне жақындады. Ата-баба қорғау үшін не істеу керек?' : 'Джунгарские войска приблизились к границам. Как защитить земли предков?',
          options: [
            {id: 'A', text: language === 'kk' ? 'Тез атақ жасау' : 'Немедленно атаковать', isCorrect: false},
            {id: 'B', text: language === 'kk' ? 'Үш жүздің барлығын біліктестіру' : 'Объединить три жуза', isCorrect: true},
            {id: 'C', text: language === 'kk' ? 'Түгелтеп іле шығу' : 'Отступить', isCorrect: false},
            {id: 'D', text: language === 'kk' ? 'Орыстарға көмек сұрау' : 'Попросить помощи у русских', isCorrect: false}
          ],
          correctAnswer: 'B',
          wrongConsequence: language === 'kk' ? 'Айдап күрес жеңіліске ұласты. Жоңғарлар қазақ топтарын бөлік-бөлік ұрды.' : 'Спешная атака привела к поражению. Джунгары разбили разрозненные казахские отряды.',
          correctConsequence: language === 'kk' ? 'Үш жүзді біріктіре отырып, сіз қүшті әскер құрдыңыз. Жоңғарларға қарсы айтадай жеңіс!' : 'Объединив три жуза, вы создали мощное войско. Победа над джунгарами!',
          historicalContext: language === 'kk' ? 'Абылай хан бірлік арқылы күшті әскер құру стратегиясын қолданды.' : 'Абылай хан использовал стратегию объединения для создания сильного войска.',
          nextScenarioSetup: language === 'kk' ? 'Үш жүз қосылса, әрі де басқа проблемалар туындайды...' : 'Объединение жузов принесло новые вызовы...'
        }
      ],
      'Абай': [
        {
          scenario: 1,
          text: language === 'kk' ? 'Жас балалар сөз сөйлеу әнерін үйренгісі келеді. Аларға не үйретесіз?' : 'Молодые люди хотят научиться красивой речи. Как их обучить?',
          options: [
            {id: 'A', text: language === 'kk' ? 'Ескі өлеңдерді оқы' : 'Читать старые стихи', isCorrect: false},
            {id: 'B', text: language === 'kk' ? 'Өздік өлең жазуды үйрет' : 'Учить писать собственные стихи', isCorrect: true},
            {id: 'C', text: language === 'kk' ? 'Басқа іс істеуге ықылас бер' : 'Позволить заняться другим', isCorrect: false},
            {id: 'D', text: language === 'kk' ? 'Шетел әдебиетін оқы' : 'Читать иностранную литературу', isCorrect: false}
          ],
          correctAnswer: 'B',
          wrongConsequence: language === 'kk' ? 'Ескі өлеңдерді қайталап жүргеніңіз балалардың шығармашылығын тоқтатты. Олар ешкімге ұқсамасса өлеңдер жаза алмады.' : 'Повторение старых стихов не развивает творчество. Молодежь не может создавать свои произведения.',
          correctConsequence: language === 'kk' ? 'Өз сөздерімен өлең жазуды үйретіңіз - балалар шығармашыл болды! Өндіктіпарлар өндіктіпарлар түрінде қайта ойлау басталады.' : 'Обучая писать собственные стихи, вы развиваете их творчество. Молодежь начинает оригинально мыслить!',
          historicalContext: language === 'kk' ? 'Абай өздік шығармашылықты түлектіге үйреді, ол қазақ әдебиетінің сәні болды.' : 'Абай учил ученикам самостоятельному творчеству, что стало основой казахской литературы.',
          nextScenarioSetup: language === 'kk' ? 'Балалар өлең жаза барлығына балалық та бұлай ілінді...' : 'Юные поэты начали творить...'
        }
      ],
      'Айтеке би': [
        {
          scenario: 1,
          text: language === 'kk' ? 'Екі саудагер өнімділік туралы дауласып жатыр. Сіз әділ сот ете аласыз ба?' : 'Два купца спорят о товаре. Как разрешить этот спор справедливо?',
          options: [
            {id: 'A', text: language === 'kk' ? 'Күшілі тарапқа құқық бер' : 'Дать право более сильному', isCorrect: false},
            {id: 'B', text: language === 'kk' ? 'Екеуінің де сөзін тыңда' : 'Выслушать обе стороны', isCorrect: true},
            {id: 'C', text: language === 'kk' ? 'Ешкімге байланыстырма' : 'Не разбираться в спорах', isCorrect: false},
            {id: 'D', text: language === 'kk' ? 'Ысқақ төңнег өлеңін' : 'Призвать свидетелей', isCorrect: false}
          ],
          correctAnswer: 'B',
          wrongConsequence: language === 'kk' ? 'Біржақтап сот істесеңіз, халық сізге күмәнеді. Өндіктіпарлар өндіктіпарлар секе міндеттерді істей қоймайды.' : 'Несправедливое решение подрывает доверие народа. Люди перестанут обращаться к вам с делами.',
          correctConsequence: language === 'kk' ? 'Екеуінің де сөзін тыңдау арқылы сіз әділ шешім қабылдадыңыз. Халық сіздің даналығына мойындау жасады және өндіктіпарлар сіздің сотын сезінді.' : 'Выслушав обе стороны, вы вынесли справедливое решение. Народ уважает вашу мудрость!',
          historicalContext: language === 'kk' ? 'Айтеке би әділік жеті жарғыда айтылғандай әділік арқылы халық өндіктіпарларын сақтады.' : 'Айтеке би, как установлено в Жеті Жарғы, разрешал споры справедливо.',
          nextScenarioSetup: language === 'kk' ? 'Әділ сот өндіктіпарлар түліктіне ықдай, түліктіктелік өндіктіпарлар келіді...' : 'Справедливость укрепила доверие народа...'
        }
      ]
    };

    const characterFallbacks = fallbacks[character] || fallbacks['Абылай хан'];
    return characterFallbacks[Math.min(scenarioNumber - 1, characterFallbacks.length - 1)];
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MissionGenerator;
} else if (typeof window !== 'undefined') {
  window.MissionGenerator = MissionGenerator;
}
