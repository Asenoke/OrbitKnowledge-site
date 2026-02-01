<script setup>
import { ref, computed } from 'vue'

const parts = ref([
  { id: 1, name: 'Фюзеляж', description: 'Основной корпус самолёта', image: '✈️', used: false },
  { id: 2, name: 'Крылья', description: 'Подъемная поверхность 12м', image: '🪽', used: false },
  { id: 3, name: 'Двигатель', description: 'Поршневой двигатель 30л.с.', image: '⚙️', used: false },
  { id: 4, name: 'Пропеллер', description: 'Деревянный, 2.4м', image: '🌀', used: false },
  { id: 5, name: 'Шасси', description: 'Колёса и рама', image: '🛞', used: false },
  { id: 6, name: 'Руль высоты', description: 'Для управления тангажом', image: '↕️', used: false },
  { id: 7, name: 'Элероны', description: 'Для крена и поворотов', image: '↔️', used: false },
  { id: 8, name: 'Кабина', description: 'Пилотское место', image: '👨‍✈️', used: false }
])

const assembledParts = ref([])
const currentStep = ref(1)
const score = ref(0)
const isCompleted = ref(false)
const facts = ref([
  'Братья Райт использовали велосипедную цепь для передачи мощности от двигателя к пропеллеру',
  'Первый полёт длился всего 12 секунд и преодолел 36 метров',
  'Самолёт весил 274 кг и был построен из ели и муслина',
  'Управление осуществлялось системой тросов и рычагов'
])

const steps = [
  { id: 1, title: 'Основа', description: 'Соберите фюзеляж и установите на него крылья' },
  { id: 2, title: 'Двигатель', description: 'Добавьте двигатель и пропеллер' },
  { id: 3, title: 'Управление', description: 'Установите органы управления' },
  { id: 4, title: 'Завершение', description: 'Добавьте шасси и кабину' }
]

const usedParts = computed(() => {
  return parts.value.filter(part => part.used)
})

const availableParts = computed(() => {
  return parts.value.filter(part => !part.used)
})

const checkStepCompletion = () => {
  switch(currentStep.value) {
    case 1:
      return assembledParts.value.some(p => p.id === 1) && assembledParts.value.some(p => p.id === 2)
    case 2:
      return assembledParts.value.some(p => p.id === 3) && assembledParts.value.some(p => p.id === 4)
    case 3:
      return assembledParts.value.some(p => p.id === 6) && assembledParts.value.some(p => p.id === 7)
    case 4:
      return assembledParts.value.some(p => p.id === 5) && assembledParts.value.some(p => p.id === 8)
  }
  return false
}

const usePart = (part) => {
  if (part.used) return

  const partIndex = parts.value.findIndex(p => p.id === part.id)
  parts.value[partIndex].used = true
  assembledParts.value.push(part)
  score.value += 10

  // Проверяем, можно ли перейти к следующему шагу
  if (checkStepCompletion()) {
    if (currentStep.value < 4) {
      setTimeout(() => {
        currentStep.value++
        score.value += 50
      }, 1000)
    } else {
      setTimeout(() => {
        isCompleted.value = true
        score.value += 100
      }, 1000)
    }
  }
}

const removePart = (part) => {
  const partIndex = parts.value.findIndex(p => p.id === part.id)
  parts.value[partIndex].used = false
  assembledParts.value = assembledParts.value.filter(p => p.id !== part.id)
  score.value = Math.max(0, score.value - 5)
}

const resetMission = () => {
  parts.value.forEach(part => part.used = false)
  assembledParts.value = []
  currentStep.value = 1
  score.value = 0
  isCompleted.value = false
}
</script>

<template>
  <div class="mission-container">
    <div class="mission-header">
      <h2><i class="fas fa-cogs"></i> Миссия: Собери свой биплан</h2>
      <p>Помогите братьям Райт построить первый управляемый самолёт!</p>
    </div>

    <div class="mission-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${(assembledParts.length / 8) * 100}%` }"></div>
      </div>
      <div class="progress-info">
        <span>Собрано: {{ assembledParts.length }}/8 частей</span>
        <span class="score">Очки: {{ score }}</span>
      </div>
    </div>

    <div class="mission-content">
      <div class="current-step">
        <h3>Шаг {{ currentStep }}: {{ steps[currentStep-1].title }}</h3>
        <p>{{ steps[currentStep-1].description }}</p>

        <div v-if="checkStepCompletion()" class="step-complete">
          <i class="fas fa-check-circle"></i> Шаг выполнен! Переход к следующему...
        </div>
      </div>

      <div class="workshop">
        <div class="assembly-area">
          <h4>Сборка самолёта</h4>
          <div class="airplane-preview">
            <div class="airplane" :class="{ 'animate': isCompleted }">
              <div class="airplane-body">
                <div v-for="part in assembledParts" :key="part.id" class="airplane-part" :title="part.name">
                  {{ part.image }}
                </div>
              </div>
            </div>
          </div>

          <div class="assembled-parts">
            <h5>Установленные детали:</h5>
            <div v-if="assembledParts.length > 0" class="parts-list">
              <div v-for="part in assembledParts" :key="part.id" class="part-item assembled" @click="removePart(part)">
                <span class="part-icon">{{ part.image }}</span>
                <span class="part-name">{{ part.name }}</span>
                <i class="fas fa-times remove-btn"></i>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>Детали ещё не добавлены</p>
            </div>
          </div>
        </div>

        <div class="parts-inventory">
          <h4>Детали в мастерской</h4>
          <div class="parts-grid">
            <div v-for="part in availableParts" :key="part.id" class="part-item" @click="usePart(part)">
              <div class="part-icon">{{ part.image }}</div>
              <div class="part-info">
                <h5>{{ part.name }}</h5>
                <p>{{ part.description }}</p>
              </div>
              <button class="btn-use"><i class="fas fa-plus"></i> Использовать</button>
            </div>
          </div>
        </div>
      </div>

      <div class="mission-facts">
        <h4><i class="fas fa-lightbulb"></i> Интересные факты:</h4>
        <div class="facts-list">
          <div v-for="(fact, index) in facts" :key="index" class="fact-item">
            <i class="fas fa-star"></i> {{ fact }}
          </div>
        </div>
      </div>

      <div v-if="isCompleted" class="completion-screen">
        <div class="completion-content">
          <i class="fas fa-trophy"></i>
          <h3>Поздравляем! Биплан собран!</h3>
          <p>Вы успешно собрали самолёт братьев Райт. Теперь он готов к своему историческому полёту!</p>
          <div class="final-score">
            <p>Итоговый счёт: <span class="score-highlight">{{ score }} очков</span></p>
          </div>
          <button class="btn btn-primary" @click="resetMission">
            <i class="fas fa-redo"></i> Попробовать снова
          </button>
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

.mission-progress {
  margin-bottom: 30px;
}

.progress-bar {
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary-color), var(--accent-color));
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  color: var(--gray-color);
}

.score {
  color: var(--accent-color);
  font-weight: bold;
}

.workshop {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .workshop {
    grid-template-columns: 1fr;
  }
}

.assembly-area {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.airplane-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 150px;
  background: white;
  border-radius: var(--border-radius);
  margin: 20px 0;
  padding: 20px;
}

.airplane {
  font-size: 3rem;
  transform-origin: center;
}

.airplane.animate {
  animation: fly 3s ease-in-out infinite;
}

@keyframes fly {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.assembled-parts {
  margin-top: 20px;
}

.parts-inventory {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.parts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.part-item {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
}

.part-item:hover {
  transform: translateY(-5px);
  border-color: var(--secondary-color);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.1);
}

.part-item.assembled {
  background: #e8f5e9;
  border-color: var(--success-color);
  flex-direction: row;
  justify-content: space-between;
  text-align: left;
}

.part-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.part-info h5 {
  margin: 0 0 5px 0;
  color: var(--primary-color);
}

.part-info p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--gray-color);
}

.btn-use {
  background: var(--secondary-color);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 10px;
  transition: var(--transition);
}

.btn-use:hover {
  background: var(--primary-color);
}

.remove-btn {
  color: var(--accent-color);
  cursor: pointer;
  padding: 5px;
}

.mission-facts {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  padding: 20px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
}

.facts-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.fact-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-complete {
  background: var(--success-color);
  color: white;
  padding: 10px 15px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.completion-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

.completion-content {
  background: white;
  padding: 40px;
  border-radius: var(--border-radius);
  text-align: center;
  max-width: 500px;
  width: 90%;
  animation: scaleIn 0.3s ease;
}

.completion-content i {
  font-size: 4rem;
  color: #ffd700;
  margin-bottom: 20px;
}

.score-highlight {
  font-size: 2rem;
  color: var(--accent-color);
  font-weight: bold;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
