<script setup>
import { ref, onMounted, watch, computed } from "vue";
import HeaderComponent from "./components/HeaderComponent.vue";
import FooterComponent from "./components/FooterComponent.vue";
import HeroCardComponent from "./components/HeroCardComponent.vue";
import TimelineItemComponent from "./components/TimelineItemComponent.vue";
import KBComponent from "./components/KBComponent.vue";
import ModalHeroComponent from "./components/ModalHeroComponent.vue";
import ProfileComponent from "./components/ProfileComponent.vue";
import AdminPanelComponent from "./components/AdminPanelComponent.vue";
import MissionBiplane from "./components/MissionBiplane.vue";
import MissionTrajectory from "./components/MissionTrajectory.vue";
import MissionAstronautTest from "./components/MissionAstronautTest.vue";
import axios from "axios";

// Основные данные
const timelineEvents = ref([]);
const heroes = ref([]);
const selectedHero = ref(null);
const isModalVisible = ref(false);

// Пагинация
const visibleHeroesCount = ref(3);
const heroesPerPage = 3;
const heroIsLoading = ref(false);
const hasMoreHeroes = ref(true);

const visibleEventsCount = ref(3);
const eventsPerPage = 3;
const timelineIsLoading = ref(false);
const hasMoreEvents = ref(true);

// URL API
const getUrlLineEvents = "http://127.0.0.1:8000/lineevent/getAllLineEvents?skip=0&limit=100";
const getUrlHeroes = "http://127.0.0.1:8000/heroes/getAllHeroes?skip=0&limit=100";

// Текущая секция - ИЗМЕНЕНО: работа с hash напрямую
const activeSection = ref('');
const activeMission = ref(null);

// Проверка авторизации
const isAuthenticated = computed(() => {
  return !!localStorage.getItem('auth_token')
})

// Проверка админ-статуса
const isAdmin = computed(() => {
  const role = localStorage.getItem('user_role')
  console.log('App: Checking admin status, role:', role)
  return role === 'ADMIN'
})

// Получение событий
const getLineEvents = async () => {
  try {
    timelineIsLoading.value = true;
    const response = await axios.get(getUrlLineEvents);
    timelineEvents.value = response.data;
    hasMoreEvents.value = timelineEvents.value.length > visibleEventsCount.value;
  } catch (error) {
    console.error("Ошибка при получении событий:", error);
  } finally {
    timelineIsLoading.value = false;
  }
};

// Получение героев
const getHeroes = async () => {
  try {
    heroIsLoading.value = true;
    const response = await axios.get(getUrlHeroes);
    heroes.value = response.data;
    hasMoreHeroes.value = heroes.value.length > visibleHeroesCount.value;
  } catch (error) {
    console.error("Ошибка при получении героев:", error);
  } finally {
    heroIsLoading.value = false;
  }
};

// Загрузка больше событий
const loadMoreEvents = () => {
  const newVisibleCount = visibleEventsCount.value + eventsPerPage;

  if (newVisibleCount >= timelineEvents.value.length) {
    visibleEventsCount.value = timelineEvents.value.length;
    hasMoreEvents.value = false;
  } else {
    visibleEventsCount.value = newVisibleCount;
    hasMoreEvents.value = true;
  }
};

// Загрузка больше героев
const loadMoreHeroes = () => {
  const newVisibleCount = visibleHeroesCount.value + heroesPerPage;

  if (newVisibleCount >= heroes.value.length) {
    visibleHeroesCount.value = heroes.value.length;
    hasMoreHeroes.value = false;
  } else {
    visibleHeroesCount.value = newVisibleCount;
    hasMoreHeroes.value = true;
  }
};

// Открытие модального окна героя
const openHeroModal = (heroData) => {
  selectedHero.value = heroData;
  isModalVisible.value = true;
};

// Закрытие модального окна
const closeHeroModal = () => {
  isModalVisible.value = false;
  setTimeout(() => {
    selectedHero.value = null;
  }, 300);
};

// Запуск миссии
const startMission = (missionName) => {
  console.log('Starting mission:', missionName);
  activeMission.value = missionName;
  activeSection.value = 'mission';
  // Обновляем URL без перезагрузки страницы
  window.history.pushState({}, '', `#mission`);
  // Прокрутка к началу страницы
  setTimeout(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, 100);
};

// Возврат с миссии
const backFromMission = () => {
  activeMission.value = null;
  activeSection.value = 'home';
  window.history.pushState({}, '', '#');
  // Прокрутка к блоку миссий
  setTimeout(() => {
    document.getElementById('missions')?.scrollIntoView({ behavior: 'smooth' });
  }, 100);
};

// Обработчик изменения хэша
const handleHashChange = () => {
  const hash = window.location.hash;
  console.log('App: Hash changed to:', hash);

  // Если hash пустой или начинается с #heroes, #missions и т.д. - это главная
  if (!hash || hash === '#' ||
      hash === '#heroes' ||
      hash === '#missions' ||
      hash === '#timeline' ||
      hash === '#future') {
    activeSection.value = 'home';
    activeMission.value = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (hash === '#mission') {
    // Оставляем для обработки в startMission
  } else {
    // Убираем # для сравнения
    const section = hash.replace('#', '');
    activeSection.value = section;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

// Назад на главную - ИЗМЕНЕНО
const backToHome = () => {
  window.location.hash = '';
  activeSection.value = 'home';
  activeMission.value = null;
};

// Отладка
const debugInfo = () => {
  console.log('App Debug Info:')
  console.log('Active section:', activeSection.value)
  console.log('Active mission:', activeMission.value)
  console.log('Current hash:', window.location.hash)
  console.log('Token exists:', !!localStorage.getItem('auth_token'))
  console.log('Token:', localStorage.getItem('auth_token')?.substring(0, 20) + '...')
  console.log('User role:', localStorage.getItem('user_role'))
  console.log('User data:', localStorage.getItem('user_data'))
  console.log('Is Admin:', isAdmin.value)
  console.log('Is Authenticated:', isAuthenticated.value)
}

// Инициализация
onMounted(() => {
  getLineEvents();
  getHeroes();

  // Инициализируем текущую секцию
  handleHashChange();

  // Слушаем изменения хэша
  window.addEventListener('hashchange', handleHashChange);

  debugInfo();
});

// Отслеживаем изменения activeSection для скролла
watch(activeSection, (newValue) => {
  console.log('App: Section changed to:', newValue)
  if (newValue === 'home') {
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  }
});
</script>

<template>
  <HeaderComponent />

  <!-- Главная страница -->
  <div v-if="activeSection === 'home'">
    <!-- Главный баннер -->
    <section class="hero">
      <div class="container">
        <div class="hero__content">
          <h1 class="hero-title">От <span class="text-gradient">мечты</span> — к <span class="text-gradient">звёздам</span></h1>
          <p class="hero-subtitle">Интерактивное путешествие по истории авиации и космонавтики для юных исследователей всех возрастов.</p>
          <div class="hero-buttons">
            <a href="#timeline" class="btn btn-primary">Начать путешествие <i class="fas fa-arrow-right"></i></a>
            <a href="#missions" class="btn btn-secondary">Попробовать миссию</a>
          </div>
          <div class="hero-stats">
            <div class="stat">
              <span class="stat-number">{{ timelineEvents.length }}+</span>
              <span class="stat-label">Событий</span>
            </div>
            <div class="stat">
              <span class="stat-number">{{ heroes.length }}+</span>
              <span class="stat-label">Героев</span>
            </div>
            <div class="stat">
              <span class="stat-number">3</span>
              <span class="stat-label">Миссий</span>
            </div>
          </div>
        </div>
        <div class="hero-image">
          <div class="floating-rocket">
            <i class="fas fa-rocket"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- Галерея Героев -->
    <section class="section" id="heroes">
      <div class="container">
        <h2 class="section-title"><i class="fas fa-user-astronaut"></i> Галерея Героев</h2>
        <p class="section-subtitle">Познакомьтесь с легендами, которые изменили небо и космос.</p>
        <div class="heroes-grid">
          <HeroCardComponent
              v-for="heroItem in heroes.slice(0, visibleHeroesCount)"
              :key="heroItem.id"
              :event="heroItem"
              @open-modal="openHeroModal"
          />
        </div>
        <div class="text-center">
          <button
              v-if="hasMoreHeroes"
              class="btn btn-secondary"
              @click="loadMoreHeroes"
              :disabled="heroIsLoading"
          >
            <span v-if="!heroIsLoading">
              Смотреть больше героев <i class="fas fa-arrow-right"></i>
            </span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i> Загрузка...
            </span>
          </button>

          <div v-else-if="heroes.length > 0" class="all-heroes-shown">
            <i class="fas fa-check-circle"></i> Все герои загружены
          </div>
        </div>
      </div>
    </section>

    <!-- Блок Миссий -->
    <section class="section section-dark" id="missions">
      <div class="container">
        <h2 class="section-title"><i class="fas fa-tasks"></i> Попробуйте Миссию</h2>
        <p class="section-subtitle">Интерактивные задания, которые погружают в историю.</p>
        <div class="missions-grid">
          <div class="mission-card">
            <div class="mission-card-header" style="background-color: #2a4b8c;">
              <i class="fas fa-cogs"></i>
              <h3>Собери свой биплан</h3>
            </div>
            <div class="mission-card-content">
              <p>Как братья Райт? Соберите летательный аппарат из предложенных деталей и узнайте принципы полёта.</p>
              <div class="mission-difficulty">
                <span>Сложность:</span>
                <div class="stars">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="far fa-star"></i>
                </div>
              </div>
              <button class="btn-card btn-mission" @click="startMission('biplane')">
                Начать миссию <i class="fas fa-play"></i>
              </button>
            </div>
          </div>
          <div class="mission-card">
            <div class="mission-card-header" style="background-color: #8c2a4b;">
              <i class="fas fa-moon"></i>
              <h3>Рассчитай траекторию</h3>
            </div>
            <div class="mission-card-content">
              <p>Помогите «Аполлону-11» добраться до Луны. Простая задача по физике и геометрии.</p>
              <div class="mission-difficulty">
                <span>Сложность:</span>
                <div class="stars">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                </div>
              </div>
              <button class="btn-card btn-mission" @click="startMission('trajectory')">
                Начать миссию <i class="fas fa-play"></i>
              </button>
            </div>
          </div>
          <div class="mission-card">
            <div class="mission-card-header" style="background-color: #2a8c5e;">
              <i class="fas fa-user-astronaut"></i>
              <h3>Тест космонавта</h3>
            </div>
            <div class="mission-card-content">
              <p>Пройдите базовые испытания на реакцию, память и знания, как настоящие покорители космоса.</p>
              <div class="mission-difficulty">
                <span>Сложность:</span>
                <div class="stars">
                  <i class="fas fa-star"></i>
                  <i class="far fa-star"></i>
                  <i class="far fa-star"></i>
                </div>
              </div>
              <button class="btn-card btn-mission" @click="startMission('test')">
                Начать миссию <i class="fas fa-play"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Лента времени -->
    <section class="section" id="timeline">
      <div class="container">
        <h2 class="section-title"><i class="fas fa-history"></i> Лента времени</h2>
        <p class="section-subtitle">Ключевые вехи в истории покорения неба и космоса.</p>
        <div class="timeline">
          <TimelineItemComponent
              v-for="event in timelineEvents.slice(0, visibleEventsCount)"
              :key="event.id"
              :event="event"
          />
          <div v-if="timelineIsLoading" class="timeline-loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка событий...
          </div>
        </div>
        <div class="text-center">
          <button
              v-if="hasMoreEvents"
              class="btn btn-secondary"
              @click="loadMoreEvents"
              :disabled="timelineIsLoading"
          >
            <span v-if="!timelineIsLoading">
              Показать больше событий
              <i class="fas fa-plus"></i>
            </span>
            <span v-else>
              <i class="fas fa-spinner fa-spin"></i> Загрузка...
            </span>
          </button>
          <div v-else-if="timelineEvents.length > 0" class="all-events-shown">
            <i class="fas fa-check-circle"></i> Все события загружены
          </div>
        </div>
      </div>
    </section>

    <KBComponent></KBComponent>
  </div>

  <!-- Страница выполнения миссии -->
  <div v-if="activeSection === 'mission'" class="section mission-section">
    <div class="container">
      <div class="section-header">
        <button class="btn btn-secondary" @click="backFromMission">
          <i class="fas fa-arrow-left"></i> Назад к миссиям
        </button>
        <h2 class="section-title">
          <i class="fas" :class="{
            'fa-cogs': activeMission === 'biplane',
            'fa-moon': activeMission === 'trajectory',
            'fa-user-astronaut': activeMission === 'test'
          }"></i>
          {{
            activeMission === 'biplane' ? 'Собери свой биплан' :
                activeMission === 'trajectory' ? 'Рассчитай траекторию' :
                    'Тест космонавта'
          }}
        </h2>
      </div>

      <div class="mission-content">
        <MissionBiplane v-if="activeMission === 'biplane'" />
        <MissionTrajectory v-if="activeMission === 'trajectory'" />
        <MissionAstronautTest v-if="activeMission === 'test'" />
      </div>
    </div>
  </div>

  <!-- Личный кабинет (доступен всем авторизованным пользователям, включая админов) -->
  <div v-if="activeSection === 'profile'" class="section">
    <div class="container">
      <div class="section-header">
        <button class="btn btn-secondary" @click="backToHome">
          <i class="fas fa-arrow-left"></i> На главную
        </button>
        <h2 class="section-title">
          <i class="fas" :class="isAdmin ? 'fa-user-shield' : 'fa-user-circle'"></i>
          Личный кабинет {{ isAdmin ? '(Администратор)' : '' }}
        </h2>
      </div>
      <ProfileComponent />
    </div>
  </div>

  <!-- Админ-панель (только для админов) -->
  <div v-if="activeSection === 'admin'" class="section">
    <div class="container">
      <div class="section-header">
        <button class="btn btn-secondary" @click="backToHome">
          <i class="fas fa-arrow-left"></i> На главную
        </button>
        <h2 class="section-title"><i class="fas fa-user-shield"></i> Административная панель</h2>
      </div>
      <AdminPanelComponent />
    </div>
  </div>

  <!-- Модальное окно героя -->
  <ModalHeroComponent
      :hero="selectedHero"
      :is-visible="isModalVisible"
      @close="closeHeroModal"
  />

  <FooterComponent></FooterComponent>
</template>

<style scoped>
/* Главный баннер */
.hero {
  padding: 160px 0 80px;
  background: linear-gradient(135deg, #f5f7ff 0%, #e3eeff 100%);
  overflow: hidden;
}

.hero .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.hero__content {
  flex: 1;
}

.hero-title {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 1.3rem;
  color: var(--gray-color);
  margin-bottom: 30px;
  max-width: 600px;
}

.hero-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.hero-stats {
  display: flex;
  gap: 40px;
  margin-top: 40px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-family: var(--font-heading);
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--primary-color);
}

.stat-label {
  color: var(--gray-color);
  font-size: 0.9rem;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
}

.floating-rocket {
  font-size: 20rem;
  color: var(--secondary-color);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-30px); }
}

/* Карточки героев */
.heroes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

/* Карточки миссий */
.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

/* Лента времени */
.timeline {
  max-width: 800px;
  margin: 50px auto;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 100%;
  background-color: var(--secondary-color);
  border-radius: 2px;
}

/* Сообщения загрузки */
.timeline-loading {
  text-align: center;
  padding: 20px;
  color: var(--secondary-color);
  font-size: 1.1rem;
}

.timeline-loading i {
  margin-right: 10px;
}

.all-events-shown {
  padding: 15px;
  color: var(--success-color);
  font-size: 1.1rem;
}

.all-events-shown i {
  margin-right: 10px;
}

.all-heroes-shown {
  padding: 15px;
  color: var(--success-color);
  font-size: 1.1rem;
}

.all-heroes-shown i {
  margin-right: 10px;
}

.text-center {
  text-align: center;
  margin-top: 30px;
}

/* Секция заголовка для профиля и админки */
.section-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.section-header .btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Страница миссии */
.mission-section {
  background: #f8f9fa;
  min-height: calc(100vh - 200px);
}

.mission-content {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 30px;
  margin-top: 20px;
}

.mission-card {
  background-color: white;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mission-card-header {
  color: white;
  padding: 25px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.mission-card-header i {
  font-size: 3rem;
}

.mission-card-content {
  padding: 25px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.mission-card-content p {
  color: var(--dark-color);
}

.mission-difficulty {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  color: var(--gray-color);
}

/* Миссии */
.stars {
  display: flex;
  gap: 5px;
  color: #ffc107;
}

.btn-mission {
  margin-top: auto;
  cursor: pointer;
  transition: var(--transition);
  background-color: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
  padding: 10px 20px;
  border-radius: 50px;
  font-weight: 600;
  width: 100%;
  font-family: var(--font-body);
  font-size: 1rem;
}

.btn-mission:hover {
  transform: translateY(-2px);
  background-color: var(--primary-color);
  color: white;
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.2);
}
</style>
