<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'

const isMenuOpen = ref(false)
const isAuthModalOpen = ref(false)
const authMode = ref('login')

// Данные для форм
const loginEmail = ref('')
const loginPassword = ref('')
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regPhone = ref('')
const loginError = ref('')
const regError = ref('')
const isLoading = ref(false)

// Получаем данные пользователя
const userData = computed(() => {
  const data = localStorage.getItem('user_data')
  return data ? JSON.parse(data) : null
})

const isLoggedIn = computed(() => {
  const token = localStorage.getItem('auth_token')
  const role = localStorage.getItem('user_role')
  return !!token && !!role
})

const isAdmin = computed(() => {
  const role = localStorage.getItem('user_role')
  console.log('Header: Checking admin status, role:', role)
  return role === 'ADMIN'
})

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

const openAuthModal = (mode = 'login') => {
  authMode.value = mode
  isAuthModalOpen.value = true
  closeMenu()
}

const closeAuthModal = () => {
  isAuthModalOpen.value = false
  // Очищаем формы
  loginEmail.value = ''
  loginPassword.value = ''
  regName.value = ''
  regEmail.value = ''
  regPassword.value = ''
  regPhone.value = ''
  loginError.value = ''
  regError.value = ''
}

const handleLogin = async () => {
  try {
    isLoading.value = true
    loginError.value = ''

    console.log('Login attempt with email:', loginEmail.value)

    const response = await fetch('http://127.0.0.1:8000/user/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: loginEmail.value,
        password: loginPassword.value
      })
    })

    const data = await response.json()
    console.log('Login response:', data)

    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка входа')
    }

    const { access_token, role } = data

    // Сохраняем токен и роль
    localStorage.setItem('auth_token', access_token)
    localStorage.setItem('user_role', role.toUpperCase()) // Приводим к верхнему регистру

    console.log('Saved token and role:', {
      token: access_token.substring(0, 20) + '...',
      role: role.toUpperCase()
    })

    // Получаем полные данные пользователя
    try {
      const userResponse = await fetch('http://127.0.0.1:8000/user/profile', {
        headers: {
          'Authorization': `Bearer ${access_token}`
        }
      })

      if (userResponse.ok) {
        const userData = await userResponse.json()
        console.log('User profile data:', userData)

        const userInfo = {
          id: userData.id,
          email: userData.email,
          role: userData.role.toUpperCase(), // Приводим к верхнему регистру
          name: userData.name,
          phone_number: userData.phone_number
        }

        localStorage.setItem('user_data', JSON.stringify(userInfo))
        console.log('Saved user data:', userInfo)
      } else {
        // Fallback на данные из формы
        const userInfo = {
          email: loginEmail.value,
          role: role.toUpperCase(),
          name: 'Пользователь'
        }
        localStorage.setItem('user_data', JSON.stringify(userInfo))
        console.log('Fallback user data:', userInfo)
      }
    } catch (userError) {
      console.error('Error fetching user profile:', userError)
      const userInfo = {
        email: loginEmail.value,
        role: role.toUpperCase(),
        name: 'Пользователь'
      }
      localStorage.setItem('user_data', JSON.stringify(userInfo))
    }

    closeAuthModal()

    // Обновляем страницу
    setTimeout(() => {
      window.location.reload()
    }, 100)

  } catch (error) {
    console.error('Login error:', error)
    loginError.value = error.message
  } finally {
    isLoading.value = false
  }
}

const handleRegister = async () => {
  try {
    isLoading.value = true
    regError.value = ''

    const response = await fetch('http://127.0.0.1:8000/user/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: regName.value,
        email: regEmail.value,
        password: regPassword.value,
        phone_number: regPhone.value
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка регистрации')
    }

    // После успешной регистрации переключаемся на вход
    authMode.value = 'login'
    regName.value = ''
    regEmail.value = ''
    regPassword.value = ''
    regPhone.value = ''

    alert('Регистрация успешна! Теперь вы можете войти.')

  } catch (error) {
    console.error('Register error:', error)
    regError.value = error.message
  } finally {
    isLoading.value = false
  }
}

const logout = () => {
  console.log('Logging out...')
  localStorage.clear()
  window.location.reload()
}

const closeMenuOnClickOutside = (e) => {
  const hamburger = document.getElementById('hamburger')
  const menu = document.querySelector('.header__menu')

  if (menu && !menu.contains(e.target) && hamburger && !hamburger.contains(e.target)) {
    closeMenu()
  }
}

const closeMenuOnResize = () => {
  if (window.innerWidth > 768) {
    closeMenu()
  }
}

const debugInfo = () => {
  console.log('Header Debug Info:')
  console.log('Token exists:', !!localStorage.getItem('auth_token'))
  console.log('Token:', localStorage.getItem('auth_token')?.substring(0, 20) + '...')
  console.log('User role:', localStorage.getItem('user_role'))
  console.log('User data:', localStorage.getItem('user_data'))
  console.log('Is Logged In:', isLoggedIn.value)
  console.log('Is Admin:', isAdmin.value)
}

onMounted(() => {
  document.addEventListener('click', closeMenuOnClickOutside)
  window.addEventListener('resize', closeMenuOnResize)

  // Убираем дублирующийся обработчик клика на гамбургер
  // так как он уже есть в @click в шаблоне
  debugInfo()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeMenuOnClickOutside)
  window.removeEventListener('resize', closeMenuOnResize)
})
</script>

<template>
  <header class="header">
    <div class="container">
      <nav class="header__content">
        <a href="#" @click.prevent="window.location.hash = ''" class="logo">
          <i class="fas fa-rocket"></i>
          <span>Орбита<span class="logo-accent">Знаний</span></span>
        </a>
        <ul class="header__menu" :class="{ active: isMenuOpen }">
          <li><a href="#heroes" @click="closeMenu"><i class="fas fa-user-astronaut"></i> Герои</a></li>
          <li><a href="#missions" @click="closeMenu"><i class="fas fa-tasks"></i> Миссии</a></li>
          <li><a href="#timeline" @click="closeMenu"><i class="fas fa-history"></i> Лента времени</a></li>
          <li><a href="#future" @click="closeMenu"><i class="fas fa-satellite"></i> КБ Будущего</a></li>

          <!-- Для неавторизованных пользователей -->
          <template v-if="!isLoggedIn">
            <li>
              <a href="#" class="header__menu-btn" @click.prevent="openAuthModal('login')">
                <i class="fas fa-sign-in-alt"></i> Войти
              </a>
            </li>
          </template>

          <!-- Для авторизованных пользователей -->
          <template v-else>
            <li class="user-menu-item">
              <a href="#" @click.prevent="closeMenu">
                <i class="fas fa-user"></i>
                <span class="user-name">{{ userData?.name || 'Пользователь' }}</span>
                <span class="user-role-badge" :class="userData?.role?.toLowerCase()">
                  {{ userData?.role === 'ADMIN' ? 'Админ' : 'Польз.' }}
                </span>
              </a>
              <div class="user-dropdown">
                <!-- Профиль доступен всем авторизованным пользователям -->
                <a href="#profile" @click="closeMenu">
                  <i class="fas" :class="isAdmin ? 'fa-user-shield' : 'fa-user-circle'"></i>
                  Профиль
                </a>
                <div v-if="isAdmin" class="admin-section">
                  <a href="#admin" @click="closeMenu">
                    <i class="fas fa-cogs"></i> Админ-панель
                  </a>
                </div>
                <div class="divider"></div>
                <a href="#" @click.prevent="logout">
                  <i class="fas fa-sign-out-alt"></i> Выйти
                </a>
              </div>
            </li>
          </template>
        </ul>
        <button class="hamburger" id="hamburger" @click="toggleMenu" :aria-expanded="isMenuOpen">
          <i class="fas" :class="isMenuOpen ? 'fa-times' : 'fa-bars'"></i>
        </button>
      </nav>
    </div>

    <!-- Модальное окно авторизации -->
    <Teleport to="body">
      <div v-if="isAuthModalOpen" class="modal-overlay" @click.self="closeAuthModal">
        <div class="auth-modal" @click.stop>
          <button class="close-btn" @click="closeAuthModal">&times;</button>

          <div class="auth-header">
            <h2>{{ authMode === 'login' ? 'Вход в систему' : 'Регистрация' }}</h2>
            <p>{{ authMode === 'login' ? 'Введите ваши данные для входа' : 'Создайте новый аккаунт' }}</p>
          </div>

          <!-- Ошибки -->
          <div v-if="loginError && authMode === 'login'" class="error-message">
            <i class="fas fa-exclamation-circle"></i> {{ loginError }}
          </div>
          <div v-if="regError && authMode === 'register'" class="error-message">
            <i class="fas fa-exclamation-circle"></i> {{ regError }}
          </div>

          <!-- Форма входа -->
          <form v-if="authMode === 'login'" @submit.prevent="handleLogin" class="auth-form">
            <div class="form-group">
              <label for="email">
                <i class="fas fa-envelope"></i> Email
              </label>
              <input
                  id="email"
                  v-model="loginEmail"
                  type="email"
                  placeholder="example@mail.com"
                  required
              />
            </div>

            <div class="form-group">
              <label for="password">
                <i class="fas fa-lock"></i> Пароль
              </label>
              <input
                  id="password"
                  v-model="loginPassword"
                  type="password"
                  placeholder="Введите пароль"
                  required
              />
            </div>

            <button type="submit" class="btn btn-primary auth-btn" :disabled="isLoading">
              <span v-if="isLoading">
                <i class="fas fa-spinner fa-spin"></i> Загрузка...
              </span>
              <span v-else>
                <i class="fas fa-sign-in-alt"></i> Войти
              </span>
            </button>
          </form>

          <!-- Форма регистрации -->
          <form v-else @submit.prevent="handleRegister" class="auth-form">
            <div class="form-group">
              <label for="reg-name">
                <i class="fas fa-user"></i> Имя и фамилия
              </label>
              <input
                  id="reg-name"
                  v-model="regName"
                  type="text"
                  placeholder="Иван Иванов"
                  required
              />
            </div>

            <div class="form-group">
              <label for="reg-email">
                <i class="fas fa-envelope"></i> Email
              </label>
              <input
                  id="reg-email"
                  v-model="regEmail"
                  type="email"
                  placeholder="example@mail.com"
                  required
              />
            </div>

            <div class="form-group">
              <label for="reg-password">
                <i class="fas fa-lock"></i> Пароль
              </label>
              <input
                  id="reg-password"
                  v-model="regPassword"
                  type="password"
                  placeholder="Не менее 6 символов"
                  required
                  minlength="6"
              />
            </div>

            <div class="form-group">
              <label for="reg-phone">
                <i class="fas fa-phone"></i> Номер телефона
              </label>
              <input
                  id="reg-phone"
                  v-model="regPhone"
                  type="tel"
                  placeholder="+7 (999) 123-45-67"
                  required
              />
            </div>

            <button type="submit" class="btn btn-primary auth-btn" :disabled="isLoading">
              <span v-if="isLoading">
                <i class="fas fa-spinner fa-spin"></i> Загрузка...
              </span>
              <span v-else>
                <i class="fas fa-user-plus"></i> Зарегистрироваться
              </span>
            </button>
          </form>

          <div class="auth-footer">
            <p>
              {{ authMode === 'login' ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
              <a href="#" @click.prevent="authMode = authMode === 'login' ? 'register' : 'login'">
                {{ authMode === 'login' ? 'Зарегистрироваться' : 'Войти' }}
              </a>
            </p>
          </div>
        </div>
      </div>
    </Teleport>
  </header>
</template>

<style scoped>
/* Шапка */
.header {
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.header__content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-heading);
  font-size: 1.8rem;
  font-weight: 900;
  text-decoration: none;
  color: var(--dark-color);
  cursor: pointer;
}

.logo:hover {
  opacity: 0.9;
}

.logo i {
  color: var(--secondary-color);
  font-size: 2rem;
}

.logo-accent {
  color: var(--accent-color);
}

.header__menu {
  display: flex;
  list-style: none;
  gap: 20px;
  align-items: center;
}

.header__menu a {
  text-decoration: none;
  color: var(--dark-color);
  font-weight: 500;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
}

.header__menu a:hover {
  color: var(--secondary-color);
  background-color: #f5f7ff;
}

.hamburger {
  display: none;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: var(--dark-color);
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  z-index: 1002;
}

.hamburger:hover {
  background-color: #f5f7ff;
}

/* Кнопка Войти (старый стиль) */
.header__menu-btn {
  background-color: var(--secondary-color);
  color: white !important;
  border-radius: 50px;
  padding: 8px 20px !important;
  margin-left: 10px;
  transition: var(--transition);
}

.header__menu-btn:hover {
  background-color: var(--primary-color);
  color: white !important;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.3);
}

/* Стили для авторизованного пользователя */
.user-menu-item {
  position: relative;
}

.user-menu-item > a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px !important;
  background-color: #f5f7ff;
  border-radius: 50px;
  transition: var(--transition);
}

.user-menu-item > a:hover {
  background-color: #e3eeff;
}

.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
}

.user-role-badge.admin {
  background-color: var(--accent-color);
}

.user-role-badge.user {
  background-color: var(--secondary-color);
}

/* Выпадающее меню пользователя */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  min-width: 180px;
  padding: 10px 0;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 1001;
}

.user-menu-item:hover .user-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.user-dropdown a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: var(--dark-color);
  text-decoration: none;
  transition: var(--transition);
  white-space: nowrap;
  border-radius: 0;
}

.user-dropdown a:hover {
  background-color: #f5f7ff;
  color: var(--secondary-color);
}

.user-dropdown .divider {
  height: 1px;
  background-color: #eaeaea;
  margin: 5px 0;
}

.admin-section {
  border-top: 1px solid #eaeaea;
  padding-top: 5px;
  margin-top: 5px;
}

.admin-section a {
  color: var(--accent-color) !important;
}

.admin-section a:hover {
  color: #e91e63 !important;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
}

.auth-modal {
  background: white;
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 450px;
  padding: 40px;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 2.5rem;
  color: var(--gray-color);
  cursor: pointer;
  transition: var(--transition);
  line-height: 1;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  color: var(--accent-color);
  background-color: rgba(0, 0, 0, 0.05);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: var(--primary-color);
  margin-bottom: 10px;
}

.auth-header p {
  color: var(--gray-color);
  margin-bottom: 0;
}

.error-message {
  background-color: rgba(255, 64, 129, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
  padding: 12px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-form {
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--dark-color);
}

.form-group label i {
  color: var(--secondary-color);
  width: 20px;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: 1rem;
  transition: var(--transition);
}

.form-group input:focus {
  outline: none;
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(0, 176, 255, 0.1);
}

.auth-btn {
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
  margin-top: 10px;
}

.auth-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.auth-footer p {
  margin-bottom: 15px;
  color: var(--gray-color);
}

.auth-footer a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition);
}

.auth-footer a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

/* Мобильные стили для гамбургер-меню */
@media (max-width: 768px) {
  .hamburger {
    display: block;
  }

  .header__menu {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: white;
    flex-direction: column;
    align-items: flex-start;
    padding: 80px 30px 30px;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    transition: right 0.3s ease;
    z-index: 1001;
    overflow-y: auto;
    gap: 0;
  }

  .header__menu.active {
    right: 0;
  }

  .header__menu li {
    width: 100%;
    margin-bottom: 10px;
  }

  .header__menu a {
    width: 100%;
    padding: 15px !important;
    border-radius: 8px;
    justify-content: flex-start;
  }

  .header__menu-btn {
    margin: 20px 0 0 0 !important;
    justify-content: center !important;
    text-align: center;
  }

  .user-menu-item > a {
    background-color: #f5f7ff;
    border-radius: 8px;
  }

  .user-dropdown {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    box-shadow: none;
    background: transparent;
    padding: 10px 0 0 0;
    display: none;
  }

  .user-menu-item:hover .user-dropdown {
    display: block;
  }

  .user-dropdown a {
    padding: 12px 15px;
    background-color: #f8f9fa;
    margin-bottom: 5px;
    border-radius: 8px;
  }

  .admin-section {
    border-top: 1px solid #eaeaea;
    padding-top: 10px;
    margin-top: 10px;
  }

  /* Оверлей для затемнения фона */
  .header__menu.active::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .header__menu.active::before {
    opacity: 1;
  }
}
</style>
