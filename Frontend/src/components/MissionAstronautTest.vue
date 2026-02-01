<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const testCategories = ref([
  {
    id: 1,
    name: 'Реакция',
    icon: 'fa-bolt',
    description: 'Тест на скорость реакции',
    questions: [
      {
        id: 1,
        type: 'reaction',
        question: 'Нажмите кнопку как только увидите зелёный свет!',
        answer: null,
        time: 0,
        maxTime: 3000,
        startTime: null,
        completed: false
      },
      {
        id: 2,
        type: 'reaction',
        question: 'Отметьте летающий объект',
        options: ['🛸', '✈️', '🚀', '🛰️'],
        correctIndex: 2,
        answer: null,
        time: 0,
        startTime: null,
        completed: false
      }
    ],
    completed: false,
    score: 0
  },
  {
    id: 2,
    name: 'Память',
    icon: 'fa-brain',
    description: 'Тест на кратковременную память',
    questions: [
      {
        id: 1,
        type: 'memory',
        question: 'Запомните последовательность планет:',
        sequence: ['🌍', '🪐', '☄️', '🌕'],
        answer: [],
        time: 0,
        startTime: null,
        completed: false,
        userSequence: []
      },
      {
        id: 2,
        type: 'memory',
        question: 'Какие числа были на экране?',
        numbers: null,
        answer: [],
        time: 0,
        startTime: null,
        completed: false,
        correctNumbers: null
      }
    ],
    completed: false,
    score: 0
  },
  {
    id: 3,
    name: 'Знания',
    icon: 'fa-graduation-cap',
    description: 'Проверка знаний космонавтики',
    questions: [
      {
        id: 1,
        type: 'knowledge',
        question: 'Кто был первым человеком в космосе?',
        options: ['Нил Армстронг', 'Юрий Гагарин', 'Алан Шепард', 'Валентина Терешкова'],
        correctIndex: 1,
        answer: null,
        time: 0,
        startTime: null,
        completed: false
      },
      {
        id: 2,
        type: 'knowledge',
        question: 'Сколько длился первый выход в открытый космос?',
        options: ['12 минут', '23 минуты', '1 час 12 минут', '2 часа 5 минут'],
        correctIndex: 0,
        answer: null,
        time: 0,
        startTime: null,
        completed: false
      },
      {
        id: 3,
        type: 'knowledge',
        question: 'Какой был позывной у Аполлона-11?',
        options: ['Колумбия', 'Орёл', 'Челленджер', 'Дискавери'],
        correctIndex: 1,
        answer: null,
        time: 0,
        startTime: null,
        completed: false
      }
    ],
    completed: false,
    score: 0
  }
])

const currentCategory = ref(0)
const currentQuestion = ref(0)
const testStarted = ref(false)
const testCompleted = ref(false)
const reactionStartTime = ref(null)
const reactionActive = ref(false)
const showSequence = ref(false)
const memoryNumbers = ref([])
const showNumbers = ref(false)
const totalScore = ref(0)
const astronautStatus = ref('Кандидат')
const reactionTimer = ref(null)

const currentTest = computed(() => {
  return testCategories.value[currentCategory.value]
})

const currentQ = computed(() => {
  return testCategories.value[currentCategory.value]?.questions[currentQuestion.value]
})

// Генерация случайных чисел для теста памяти
const generateRandomNumbers = () => {
  const numbers = []
  for (let i = 0; i < 4; i++) {
    numbers.push(Math.floor(Math.random() * 10))
  }
  return numbers
}

const startTest = () => {
  testStarted.value = true
  testCompleted.value = false
  currentCategory.value = 0
  currentQuestion.value = 0
  totalScore.value = 0
  astronautStatus.value = 'Кандидат'

  // Сброс всех категорий и вопросов
  testCategories.value.forEach(category => {
    category.completed = false
    category.score = 0
    category.questions.forEach(question => {
      question.answer = null
      question.time = 0
      question.startTime = null
      question.completed = false
      if (question.type === 'memory' && question.id === 2) {
        question.numbers = generateRandomNumbers()
        question.correctNumbers = [...question.numbers]
      }
    })
  })

  // Начинаем с первого вопроса
  startCurrentQuestion()
}

const startCurrentQuestion = () => {
  const question = currentQ.value
  if (!question) return

  question.startTime = Date.now()
  question.completed = false

  if (question.type === 'reaction' && question.id === 1) {
    startReactionTimer()
  } else if (question.type === 'memory' && question.id === 1) {
    showSequence.value = true
    setTimeout(() => {
      showSequence.value = false
      question.userSequence = []
    }, 2000)
  } else if (question.type === 'memory' && question.id === 2) {
    showNumbers.value = true
    memoryNumbers.value = [...question.numbers]
    setTimeout(() => {
      showNumbers.value = false
      question.answer = []
    }, 2000)
  }
}

const startReactionTimer = () => {
  if (reactionTimer.value) clearTimeout(reactionTimer.value)

  reactionActive.value = false
  const delay = Math.random() * 2000 + 1000 // 1-3 секунды

  reactionTimer.value = setTimeout(() => {
    reactionActive.value = true
    reactionStartTime.value = Date.now()
    currentQ.value.startTime = Date.now()
  }, delay)
}

const handleReactionClick = () => {
  if (!reactionActive.value) return

  const question = currentQ.value
  if (!question) return

  const reactionTime = Date.now() - reactionStartTime.value
  question.time = reactionTime
  question.answer = reactionTime
  question.completed = true

  // Начисление очков
  let points = 0
  if (reactionTime < 300) {
    points = 50
  } else if (reactionTime < 600) {
    points = 40
  } else if (reactionTime < 1000) {
    points = 30
  } else {
    points = 20
  }

  currentTest.value.score += points
  nextQuestion()
}

const handleReactionOption = (index) => {
  const question = currentQ.value
  if (!question) return

  question.answer = index
  question.time = Date.now() - question.startTime
  question.completed = true

  // Проверка правильности
  if (index === question.correctIndex) {
    currentTest.value.score += 40
  } else {
    currentTest.value.score += 10
  }

  nextQuestion()
}

const handleMemoryItemClick = (item) => {
  const question = currentQ.value
  if (!question || question.id !== 1) return

  if (!question.userSequence) question.userSequence = []
  question.userSequence.push(item)

  if (question.userSequence.length === question.sequence.length) {
    // Проверяем правильность
    const correct = question.userSequence.every((item, index) =>
        item === question.sequence[index]
    )

    question.answer = correct ? 1 : 0
    question.time = Date.now() - question.startTime
    question.completed = true

    if (correct) {
      currentTest.value.score += 40
    } else {
      currentTest.value.score += 10
    }

    nextQuestion()
  }
}

const handleMemoryNumberInput = (index, value) => {
  const question = currentQ.value
  if (!question || question.id !== 2) return

  if (!question.answer) question.answer = []
  question.answer[index] = parseInt(value) || 0

  // Проверяем, все ли числа введены
  if (question.answer.length === 4 && question.answer.every(num => num !== null && num !== undefined)) {
    const correct = question.answer.every((num, idx) =>
        num === question.correctNumbers[idx]
    )

    question.completed = true
    question.time = Date.now() - question.startTime

    if (correct) {
      currentTest.value.score += 40
    } else {
      currentTest.value.score += 10
    }

    nextQuestion()
  }
}

const handleKnowledgeAnswer = (index) => {
  const question = currentQ.value
  if (!question) return

  question.answer = index
  question.time = Date.now() - question.startTime
  question.completed = true

  // Проверка правильности
  if (index === question.correctIndex) {
    currentTest.value.score += 30
  }

  nextQuestion()
}

const nextQuestion = () => {
  reactionActive.value = false
  if (reactionTimer.value) {
    clearTimeout(reactionTimer.value)
    reactionTimer.value = null
  }

  // Ждем немного перед переходом
  setTimeout(() => {
    const category = currentTest.value

    if (currentQuestion.value < category.questions.length - 1) {
      currentQuestion.value++
      startCurrentQuestion()
    } else {
      completeCategory()
    }
  }, 1000)
}

const completeCategory = () => {
  const category = currentTest.value
  category.completed = true
  totalScore.value += category.score

  if (currentCategory.value < testCategories.value.length - 1) {
    currentCategory.value++
    currentQuestion.value = 0
    startCurrentQuestion()
  } else {
    completeTest()
  }
}

const completeTest = () => {
  testCompleted.value = true

  // Определение статуса
  if (totalScore.value >= 180) {
    astronautStatus.value = 'Космонавт'
  } else if (totalScore.value >= 120) {
    astronautStatus.value = 'Кандидат в космонавты'
  } else if (totalScore.value >= 80) {
    astronautStatus.value = 'Космический турист'
  } else {
    astronautStatus.value = 'Наблюдатель'
  }
}

const getProgress = computed(() => {
  const totalQuestions = testCategories.value.reduce((sum, cat) => sum + cat.questions.length, 0)
  const answeredQuestions = testCategories.value.reduce((sum, cat) =>
      sum + cat.questions.filter(q => q.completed).length, 0
  )
  return (answeredQuestions / totalQuestions) * 100
})

const getQuestionStatus = (categoryIndex, questionIndex) => {
  const question = testCategories.value[categoryIndex]?.questions[questionIndex]
  if (!question) return 'pending'

  if (question.completed) return 'completed'
  if (categoryIndex === currentCategory.value && questionIndex === currentQuestion.value) return 'active'
  return 'pending'
}

const resetMemorySequence = () => {
  const question = currentQ.value
  if (question && question.type === 'memory' && question.id === 1) {
    question.userSequence = []
  }
}

onMounted(() => {
  // Инициализируем числа для теста памяти
  testCategories.value.forEach(category => {
    category.questions.forEach(question => {
      if (question.type === 'memory' && question.id === 2) {
        question.numbers = generateRandomNumbers()
        question.correctNumbers = [...question.numbers]
      }
    })
  })
})
</script>

<template>
  <div class="mission-container">
    <div class="mission-header">
      <h2><i class="fas fa-user-astronaut"></i> Тест космонавта</h2>
      <p>Пройдите испытания на реакцию, память и знания, как настоящие покорители космоса!</p>
    </div>

    <div class="test-container">
      <div class="test-sidebar">
        <div class="astronaut-profile">
          <div class="profile-avatar">
            <i class="fas fa-user-astronaut"></i>
          </div>
          <h4>Кандидат</h4>
          <p class="status">{{ astronautStatus }}</p>
          <div class="profile-score">
            <i class="fas fa-star"></i>
            <span>{{ totalScore }} очков</span>
          </div>
        </div>

        <div class="progress-tracker">
          <h5>Прогресс теста:</h5>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${getProgress}%` }"></div>
          </div>
          <p>{{ Math.round(getProgress) }}% выполнено</p>
        </div>

        <div class="test-categories">
          <div
              v-for="(category, catIndex) in testCategories"
              :key="category.id"
              class="category-item"
              :class="{
              active: catIndex === currentCategory,
              completed: category.completed
            }"
          >
            <div class="category-icon">
              <i :class="`fas ${category.icon}`"></i>
            </div>
            <div class="category-info">
              <h6>{{ category.name }}</h6>
              <p>{{ category.description }}</p>
              <div class="category-score" v-if="category.completed">
                {{ category.score }} очков
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="test-main">
        <div v-if="!testStarted" class="welcome-screen">
          <div class="welcome-content">
            <i class="fas fa-user-astronaut"></i>
            <h3>Добро пожаловать на отбор космонавтов!</h3>
            <p>Вам предстоит пройти три испытания:</p>
            <ul class="test-overview">
              <li><i class="fas fa-bolt"></i> <strong>Реакция</strong> - проверка скорости реакции</li>
              <li><i class="fas fa-brain"></i> <strong>Память</strong> - тест кратковременной памяти</li>
              <li><i class="fas fa-graduation-cap"></i> <strong>Знания</strong> - вопросы космонавтики</li>
            </ul>
            <button class="btn btn-primary btn-large" @click="startTest">
              <i class="fas fa-play"></i> Начать тестирование
            </button>
          </div>
        </div>

        <div v-if="testStarted && !testCompleted" class="test-area">
          <div class="test-header">
            <h3>{{ currentTest.name }}</h3>
            <p>{{ currentTest.description }}</p>
            <div class="test-progress">
              Вопрос {{ currentQuestion + 1 }} из {{ currentTest.questions.length }}
            </div>
          </div>

          <div class="question-area">
            <!-- Тест реакции - зеленый свет -->
            <div v-if="currentQ.type === 'reaction' && currentQ.id === 1" class="reaction-test">
              <h4>{{ currentQ.question }}</h4>

              <div class="reaction-button-container">
                <div
                    class="reaction-button"
                    :class="{ active: reactionActive }"
                    @click="handleReactionClick"
                >
                  <div v-if="!reactionActive" class="waiting">
                    <i class="fas fa-hourglass-half"></i>
                    <p>Ждите зелёного сигнала...</p>
                  </div>
                  <div v-if="reactionActive" class="active-signal">
                    <i class="fas fa-bolt"></i>
                    <p>НАЖМИТЕ СЕЙЧАС!</p>
                  </div>
                </div>

                <div v-if="currentQ.completed" class="reaction-result">
                  <p>Время реакции: {{ currentQ.time }} мс</p>
                  <p v-if="currentQ.time < 500" class="fast-reaction">Отличная реакция! 🚀</p>
                  <p v-else-if="currentQ.time < 1000" class="good-reaction">Хорошая реакция! ✨</p>
                  <p v-else class="normal-reaction">Нормальная реакция! ⭐</p>
                </div>
              </div>
            </div>

            <!-- Тест реакции - выбор объекта -->
            <div v-if="currentQ.type === 'reaction' && currentQ.id === 2" class="reaction-test">
              <h4>{{ currentQ.question }}</h4>

              <div class="reaction-options">
                <div
                    v-for="(option, index) in currentQ.options"
                    :key="index"
                    class="reaction-option"
                    :class="{ selected: currentQ.answer === index }"
                    @click="handleReactionOption(index)"
                >
                  <span class="option-emoji">{{ option }}</span>
                  <span class="option-label">{{
                      index === 0 ? 'НЛО' :
                          index === 1 ? 'Самолёт' :
                              index === 2 ? 'Ракета' : 'Спутник'
                    }}</span>
                </div>
              </div>

              <div v-if="currentQ.completed" class="reaction-feedback">
                <div v-if="currentQ.answer === currentQ.correctIndex" class="correct-answer">
                  <i class="fas fa-check-circle"></i> Правильно! Ракета - летательный аппарат для космоса!
                </div>
                <div v-else class="incorrect-answer">
                  <i class="fas fa-times-circle"></i> Неправильно. Правильный ответ: Ракета
                </div>
              </div>
            </div>

            <!-- Тест памяти - последовательность -->
            <div v-if="currentQ.type === 'memory' && currentQ.id === 1" class="memory-test">
              <h4>{{ currentQ.question }}</h4>

              <div v-if="showSequence" class="sequence-display">
                <div class="sequence-items">
                  <div
                      v-for="(item, index) in currentQ.sequence"
                      :key="index"
                      class="sequence-item"
                  >
                    {{ item }}
                  </div>
                </div>
                <p class="sequence-hint">Запомните последовательность!</p>
              </div>

              <div v-else class="sequence-input">
                <p>Воспроизведите последовательность:</p>
                <div class="sequence-options">
                  <div
                      v-for="item in ['🌍', '🪐', '☄️', '🌕', '⭐', '🚀']"
                      :key="item"
                      class="sequence-option"
                      @click="handleMemoryItemClick(item)"
                  >
                    {{ item }}
                  </div>
                </div>

                <div v-if="currentQ.userSequence && currentQ.userSequence.length > 0" class="user-sequence">
                  <p>Ваш выбор:</p>
                  <div class="user-sequence-items">
                    <div
                        v-for="(item, index) in currentQ.userSequence"
                        :key="index"
                        class="user-sequence-item"
                    >
                      {{ item }}
                    </div>
                  </div>
                  <button
                      class="btn btn-secondary"
                      @click="resetMemorySequence"
                  >
                    <i class="fas fa-redo"></i> Сбросить
                  </button>
                </div>

                <div v-if="currentQ.completed" class="memory-feedback">
                  <div v-if="currentQ.answer === 1" class="correct-answer">
                    <i class="fas fa-check-circle"></i> Отлично! Вы запомнили последовательность!
                  </div>
                  <div v-else class="incorrect-answer">
                    <i class="fas fa-times-circle"></i> Порядок был: Земля, Сатурн, Комета, Луна
                  </div>
                </div>
              </div>
            </div>

            <!-- Тест памяти - числа -->
            <div v-if="currentQ.type === 'memory' && currentQ.id === 2" class="memory-test">
              <h4>{{ currentQ.question }}</h4>

              <div v-if="showNumbers" class="numbers-display">
                <div class="numbers-grid">
                  <div
                      v-for="(number, index) in memoryNumbers"
                      :key="index"
                      class="number-item"
                  >
                    {{ number }}
                  </div>
                </div>
                <p class="numbers-hint">Запомните числа!</p>
              </div>

              <div v-else class="numbers-input">
                <p>Какие числа вы видели? Введите все 4 числа:</p>
                <div class="number-input-grid">
                  <div
                      v-for="n in 4"
                      :key="n"
                      class="number-input-wrapper"
                  >
                    <label>Число {{ n }}:</label>
                    <input
                        type="number"
                        :value="currentQ.answer ? currentQ.answer[n-1] : ''"
                        @input="(e) => handleMemoryNumberInput(n-1, e.target.value)"
                        min="0"
                        max="9"
                        class="number-input"
                        :disabled="currentQ.completed"
                    />
                  </div>
                </div>

                <div v-if="currentQ.completed" class="memory-feedback">
                  <div v-if="currentQ.answer && currentQ.correctNumbers &&
                           currentQ.answer.every((num, idx) => num === currentQ.correctNumbers[idx])"
                       class="correct-answer">
                    <i class="fas fa-check-circle"></i> Супер память! Все числа верные!
                  </div>
                  <div v-else class="incorrect-answer">
                    <i class="fas fa-times-circle"></i> Правильные числа были: {{ currentQ.correctNumbers?.join(', ') }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Тест знаний -->
            <div v-if="currentQ.type === 'knowledge'" class="knowledge-test">
              <h4>{{ currentQ.question }}</h4>

              <div class="knowledge-options">
                <div
                    v-for="(option, index) in currentQ.options"
                    :key="index"
                    class="knowledge-option"
                    :class="{
                    selected: currentQ.answer === index,
                    correct: currentQ.completed && index === currentQ.correctIndex
                  }"
                    @click="handleKnowledgeAnswer(index)"
                    :disabled="currentQ.completed"
                >
                  <div class="option-letter">{{ String.fromCharCode(65 + index) }}</div>
                  <div class="option-text">{{ option }}</div>
                </div>
              </div>

              <div v-if="currentQ.completed" class="knowledge-feedback">
                <div v-if="currentQ.answer === currentQ.correctIndex" class="correct-answer">
                  <i class="fas fa-check-circle"></i> Правильно! +30 очков
                </div>
                <div v-else class="incorrect-answer">
                  <i class="fas fa-times-circle"></i> Неправильно. Правильный ответ: {{ currentQ.options[currentQ.correctIndex] }}
                </div>
              </div>
            </div>
          </div>

          <div class="test-navigation">
            <div class="time-info" v-if="currentQ.completed && currentQ.time">
              <i class="fas fa-clock"></i>
              Время: {{ currentQ.time }} мс
            </div>
            <button
                v-if="currentQ.completed && !(currentQ.type === 'memory' && currentQ.id === 2 && currentQ.answer?.length < 4)"
                class="btn btn-primary"
                @click="nextQuestion"
            >
              {{ currentQuestion < currentTest.questions.length - 1 ? 'Следующий вопрос' : 'Завершить категорию' }}
              <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>

        <div v-if="testCompleted" class="results-screen">
          <div class="results-content">
            <div class="results-header">
              <div class="results-badge">
                <i class="fas" :class="{
                  'fa-user-astronaut': totalScore >= 180,
                  'fa-user-graduate': totalScore >= 120,
                  'fa-user-tie': totalScore >= 80,
                  'fa-user': totalScore < 80
                }"></i>
              </div>
              <h3>Тестирование завершено!</h3>
              <p class="results-status">Ваш статус: <strong>{{ astronautStatus }}</strong></p>
            </div>

            <div class="results-score">
              <div class="total-score">
                <h4>Итоговый результат:</h4>
                <div class="score-circle">
                  <span class="score-number">{{ totalScore }}</span>
                  <span class="score-label">очков</span>
                </div>
              </div>

              <div class="category-scores">
                <h4>Результаты по категориям:</h4>
                <div class="scores-grid">
                  <div v-for="category in testCategories" :key="category.id" class="category-score-item">
                    <div class="category-score-header">
                      <i :class="`fas ${category.icon}`"></i>
                      <h5>{{ category.name }}</h5>
                    </div>
                    <div class="score-bar">
                      <div
                          class="score-fill"
                          :style="{ width: `${(category.score / (category.questions.length * 50)) * 100}%` }"
                      ></div>
                    </div>
                    <div class="score-value">{{ category.score }} очков</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="results-analysis">
              <h4>Анализ результатов:</h4>
              <div class="analysis-grid">
                <div class="analysis-item" v-if="totalScore >= 180">
                  <i class="fas fa-check-circle"></i>
                  <p>Отличные результаты! Вы обладаете всеми качествами космонавта!</p>
                </div>
                <div class="analysis-item" v-else-if="totalScore >= 120">
                  <i class="fas fa-check"></i>
                  <p>Хорошие результаты! Продолжайте тренироваться для улучшения навыков.</p>
                </div>
                <div class="analysis-item" v-else-if="totalScore >= 80">
                  <i class="fas fa-star"></i>
                  <p>Неплохо! Изучайте космос и тренируйте память с реакцией.</p>
                </div>
                <div class="analysis-item" v-else>
                  <i class="fas fa-rocket"></i>
                  <p>Начните с изучения истории космонавтики и простых упражнений.</p>
                </div>
              </div>
            </div>

            <div class="results-actions">
              <button class="btn btn-primary" @click="startTest">
                <i class="fas fa-redo"></i> Пройти тест снова
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mission-container {
  background: white;
  border-radius: var(--border-radius);
  padding: 30px;
  box-shadow: var(--box-shadow);
}

.mission-header {
  text-align: center;
  margin-bottom: 30px;
}

.mission-header h2 {
  color: var(--primary-color);
  margin-bottom: 10px;
}

.test-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  min-height: 600px;
}

@media (max-width: 992px) {
  .test-container {
    grid-template-columns: 1fr;
  }
}

.test-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.astronaut-profile {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  padding: 25px;
  border-radius: var(--border-radius);
  text-align: center;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  font-size: 2.5rem;
}

.astronaut-profile h4 {
  margin-bottom: 5px;
}

.status {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 15px;
}

.profile-score {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 15px;
  border-radius: 20px;
}

.progress-tracker {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.progress-bar {
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary-color), var(--accent-color));
  transition: width 0.3s ease;
}

.test-categories {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: var(--transition);
  cursor: pointer;
}

.category-item.active {
  border-color: var(--secondary-color);
  background: #f0f8ff;
  transform: translateX(5px);
}

.category-item.completed {
  border-color: var(--success-color);
  background: #e8f5e9;
}

.category-icon {
  width: 40px;
  height: 40px;
  background: var(--secondary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.category-item.completed .category-icon {
  background: var(--success-color);
}

.category-info h6 {
  margin: 0 0 5px 0;
  color: var(--dark-color);
}

.category-info p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--gray-color);
}

.category-score {
  font-size: 0.8rem;
  font-weight: bold;
  color: var(--accent-color);
  margin-top: 5px;
}

.test-main {
  background: #f8f9fa;
  border-radius: var(--border-radius);
  padding: 30px;
}

.welcome-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.welcome-content {
  text-align: center;
  max-width: 500px;
}

.welcome-content i {
  font-size: 4rem;
  color: var(--secondary-color);
  margin-bottom: 20px;
}

.test-overview {
  text-align: left;
  margin: 25px 0;
  padding: 0;
  list-style: none;
}

.test-overview li {
  margin-bottom: 15px;
  padding: 15px;
  background: white;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-overview i {
  font-size: 1.5rem;
  color: var(--accent-color);
}

.btn-large {
  padding: 15px 40px;
  font-size: 1.1rem;
}

.test-area {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.test-header {
  margin-bottom: 30px;
  text-align: center;
}

.test-header h3 {
  color: var(--primary-color);
  margin-bottom: 10px;
}

.test-progress {
  display: inline-block;
  background: var(--secondary-color);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  margin-top: 10px;
}

.question-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.reaction-test,
.memory-test,
.knowledge-test {
  text-align: center;
}

.reaction-test h4,
.memory-test h4,
.knowledge-test h4 {
  margin-bottom: 30px;
  color: var(--dark-color);
}

.reaction-options {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.reaction-option {
  width: 120px;
  height: 120px;
  background: white;
  border: 3px solid #e0e0e0;
  border-radius: var(--border-radius);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}

.reaction-option:hover {
  transform: translateY(-5px);
  border-color: var(--secondary-color);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.2);
}

.reaction-option.selected {
  border-color: var(--accent-color);
  background: #fff5f7;
}

.option-emoji {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.option-label {
  font-size: 0.9rem;
  color: var(--gray-color);
}

.reaction-button-container {
  margin: 40px 0;
}

.reaction-button {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}

.reaction-button.active {
  background: var(--success-color);
  animation: pulse 1s infinite;
  color: white;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.reaction-button .waiting {
  text-align: center;
}

.reaction-button .waiting i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: var(--gray-color);
}

.reaction-button .active-signal i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: white;
}

.reaction-result {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: var(--border-radius);
}

.reaction-result p {
  margin: 5px 0;
}

.fast-reaction {
  color: var(--success-color);
  font-weight: bold;
}

.good-reaction {
  color: #ff9800;
  font-weight: bold;
}

.normal-reaction {
  color: var(--secondary-color);
  font-weight: bold;
}

.reaction-feedback,
.memory-feedback,
.knowledge-feedback {
  margin-top: 30px;
  padding: 20px;
  border-radius: var(--border-radius);
}

.correct-answer {
  background: #e8f5e9;
  color: var(--success-color);
  padding: 15px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.incorrect-answer {
  background: #ffebee;
  color: var(--accent-color);
  padding: 15px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.sequence-display,
.numbers-display {
  margin: 30px 0;
}

.sequence-items,
.numbers-grid {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.sequence-item,
.number-item {
  width: 80px;
  height: 80px;
  background: white;
  border: 3px solid var(--secondary-color);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  animation: bounceIn 0.5s ease;
}

@keyframes bounceIn {
  0% { transform: scale(0); }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.number-item {
  font-size: 2rem;
  font-weight: bold;
}

.sequence-hint,
.numbers-hint {
  color: var(--gray-color);
  font-style: italic;
}

.sequence-input,
.numbers-input {
  margin-top: 30px;
}

.sequence-options {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.sequence-option {
  width: 70px;
  height: 70px;
  background: white;
  border: 2px solid var(--secondary-color);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  cursor: pointer;
  transition: var(--transition);
}

.sequence-option:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.2);
}

.user-sequence {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: var(--border-radius);
}

.user-sequence-items {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 15px 0;
}

.user-sequence-item {
  width: 60px;
  height: 60px;
  background: var(--secondary-color);
  color: white;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.number-input-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 20px 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.number-input-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.number-input-wrapper label {
  font-weight: 600;
  color: var(--dark-color);
}

.number-input {
  width: 80px;
  height: 60px;
  border: 2px solid var(--secondary-color);
  border-radius: var(--border-radius);
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.number-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.knowledge-options {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
  max-width: 600px;
  margin: 30px auto;
}

.knowledge-option {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.knowledge-option:hover:not(.correct) {
  transform: translateX(10px);
  border-color: var(--secondary-color);
}

.knowledge-option.selected {
  border-color: var(--secondary-color);
  background: #f0f8ff;
}

.knowledge-option.correct {
  border-color: var(--success-color);
  background: #e8f5e9;
}

.option-letter {
  width: 30px;
  height: 30px;
  background: var(--secondary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.knowledge-option.correct .option-letter {
  background: var(--success-color);
}

.option-text {
  flex: 1;
}

.test-navigation {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--gray-color);
}

.results-screen {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.results-content {
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.results-badge {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 3rem;
}

.results-status {
  font-size: 1.2rem;
  margin: 15px 0 30px;
}

.total-score {
  margin: 30px 0;
}

.score-circle {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
}

.score-number {
  font-size: 3rem;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.category-scores {
  margin: 30px 0;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.category-score-item {
  background: white;
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.category-score-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.category-score-header i {
  color: var(--secondary-color);
  font-size: 1.2rem;
}

.category-score-header h5 {
  margin: 0;
  font-size: 0.9rem;
}

.score-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary-color), var(--accent-color));
}

.score-value {
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--accent-color);
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.analysis-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 15px;
}

.analysis-item i {
  color: var(--success-color);
  font-size: 1.2rem;
}

.results-actions {
  margin-top: 30px;
}
</style>
