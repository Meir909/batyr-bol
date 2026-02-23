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
   * @param {string} character - Character name
   * @param {number} scenarioNumber - Scenario number
   * @param {number} level - Player level (1-10)
   * @param {string} language - Language code ('kk' or 'ru')
   * @returns {Promise<Object>} - Single scenario data with options
   */
  async generateScenario(character, scenarioNumber = 1, level = 1, language = 'kk') {
    try {
      // Build prompt for scenario generation
      const prompt = this._buildScenarioPrompt(character, level, scenarioNumber, language);

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

      if (!response.ok) {
        // Use fallback if API fails
        console.warn(`API error: ${response.status}, using fallback scenario`);
        return this._getFallbackScenario(character, scenarioNumber, language);
      }

      const data = await response.json();

      if (data.success && data.scenario) {
        // Normalize response format
        return {
          scenario: data.scenario.text || data.scenario.scenario || '',
          options: (data.scenario.options || []).map(opt => ({
            text: opt.text || opt.option || '',
            is_correct: opt.is_correct || opt.isCorrect || false,
            explanation: opt.explanation || opt.consequence || ''
          })),
          correct_answer: data.scenario.correct_answer || data.scenario.correctAnswer,
          fallback: false
        };
      } else {
        // Fallback scenario
        return this._getFallbackScenario(character, scenarioNumber, language);
      }
    } catch (error) {
      console.error('Mission generation error:', error);
      // Always return fallback on error
      return this._getFallbackScenario(character, scenarioNumber, language);
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
    // Normalize character name (handle both 'Абай' and 'Абай Кунанбаев')
    let normalizedCharacter = character;
    if (character === 'Абай' || character === 'Абай Кунанбаев') {
      normalizedCharacter = 'Абай';
    }

    console.log('[DEBUG] Using fallback scenario for:', normalizedCharacter, scenarioNumber, language);

    const fallbacks = {
      'Абылай хан': [
        {
          scenario: language === 'kk' ? 'Жоңғар сарбаздары қазақ жерінің шегіне жақындады. Ата-баба қорғау үшін не істеу керек?' : 'Джунгарские войска приблизились к границам. Как защитить земли предков?',
          options: [
            {text: language === 'kk' ? 'Тез атақ жасау' : 'Немедленно атаковать', is_correct: false, explanation: language === 'kk' ? 'Спешная атака привела к разрозненному сопротивлению' : 'Спешная атака привела к разрозненному сопротивлению'},
            {text: language === 'kk' ? 'Үш жүздің барлығын біліктестіру' : 'Объединить три жуза', is_correct: true, explanation: language === 'kk' ? 'Үш жүзді біріктіре отырып, сіз қүшті әскер құрдыңыз' : 'Объединив три жуза, вы создали мощное войско'},
            {text: language === 'kk' ? 'Түгелтеп іле шығу' : 'Отступить', is_correct: false, explanation: language === 'kk' ? 'Отступление ослабляет позиции' : 'Отступление ослабляет позиции'},
            {text: language === 'kk' ? 'Орыстарға көмек сұрау' : 'Попросить помощи у русских', is_correct: false, explanation: language === 'kk' ? 'Зависимость от других - слабость' : 'Зависимость от других - слабость'}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Бірінші ұрысынан кейін халық құлығын жоғалттағаннан күнініс көргені белгілі болды. Боевой дух қалай қалпына келтіруге болады?' : 'После первого поражения народ потерял веру в вас. Как восстановить боевой дух?',
          options: [
            {text: language === 'kk' ? 'Қадәт ұрысын жариялау' : 'Объявить священную войну', is_correct: false, explanation: language === 'kk' ? 'Эмоции не заменяют стратегию' : 'Эмоции не заменяют стратегию'},
            {text: language === 'kk' ? 'Биялар сатысын істеп, әскерді қайта құру' : 'Провести совет биев и переформировать войско', is_correct: true, explanation: language === 'kk' ? 'Даналық бұлтынын қалпына келтіреді' : 'Мудрость восстанавливает единство'},
            {text: language === 'kk' ? 'Барлығына сыйлықтар ұсыну' : 'Пообещать награды', is_correct: false, explanation: language === 'kk' ? 'Үзінді мамынды түсіндіру керек' : 'Нужна стратегия, не награды'},
            {text: language === 'kk' ? 'Күту және өндіктіпарлы' : 'Отступить и переждать', is_correct: false, explanation: language === 'kk' ? 'Уақыт төл дос емес' : 'Время работает против нас'}
          ],
          correct_answer: 'B'
        }
      ],
      'Абай': [
        {
          scenario: language === 'kk' ? 'Жас балалар сөз сөйлеу әнерін үйренгісі келеді. Аларға не үйретесіз?' : 'Молодые люди хотят научиться красивой речи. Как их обучить?',
          options: [
            {text: language === 'kk' ? 'Ескі өлеңдерді оқы' : 'Читать старые стихи', is_correct: false, explanation: language === 'kk' ? 'Ескі өлеңдер баға емес' : 'Старые стихи не помогают учиться'},
            {text: language === 'kk' ? 'Өздік өлең жазуды үйрет' : 'Учить писать собственные стихи', is_correct: true, explanation: language === 'kk' ? 'Өздік шығармашылық өндіктіпарлар өндіктіпарларын қалпына келтіреді' : 'Собственное творчество развивает мышление'},
            {text: language === 'kk' ? 'Басқа іс істеуге ықылас бер' : 'Позволить заняться другим', is_correct: false, explanation: language === 'kk' ? 'Ойынды қоштау - өндіктіпарлар' : 'Отвлечение не помогает учиться'},
            {text: language === 'kk' ? 'Шетел әдебиетін оқы' : 'Читать иностранную литературу', is_correct: false, explanation: language === 'kk' ? 'Өз тілді білу керек' : 'Нужно знать свой язык'}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар өндіктіпарларының сөзіне ынамсыз болуы мүмкін. Оларды сендіруге не істеу керек?' : 'Ученики сомневаются в вашем учении. Как убедить их в правоте?',
          options: [
            {text: language === 'kk' ? 'Қоршеген адамдар істеген сөзге құлақ тағу' : 'Слушать, что говорят окружающие', is_correct: false, explanation: language === 'kk' ? 'Қоршеген әуелі өндіктіпарлар сөздеді құлақ қоймайды' : 'Люди часто слабо понимают смысл'},
            {text: language === 'kk' ? 'Өндіктіпарлар сөзінің дұрыс екенін өндіктіпарлар мысалымен көрсету' : 'Показать примерами из жизни', is_correct: true, explanation: language === 'kk' ? 'Өндіктіпарлар мысалымен құлақ сөйлеп түседі' : 'Живые примеры убеждают лучше слов'},
            {text: language === 'kk' ? 'Ынамсыз болуды қайтарып салу' : 'Отвергнуть сомнения', is_correct: false, explanation: language === 'kk' ? 'Сомнения пиши, үйрену керек' : 'Сомнения нужно разрешать'},
            {text: language === 'kk' ? 'Басқа өндіктіпарлар табу' : 'Найти других учеников', is_correct: false, explanation: language === 'kk' ? 'Өндіктіпарлар бөлік-бөлік - өндіктіпарлар' : 'Уход учеников - плохо для обучения'}
          ],
          correct_answer: 'B'
        }
      ],
      'Айтеке би': [
        {
          scenario: language === 'kk' ? 'Екі саудагер өнімділік туралы дауласып жатыр. Сіз әділ сот ете аласыз ба?' : 'Два купца спорят о товаре. Как разрешить этот спор справедливо?',
          options: [
            {text: language === 'kk' ? 'Күшілі тарапқа құқық бер' : 'Дать право более сильному', is_correct: false, explanation: language === 'kk' ? 'Онда әділік жоқ' : 'Это несправедливо'},
            {text: language === 'kk' ? 'Екеуінің де сөзін тыңда' : 'Выслушать обе стороны', is_correct: true, explanation: language === 'kk' ? 'Әділік - екеуінің де сөзінің сөйлеуінде' : 'Справедливость требует послушания обеих сторон'},
            {text: language === 'kk' ? 'Ешкімге байланыстырма' : 'Не разбираться в спорах', is_correct: false, explanation: language === 'kk' ? 'Сот істеуі керек' : 'Необходимо разрешать конфликты'},
            {text: language === 'kk' ? 'Ысқақ төңнег өлеңін' : 'Призвать свидетелей', is_correct: false, explanation: language === 'kk' ? 'Өндіктіпарлар сөзінің ең бастысы' : 'Свидетели важны, но нужна справедливость'}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Бір ата-ана балалыққасындағы балалығын атыс істеп жатыр. Өндіктіпарлар өндіктіпарларың өндіктіпарларын өндіктіпарлар.' : 'Родитель обвиняет соседа в оскорблении. Как судить справедливо?',
          options: [
            {text: language === 'kk' ? 'Ата-ананың сөзі - шындық' : 'Слово родителя - закон', is_correct: false, explanation: language === 'kk' ? 'Бірінің сөзі - әлі істеуге жетпес' : 'Одного свидетеля недостаточно'},
            {text: language === 'kk' ? 'Екеуінің де дәлелдеуін төле' : 'Потребовать доказательства от обеих сторон', is_correct: true, explanation: language === 'kk' ? 'Дәлелі - әділіктің негізі' : 'Доказательства - основа справедливости'},
            {text: language === 'kk' ? 'Көршелерге сұра' : 'Спросить соседей', is_correct: false, explanation: language === 'kk' ? 'Көршелер әрі де өндіктіпарлар болуы мүмкін' : 'Соседи могут быть предвзяты'},
            {text: language === 'kk' ? 'Баланың сөзін тыңда' : 'Слушать ребенка', is_correct: false, explanation: language === 'kk' ? 'Бала баршылықсыз сөйлеген болуы мүмкін' : 'Ребенок может ошибаться'}
          ],
          correct_answer: 'B'
        }
      ]
    };

    const characterFallbacks = fallbacks[normalizedCharacter] || fallbacks['Абылай хан'];
    const fallback = characterFallbacks[Math.min(scenarioNumber - 1, characterFallbacks.length - 1)];

    if (!fallback) {
      console.error('[ERROR] Fallback scenario not found for:', character, scenarioNumber);
      // Return a default scenario if fallback not found
      return {
        scenario: 'Қате: сценарий жүктелген жоқ',
        options: [{text: 'Қайта байланысуға тырысыңыз', is_correct: true, explanation: 'Сценарий жүктелмеген'}],
        correct_answer: 'A',
        fallback: true
      };
    }

    const result = {
      scenario: fallback.scenario,
      options: fallback.options,
      correct_answer: fallback.correct_answer,
      fallback: true
    };

    console.log('[DEBUG] Fallback scenario result:', result);
    return result;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MissionGenerator;
} else if (typeof window !== 'undefined') {
  window.MissionGenerator = MissionGenerator;
}
