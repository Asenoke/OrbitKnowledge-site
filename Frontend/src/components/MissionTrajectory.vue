<script setup>
import { ref, onMounted } from 'vue'

const phases = ref([
  {
    id: 1,
    name: 'Вывод на орбиту',
    description: 'Рассчитайте угол запуска ракеты',
    targetAngle: 85,
    userAngle: 0,
    completed: false,
    hint: 'Угол должен быть близок к вертикальному'
  },
  {
    id: 2,
    name: 'Транслунная инъекция',
    description: 'Рассчитайте момент включения двигателя',
    targetTime: 2.5,
    userTime: 0,
    completed: false,
    hint: 'Двигатель включают на околоземной орбите'
  },
  {
    id: 3,
    name: 'Коррекция курса',
    description: 'Рассчитайте длительность импульса коррекции',
    targetImpulse: 3.2,
    userImpulse: 0,
    completed: false,
    hint: 'Импульс зависит от массы корабля'
  },
  {
    id: 4,
    name: 'Выход на лунную орбиту',
    description: 'Рассчитайте скорость торможения',
    targetSpeed: 1.6,
    userSpeed: 0,
    completed: false,
    hint: 'Слишком большая скорость - проскочите мимо Луны'
  }
])

const currentPhase = ref(0)
const score = ref(0)
const totalScore = ref(400)
const isCompleted = ref(false)
const simulationRunning = ref(false)
const trajectory = ref([])

const missionInfo = ref([
  { title: 'Масса корабля', value: '28,000 кг' },
  { title: 'Расстояние до Луны', value: '384,400 км' },
  { title: 'Скорость у Земли', value: '28,000 км/ч' },
  { title: 'Время полёта', value: '3 дня' }
])

const startMission = () => {
  currentPhase.value = 0
  score.value = 0
  isCompleted.value = false
  phases.value.forEach(phase => {
    phase.completed = false
    phase.userAngle = 0
    phase.userTime = 0
    phase.userImpulse = 0
    phase.userSpeed = 0
  })
  trajectory.value = []
}

const checkPhase = () => {
  const phase = phases.value[currentPhase.value]
  let isCorrect = false

  switch(phase.id) {
    case 1:
      isCorrect = Math.abs(phase.userAngle - phase.targetAngle) <= 5
      break
    case 2:
      isCorrect = Math.abs(phase.userTime - phase.targetTime) <= 0.5
      break
    case 3:
      isCorrect = Math.abs(phase.userImpulse - phase.targetImpulse) <= 0.3
      break
    case 4:
      isCorrect = Math.abs(phase.userSpeed - phase.targetSpeed) <= 0.2
      break
  }

  if (isCorrect) {
    phase.completed = true
    score.value += 100

    if (currentPhase.value < phases.value.length - 1) {
      currentPhase.value++
    } else {
      completeMission()
    }

    addTrajectoryPoint()
    return true
  }

  return false
}

const completeMission = () => {
  isCompleted.value = true
  simulationRunning.value = true
  setTimeout(() => {
    simulationRunning.value = false
  }, 5000)
}

const addTrajectoryPoint = () => {
  const points = [
    { x: 10, y: 90, label: 'Запуск' },
    { x: 30, y: 30, label: 'Орбита Земли' },
    { x: 50, y: 50, label: 'Транслунная' },
    { x: 70, y: 70, label: 'Коррекция' },
    { x: 90, y: 30, label: 'Лунная орбита' }
  ]

  if (trajectory.value.length < points.length) {
    trajectory.value.push(points[trajectory.value.length])
  }
}

const simulateFlight = () => {
  if (trajectory.value.length < 5) return ''

  const progress = Date.now() / 1000 % 5
  const segment = Math.floor(progress)
  const segmentProgress = progress % 1

  const start = trajectory.value[segment]
  const end = trajectory.value[segment + 1] || trajectory.value[0]

  const x = start.x + (end.x - start.x) * segmentProgress
  const y = start.y + (end.y - start.y) * segmentProgress

  return `translate(${x}%, ${y}%)`
}

onMounted(() => {
  startMission()
  addTrajectoryPoint()
})
</script>

<template>
  <div class="mission-container">
    <div class="mission-header">
      <h2><i class="fas fa-moon"></i> Миссия: Рассчитай траекторию</h2>
      <p>Помогите «Аполлону-11» добраться до Луны. Рассчитайте параметры полёта!</p>
    </div>

    <div class="mission-layout">
      <div class="control-panel">
        <div class="phase-info">
          <h3>Фаза {{ currentPhase + 1 }}: {{ phases[currentPhase].name }}</h3>
          <p>{{ phases[currentPhase].description }}</p>
          <div class="hint-box">
            <i class="fas fa-lightbulb"></i> Подсказка: {{ phases[currentPhase].hint }}
          </div>
        </div>

        <div class="calculator">
          <h4>Калькулятор параметров:</h4>

          <div v-if="phases[currentPhase].id === 1" class="input-group">
            <label>Угол запуска (°):</label>
            <div class="slider-container">
              <input
                  type="range"
                  min="60"
                  max="90"
                  step="1"
                  v-model="phases[currentPhase].userAngle"
                  class="slider"
              >
              <div class="slider-value">{{ phases[currentPhase].userAngle }}°</div>
            </div>
            <div class="angle-visualization">
              <div class="angle-line" :style="{ transform: `rotate(${phases[currentPhase].userAngle}deg)` }"></div>
              <div class="angle-label">{{ phases[currentPhase].userAngle }}°</div>
            </div>
          </div>

          <div v-if="phases[currentPhase].id === 2" class="input-group">
            <label>Время включения (мин):</label>
            <div class="slider-container">
              <input
                  type="range"
                  min="1"
                  max="5"
                  step="0.1"
                  v-model="phases[currentPhase].userTime"
                  class="slider"
              >
              <div class="slider-value">{{ phases[currentPhase].userTime }} мин</div>
            </div>
          </div>

          <div v-if="phases[currentPhase].id === 3" class="input-group">
            <label>Импульс коррекции (м/с):</label>
            <div class="slider-container">
              <input
                  type="range"
                  min="1"
                  max="5"
                  step="0.1"
                  v-model="phases[currentPhase].userImpulse"
                  class="slider"
              >
              <div class="slider-value">{{ phases[currentPhase].userImpulse }} м/с</div>
            </div>
          </div>

          <div v-if="phases[currentPhase].id === 4" class="input-group">
            <label>Скорость торможения (км/с):</label>
            <div class="slider-container">
              <input
                  type="range"
                  min="0.5"
                  max="3"
                  step="0.1"
                  v-model="phases[currentPhase].userSpeed"
                  class="slider"
              >
              <div class="slider-value">{{ phases[currentPhase].userSpeed }} км/с</div>
            </div>
          </div>

          <button class="btn btn-primary" @click="checkPhase" :disabled="phases[currentPhase].completed">
            <i class="fas fa-check"></i> Проверить расчёт
          </button>
        </div>

        <div class="mission-data">
          <h4>Данные миссии:</h4>
          <div class="data-grid">
            <div v-for="item in missionInfo" :key="item.title" class="data-item">
              <span class="data-label">{{ item.title }}:</span>
              <span class="data-value">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="simulation-area">
        <div class="simulation-header">
          <h4>Симуляция траектории</h4>
          <div class="score-display">
            Очки: {{ score }}/{{ totalScore }}
          </div>
        </div>

        <div class="space-simulation">
          <div class="celestial-body earth">
            <i class="fas fa-globe-americas"></i>
            <span class="label">Земля</span>
          </div>

          <div class="celestial-body moon">
            <i class="fas fa-moon"></i>
            <span class="label">Луна</span>
          </div>

          <div class="trajectory-path">
            <svg width="100%" height="100%" style="position: absolute; top: 0; left: 0;">
              <path
                  v-if="trajectory.length > 1"
                  :d="`M ${trajectory[0].x}% ${trajectory[0].y}%
                     C ${trajectory[1].x}% ${trajectory[1].y}%
                     ${trajectory[2]?.x || 50}% ${trajectory[2]?.y || 50}%
                     ${trajectory[3]?.x || 70}% ${trajectory[3]?.y || 70}%
                     L ${trajectory[4]?.x || 90}% ${trajectory[4]?.y || 30}%`"
                  stroke="var(--secondary-color)"
                  stroke-width="2"
                  fill="none"
                  stroke-dasharray="5,5"
              />
            </svg>
          </div>

          <div
              class="spacecraft"
              :style="{ transform: simulationRunning ? simulateFlight() : '' }"
              :class="{ flying: simulationRunning }"
          >
            <i class="fas fa-rocket"></i>
          </div>

          <div class="phase-markers">
            <div
                v-for="(phase, index) in phases"
                :key="phase.id"
                class="phase-marker"
                :class="{ completed: phase.completed }"
                :style="{ left: `${20 + index * 20}%`, top: `${index % 2 === 0 ? 40 : 60}%` }"
            >
              <div class="marker-dot"></div>
              <div class="marker-label">{{ phase.name }}</div>
            </div>
          </div>
        </div>

        <div class="phases-progress">
          <h5>Прогресс по фазам:</h5>
          <div class="phases-list">
            <div
                v-for="phase in phases"
                :key="phase.id"
                class="phase-item"
                :class="{ active: phase.id === phases[currentPhase].id, completed: phase.completed }"
            >
              <div class="phase-number">{{ phase.id }}</div>
              <div class="phase-name">{{ phase.name }}</div>
              <div class="phase-status">
                <i v-if="phase.completed" class="fas fa-check-circle"></i>
                <i v-else class="fas fa-circle"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isCompleted" class="completion-screen">
      <div class="completion-content">
        <div class="success-animation">
          <i class="fas fa-flag-checkered"></i>
          <div class="confetti"></div>
        </div>
        <h3>Миссия выполнена!</h3>
        <p>Вы успешно рассчитали траекторию полёта к Луне. «Аполлон-11» достиг лунной орбиты!</p>

        <div class="results">
          <div class="result-item">
            <i class="fas fa-chart-line"></i>
            <span>Точность расчётов: <strong>{{ Math.round((score / totalScore) * 100) }}%</strong></span>
          </div>
          <div class="result-item">
            <i class="fas fa-tachometer-alt"></i>
            <span>Эффективность траектории: <strong>{{ 100 - Math.abs(score - totalScore) }}%</strong></span>
          </div>
        </div>

        <div class="completion-actions">
          <button class="btn btn-primary" @click="startMission">
            <i class="fas fa-redo"></i> Пройти заново
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

.mission-layout {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 30px;
}

@media (max-width: 992px) {
  .mission-layout {
    grid-template-columns: 1fr;
  }
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.phase-info {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  padding: 20px;
  border-radius: var(--border-radius);
}

.hint-box {
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 15px;
  border-radius: 8px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.calculator {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.input-group {
  margin-bottom: 25px;
}

.input-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: var(--dark-color);
}

.slider-container {
  position: relative;
  margin: 20px 0;
}

.slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  background: #e0e0e0;
  border-radius: 4px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px;
  height: 24px;
  background: var(--secondary-color);
  border-radius: 50%;
  cursor: pointer;
  transition: var(--transition);
}

.slider::-webkit-slider-thumb:hover {
  background: var(--primary-color);
  transform: scale(1.1);
}

.slider-value {
  text-align: center;
  margin-top: 10px;
  font-weight: bold;
  color: var(--accent-color);
  font-size: 1.2rem;
}

.angle-visualization {
  width: 150px;
  height: 150px;
  position: relative;
  margin: 20px auto;
  border: 2px solid #e0e0e0;
  border-radius: 50%;
}

.angle-line {
  position: absolute;
  bottom: 50%;
  left: 50%;
  width: 2px;
  height: 60px;
  background: var(--accent-color);
  transform-origin: bottom center;
  transition: transform 0.3s ease;
}

.angle-label {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-weight: bold;
  color: var(--dark-color);
}

.mission-data {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: white;
  border-radius: 8px;
}

.data-label {
  color: var(--gray-color);
}

.data-value {
  font-weight: 600;
  color: var(--primary-color);
}

.simulation-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.simulation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-display {
  background: var(--accent-color);
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
}

.space-simulation {
  position: relative;
  height: 400px;
  background: linear-gradient(135deg, #0a0e2a, #1a237e);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.celestial-body {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  transition: var(--transition);
}

.earth {
  top: 20%;
  left: 10%;
  font-size: 3rem;
  animation: pulse 2s infinite;
}

.moon {
  top: 20%;
  right: 10%;
  font-size: 2rem;
  animation: pulse 2s infinite 1s;
}

.label {
  margin-top: 10px;
  font-size: 0.8rem;
  opacity: 0.8;
}

.spacecraft {
  position: absolute;
  top: 50%;
  left: 15%;
  font-size: 2rem;
  color: var(--secondary-color);
  transform-origin: center;
  transition: transform 2s linear;
}

.spacecraft.flying {
  animation: spacecraftGlow 1s infinite alternate;
}

@keyframes spacecraftGlow {
  from {
    filter: drop-shadow(0 0 5px var(--secondary-color));
  }
  to {
    filter: drop-shadow(0 0 15px var(--accent-color));
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.trajectory-path {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.phase-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.phase-marker {
  position: absolute;
  transform: translate(-50%, -50%);
}

.marker-dot {
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  border: 2px solid var(--secondary-color);
}

.phase-marker.completed .marker-dot {
  background: var(--success-color);
  border-color: var(--success-color);
}

.marker-label {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 0.7rem;
  white-space: nowrap;
  opacity: 0.8;
}

.phases-progress {
  background: #f8f9fa;
  padding: 20px;
  border-radius: var(--border-radius);
}

.phases-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.phase-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 8px;
  transition: var(--transition);
}

.phase-item.active {
  border: 2px solid var(--secondary-color);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.2);
}

.phase-item.completed {
  background: #e8f5e9;
}

.phase-number {
  width: 30px;
  height: 30px;
  background: var(--secondary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 5px;
}

.phase-item.completed .phase-number {
  background: var(--success-color);
}

.phase-name {
  font-size: 0.8rem;
  text-align: center;
  margin-bottom: 5px;
}

.phase-status {
  color: var(--success-color);
}

.phase-item:not(.completed) .phase-status {
  color: #e0e0e0;
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
}

.completion-content {
  background: white;
  padding: 40px;
  border-radius: var(--border-radius);
  text-align: center;
  max-width: 500px;
  width: 90%;
  animation: slideInUp 0.3s ease;
}

.success-animation {
  position: relative;
  margin-bottom: 20px;
}

.success-animation i {
  font-size: 4rem;
  color: #ffd700;
  animation: bounce 1s ease infinite;
}

.confetti {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.results {
  margin: 30px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: var(--border-radius);
}

.result-item i {
  color: var(--secondary-color);
  font-size: 1.2rem;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
