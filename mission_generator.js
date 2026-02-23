/**
 * Mission Generator - OPTIMIZED VERSION
 * Ultra-short prompts + 6 unique scenarios per character
 */

class MissionGenerator {
  constructor() {
    this.apiBase = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';
  }

  async generateScenario(character, scenarioNumber = 1, level = 1, language = 'kk') {
    try {
      const prompt = this._buildScenarioPrompt(character, level, scenarioNumber, language);

      const response = await fetch(`${this.apiBase}/api/mission/generate-scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character, level, scenarioNumber, prompt, language })
      });

      if (!response.ok) {
        console.warn(`API error: ${response.status}, fallback`);
        return this._getFallbackScenario(character, scenarioNumber, language);
      }

      const data = await response.json();
      if (data.success && data.scenario) {
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
      }
      return this._getFallbackScenario(character, scenarioNumber, language);
    } catch (error) {
      console.error('Generation error:', error);
      return this._getFallbackScenario(character, scenarioNumber, language);
    }
  }

  _buildScenarioPrompt(character, level, scenarioNumber, language) {
    // ULTRA-OPTIMIZED: 3-line prompts instead of 30+
    return language === 'kk' ?
      `${character} (#${scenarioNumber}, lvl ${level}): Сценарий жасау. JSON: {"text":"ситуация (80 сөз)","options":[{"text":"...","isCorrect":false},{"text":"дұрыс жауап","isCorrect":true},{"text":"...","isCorrect":false},{"text":"...","isCorrect":false}],"correctAnswer":"B"}`
      :
      `${character} (#${scenarioNumber}, lvl ${level}): Create scenario. JSON: {"text":"situation (80 words)","options":[{"text":"...","isCorrect":false},{"text":"correct answer","isCorrect":true},{"text":"...","isCorrect":false},{"text":"...","isCorrect":false}],"correctAnswer":"B"}`;
  }

  _getFallbackScenario(character, scenarioNumber, language) {
    let normalizedCharacter = character;
    if (character === 'Абай' || character === 'Абай Кунанбаев') {
      normalizedCharacter = 'Абай';
    }

    const fallbacks = {
      'Абылай хан': [
        {
          scenario: language === 'kk' ? 'Жоңғарлар шегіне жақындады. Оны қорғау қалай?' : 'Врагов приблизилась. Как защитить земли?',
          options: [
            {text: language === 'kk' ? 'Тез атақ' : 'Быстро атаковать', is_correct: false},
            {text: language === 'kk' ? '3 жүз біліктестіру' : 'Объединить три жуза', is_correct: true},
            {text: language === 'kk' ? 'Іле шығу' : 'Отступить', is_correct: false},
            {text: language === 'kk' ? 'Көмек сұрау' : 'Просить помощь', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Ұрысынан кейін халық құлығын жоғалтты. Оны қалпына қалай?' : 'После поражения люди потеряли веру. Как восстановить дух?',
          options: [
            {text: language === 'kk' ? 'Қадәт ұрыс' : 'Священная война', is_correct: false},
            {text: language === 'kk' ? 'Биялар сатысы' : 'Совет старейшин', is_correct: true},
            {text: language === 'kk' ? 'Сыйлықтар' : 'Обещать награды', is_correct: false},
            {text: language === 'kk' ? 'Күту' : 'Ждать', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Көршілер салық төлемегісі келді. Не істеу?' : 'Соседи не платят налоги. Что делать?',
          options: [
            {text: language === 'kk' ? 'Әскер жібер' : 'Отправить войска', is_correct: false},
            {text: language === 'kk' ? 'Елшіді жіберіп келіс' : 'Послов отправить', is_correct: true},
            {text: language === 'kk' ? 'Салықты ұмыт' : 'Забыть о налогах', is_correct: false},
            {text: language === 'kk' ? 'Түлік пайла' : 'Поделить награды', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Орыс империясы бірлік ұсынды. Өндіктіпарлар сақта?' : 'Русская империя союз. Независимость?',
          options: [
            {text: language === 'kk' ? 'Бәрі қабыл' : 'Полностью согласиться', is_correct: false},
            {text: language === 'kk' ? 'Салым + өндіктіпарлар' : 'Налог, но автономия', is_correct: true},
            {text: language === 'kk' ? 'Бәрі таслау' : 'Разорвать все', is_correct: false},
            {text: language === 'kk' ? 'Басқа табу' : 'Найти другого', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Жастар ұрысқа оқу болды. Оларды қалай дайындау?' : 'Молодежь хочет война. Как подготовить?',
          options: [
            {text: language === 'kk' ? 'Опыт өндіктіпарлар' : 'Опытным воинам обучить', is_correct: true},
            {text: language === 'kk' ? 'Тек теория' : 'Только теория', is_correct: false},
            {text: language === 'kk' ? 'Елші істеу' : 'Послом сделать', is_correct: false},
            {text: language === 'kk' ? 'Басқа істі' : 'Другим делом', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар тарихы маңайлы. Оны кім сақтау?' : 'История государства. Кто сохранит?',
          options: [
            {text: language === 'kk' ? 'Тек өндіктіпарлар' : 'Только жрецы', is_correct: false},
            {text: language === 'kk' ? 'Барлығы білу керек' : 'Все должны знать', is_correct: true},
            {text: language === 'kk' ? 'Элита ғана' : 'Только элита', is_correct: false},
            {text: language === 'kk' ? 'Маңайсыз' : 'Не важно', is_correct: false}
          ],
          correct_answer: 'B'
        }
      ],
      'Абай': [
        {
          scenario: language === 'kk' ? 'Жастар сөйлеу әнері үйрену болды. Оларға не үйрету?' : 'Молодежь красивую речь. Как учить?',
          options: [
            {text: language === 'kk' ? 'Ескі өлең оқы' : 'Читать старые стихи', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар өлең жаз' : 'Свои стихи писать', is_correct: true},
            {text: language === 'kk' ? 'Басқа істі' : 'Другим делом', is_correct: false},
            {text: language === 'kk' ? 'Шетел әдеб' : 'Иностранную литературу', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Оқушылар өндіктіпарлар сөзіне сенбеді. Оларды сендіру?' : 'Ученики сомневаются. Убедить их?',
          options: [
            {text: language === 'kk' ? 'Өндіктіпарлар сөзін' : 'Слушать других', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар мысалы' : 'Примерами показать', is_correct: true},
            {text: language === 'kk' ? 'Орын тасту' : 'Отвергнуть', is_correct: false},
            {text: language === 'kk' ? 'Басқа табу' : 'Других найти', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар ақыны болғасы келді. Қандай сөлет?' : 'Хотят стать поэтами. Советы?',
          options: [
            {text: language === 'kk' ? 'Өндіктіпарлар көшіру' : 'Копировать мастеров', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар туралы жаз' : 'О своей жизни писать', is_correct: true},
            {text: language === 'kk' ? 'Жазбасын' : 'Не писать', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Другое занятие', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар морал құру. Қалай басқарғалы?' : 'Нравственность в обществе. Как?',
          options: [
            {text: language === 'kk' ? 'Қатағай заңдар' : 'Строгие законы', is_correct: false},
            {text: language === 'kk' ? 'Білім және өндіктіпарлар' : 'Образование', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Богатство', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Власть', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар мен өндіктіпарлар төтенше. Өндіктіпарлар?' : 'Традиции vs прогресс. Как?',
          options: [
            {text: language === 'kk' ? 'Ескіге қол теппеу' : 'Отказаться от старого', is_correct: false},
            {text: language === 'kk' ? 'Екеуі де сақтау, өндіктіпарлар' : 'Оба сохранить', is_correct: true},
            {text: language === 'kk' ? 'Тек ескі' : 'Только традиции', is_correct: false},
            {text: language === 'kk' ? 'Ынамдас' : 'Компромисс', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Философия адамның өндіктіпарларында. Өндіктіпарлар?' : 'Философия в жизни. Роль?',
          options: [
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Бесполезна', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар мағына' : 'Смысл найти помогает', is_correct: true},
            {text: language === 'kk' ? 'Тек өндіктіпарлар' : 'Только для ученых', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар орнына' : 'Веру заменяет', is_correct: false}
          ],
          correct_answer: 'B'
        }
      ],
      'Айтеке би': [
        {
          scenario: language === 'kk' ? 'Екі саудагер өндіктіпарлар. Әділ өндіктіпарлар?' : 'Два купца спор. Справедливо судить?',
          options: [
            {text: language === 'kk' ? 'Күшті беру' : 'Сильному дать', is_correct: false},
            {text: language === 'kk' ? 'Екеуінің де сөзін' : 'Обоих слушать', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Не разбираться', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Свидетелей позвать', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Ата-ана өндіктіпарлар. Әділ өндіктіпарлар?' : 'Родитель обвинение. Судить справедливо?',
          options: [
            {text: language === 'kk' ? 'Өндіктіпарлар заң' : 'Слово - закон', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар екеуінің' : 'Доказательства требовать', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар сұра' : 'Соседей спросить', is_correct: false},
            {text: language === 'kk' ? 'Балаға теңбеу' : 'Ребенка слушать', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар өндіктіпарлары. Әділ өндіктіпарлар?' : 'Раздор о наследстве. Как справедливо?',
          options: [
            {text: language === 'kk' ? 'Ұлығына' : 'Старшему все', is_correct: false},
            {text: language === 'kk' ? 'Заңға өндіктіпарлар' : 'По закону справедливо', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Поровну всем', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Жребий', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар. Шындықты өндіктіпарлар?' : 'Ложное обвинение. Истину как?',
          options: [
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Обвинителю верить', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар тексеру' : 'Расследовать проверить', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Наказать подозреваемого', is_correct: false},
            {text: language === 'kk' ? 'Ұмыту' : 'Забыть', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар өндіктіпарлары. Өндіктіпарлар миралу?' : 'Конфликт племен о земле. Мир?',
          options: [
            {text: language === 'kk' ? 'Ұрыс' : 'Война решит', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар міндеттеме' : 'Переговоры договор', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар барлығы' : 'Одному все', is_correct: false},
            {text: language === 'kk' ? 'Шекара' : 'Границу провести', is_correct: false}
          ],
          correct_answer: 'B'
        },
        {
          scenario: language === 'kk' ? 'Өндіктіпарлар өндіктіпарлы. Әділ өндіктіпарлар?' : 'Преступление под давлением. Судить?',
          options: [
            {text: language === 'kk' ? 'Максималды' : 'Максимум наказания', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар есептеу' : 'Обстоятельства учитывать', is_correct: true},
            {text: language === 'kk' ? 'Өндіктіпарлар' : 'Не наказывать', is_correct: false},
            {text: language === 'kk' ? 'Өндіктіпарлар сұра' : 'Людей спросить', is_correct: false}
          ],
          correct_answer: 'B'
        }
      ]
    };

    const charFallbacks = fallbacks[normalizedCharacter] || fallbacks['Абылай хан'];
    const scenario = charFallbacks[Math.min(scenarioNumber - 1, charFallbacks.length - 1)];

    if (!scenario) {
      return {
        scenario: language === 'kk' ? 'Қате' : 'Ошибка',
        options: [{text: language === 'kk' ? 'Қайта' : 'Снова', is_correct: true}],
        correct_answer: 'A',
        fallback: true
      };
    }

    return {
      scenario: scenario.scenario,
      options: scenario.options,
      correct_answer: scenario.correct_answer,
      fallback: true
    };
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = MissionGenerator;
} else if (typeof window !== 'undefined') {
  window.MissionGenerator = MissionGenerator;
}
