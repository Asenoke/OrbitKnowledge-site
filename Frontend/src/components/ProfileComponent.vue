<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const userData = ref(null)
const isLoading = ref(false)
const isEditing = ref(false)
const editForm = ref({})
const errors = ref({})
const successMessage = ref('')
const isAuthenticated = ref(false)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Получаем токен из localStorage
const getToken = () => {
  const token = localStorage.getItem('auth_token')
  console.log('Token from localStorage:', token ? 'Exists' : 'Missing')
  return token
}

// Проверяем авторизацию
const checkAuth = () => {
  const token = getToken()
  const userRole = localStorage.getItem('user_role')
  const userDataStr = localStorage.getItem('user_data')

  console.log('Auth check - Token:', !!token, 'Role:', userRole, 'UserData:', !!userDataStr)

  isAuthenticated.value = !!token

  // Если есть данные в localStorage, используем их для начального отображения
  if (userDataStr && !userData.value) {
    try {
      userData.value = JSON.parse(userDataStr)
      console.log('Using cached user data:', userData.value)
    } catch (e) {
      console.error('Error parsing cached user data:', e)
    }
  }

  return !!token
}

// Проверка админ-статуса - исправлено: сравниваем с 'admin' в нижнем регистре
const isAdmin = computed(() => {
  if (userData.value && userData.value.role) {
    return userData.value.role.toLowerCase() === 'admin'
  }
  const role = localStorage.getItem('user_role')
  return role && role.toLowerCase() === 'admin'
})

// Упрощенное получение данных пользователя
const getUserData = async () => {
  try {
    const token = getToken()
    if (!token) {
      errors.value.general = 'Требуется авторизация'
      isAuthenticated.value = false
      return
    }

    isLoading.value = true

    console.log('Fetching profile from API...')

    // Используем один эндпоинт
    const endpoint = `${API_BASE_URL}/user/profile`

    console.log('Trying endpoint:', endpoint)

    const response = await axios.get(endpoint, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 5000
    })

    console.log('Success with endpoint:', endpoint, 'Data:', response.data)
    console.log('Role from API:', response.data.role, 'Type:', typeof response.data.role)

    userData.value = response.data
    isAuthenticated.value = true

    // Сохраняем данные в localStorage
    const userInfo = {
      id: response.data.id || response.data.userId,
      name: response.data.name || response.data.username || response.data.email,
      email: response.data.email,
      role: response.data.role || response.data.userRole || 'user', // 'user' в нижнем регистре
      phone_number: response.data.phone_number || response.data.phone || ''
    }

    localStorage.setItem('user_data', JSON.stringify(userInfo))
    localStorage.setItem('user_role', userInfo.role)

    editForm.value = {
      name: userInfo.name,
      phone_number: userInfo.phone_number || '',
      password: ''
    }

    successMessage.value = 'Профиль успешно загружен!'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)

  } catch (error) {
    console.error('Error fetching profile:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)

    // Используем кэшированные данные, если API не отвечает
    const cachedData = localStorage.getItem('user_data')
    if (cachedData) {
      try {
        userData.value = JSON.parse(cachedData)
        errors.value.general = 'Используются кэшированные данные. API недоступен.'
      } catch (e) {
        console.error('Error parsing cached data:', e)
        handleAuthError(error)
      }
    } else {
      handleAuthError(error)
    }
  } finally {
    isLoading.value = false
  }
}

const handleAuthError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        errors.value.general = 'Сессия истекла'
        logout()
        break
      case 403:
        errors.value.general = 'Доступ запрещен. Проверьте права доступа.'
        break
      case 404:
        errors.value.general = 'Профиль не найден'
        break
      default:
        errors.value.general = error.response.data?.detail || 'Ошибка сервера'
    }
  } else if (error.request) {
    errors.value.general = 'Сервер не отвечает'
  } else {
    errors.value.general = 'Ошибка подключения: ' + error.message
  }
}

const validateEditForm = () => {
  errors.value = {}

  if (!editForm.value.name || editForm.value.name.length < 2) {
    errors.value.name = 'Имя должно быть не менее 2 символов'
  }

  if (editForm.value.phone_number && !/^[\d\s\-\+\(\)]+$/.test(editForm.value.phone_number)) {
    errors.value.phone_number = 'Некорректный номер телефона'
  }

  if (editForm.value.password && editForm.value.password.length < 6) {
    errors.value.password = 'Пароль должен быть не менее 6 символов'
  }

  return Object.keys(errors.value).length === 0
}

const saveProfile = async () => {
  if (!validateEditForm()) return

  try {
    const token = getToken()
    if (!token) {
      errors.value.general = 'Требуется авторизация'
      return
    }

    isLoading.value = true

    const payload = {
      name: editForm.value.name,
      phone_number: editForm.value.phone_number
    }

    if (editForm.value.password) {
      payload.password = editForm.value.password
    }

    console.log('Updating profile with payload:', payload)

    // Используем один эндпоинт для обновления
    const endpoint = `${API_BASE_URL}/user/profile`

    const response = await axios.put(endpoint, payload, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 5000
    })

    successMessage.value = 'Профиль успешно обновлен!'

    // Обновляем локальные данные
    if (userData.value) {
      userData.value.name = editForm.value.name
      userData.value.phone_number = editForm.value.phone_number
      localStorage.setItem('user_data', JSON.stringify(userData.value))
    }

    // Очищаем пароль
    editForm.value.password = ''

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)

    isEditing.value = false
  } catch (error) {
    console.error('Error updating profile:', error)
    console.error('Update error response:', error.response?.data)

    if (error.response?.data?.detail) {
      errors.value.general = error.response.data.detail
    } else if (error.response?.data?.message) {
      errors.value.general = error.response.data.message
    } else if (error.response?.data) {
      errors.value.general = JSON.stringify(error.response.data)
    } else {
      errors.value.general = 'Ошибка при обновлении профиля'
    }
  } finally {
    isLoading.value = false
  }
}

const deleteProfile = async () => {
  if (!confirm('Вы уверены, что хотите удалить свой профиль? Это действие необратимо.')) {
    return
  }

  try {
    const token = getToken()
    if (!token) {
      errors.value.general = 'Требуется авторизация'
      return
    }

    isLoading.value = true

    // Используем один эндпоинт
    const endpoint = `${API_BASE_URL}/user/profile`

    await axios.delete(endpoint, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 5000
    })

    localStorage.clear()
    window.location.href = '/'
  } catch (error) {
    console.error('Error deleting profile:', error)
    errors.value.general = 'Ошибка при удалении профиля'
  } finally {
    isLoading.value = false
  }
}

const logout = () => {
  console.log('Logging out...')
  localStorage.clear()
  window.location.href = '/'
}

const login = () => {
  window.location.href = '/#/login'
}

onMounted(() => {
  console.log('ProfileComponent mounted')

  if (checkAuth()) {
    getUserData()
  } else {
    errors.value.general = 'Пожалуйста, войдите в систему'
  }
})
</script>

<template>
  <div class="profile-container">
    <!-- Состояние загрузки -->
    <div v-if="isLoading && !userData" class="profile-loading">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Загрузка профиля...</p>
    </div>

    <!-- Не авторизован -->
    <div v-else-if="!isAuthenticated" class="profile-not-authorized">
      <div class="unauthorized-message">
        <i class="fas fa-user-lock"></i>
        <h3>Доступ запрещен</h3>
        <p>Для просмотра профиля необходимо войти в систему.</p>
        <button class="btn btn-primary" @click="login">
          <i class="fas fa-sign-in-alt"></i> Войти
        </button>
      </div>
    </div>

    <!-- Авторизован и данные загружены -->
    <div v-else-if="userData" class="profile-content">
      <!-- Заголовок профиля -->
      <div class="profile-header">
        <div class="profile-avatar">
          <i class="fas" :class="isAdmin ? 'fa-user-shield' : 'fa-user-astronaut'"></i>
          <span class="role-badge" :class="(userData.role || 'user').toLowerCase()">
            {{ isAdmin ? 'Админ' : 'Пользователь' }}
          </span>
        </div>
        <div class="profile-info">
          <h2>{{ userData.name || 'Пользователь' }}</h2>
          <p class="profile-email">{{ userData.email || 'Email не указан' }}</p>
          <div class="profile-meta">
            <span><i class="fas fa-phone"></i> {{ userData.phone_number || 'Телефон не указан' }}</span>
            <span v-if="userData.id"><i class="fas fa-user-tag"></i> ID: {{ userData.id }}</span>
          </div>
        </div>
        <div class="profile-actions">
          <button class="btn btn-secondary" @click="isEditing = !isEditing">
            <i class="fas" :class="isEditing ? 'fa-times' : 'fa-edit'"></i>
            {{ isEditing ? 'Отмена' : 'Редактировать' }}
          </button>
          <button class="btn btn-logout" @click="logout">
            <i class="fas fa-sign-out-alt"></i> Выйти
          </button>
        </div>
      </div>

      <!-- Уведомления -->
      <div v-if="successMessage" class="alert alert-success">
        <i class="fas fa-check-circle"></i> {{ successMessage }}
      </div>
      <div v-if="errors.general" class="alert alert-error">
        <i class="fas fa-exclamation-circle"></i> {{ errors.general }}
      </div>

      <!-- Форма редактирования -->
      <div v-if="isEditing" class="edit-form">
        <h3><i class="fas fa-user-edit"></i> Редактирование профиля</h3>

        <div class="form-group">
          <label for="edit-name">Имя *</label>
          <input
              id="edit-name"
              v-model="editForm.name"
              type="text"
              placeholder="Ваше имя"
              :class="{ 'error': errors.name }"
              required
          />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>

        <div class="form-group">
          <label for="edit-phone">Телефон</label>
          <input
              id="edit-phone"
              v-model="editForm.phone_number"
              type="tel"
              placeholder="+7 (999) 123-45-67"
              :class="{ 'error': errors.phone_number }"
          />
          <span v-if="errors.phone_number" class="field-error">{{ errors.phone_number }}</span>
        </div>

        <div class="form-group">
          <label for="edit-password">Новый пароль (оставьте пустым, если не меняете)</label>
          <input
              id="edit-password"
              v-model="editForm.password"
              type="password"
              placeholder="Новый пароль"
              :class="{ 'error': errors.password }"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="form-actions">
          <button class="btn btn-primary" @click="saveProfile" :disabled="isLoading">
            <i class="fas fa-save"></i> {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button class="btn btn-danger" @click="deleteProfile" :disabled="isLoading">
            <i class="fas fa-trash"></i> Удалить профиль
          </button>
        </div>
      </div>

      <!-- Информация о пользователе -->
      <div class="profile-section">
        <h3><i class="fas fa-info-circle"></i> Информация об аккаунте</h3>
        <div class="simple-stats">
          <div class="stat-item">
            <i class="fas" :class="isAdmin ? 'fa-user-shield' : 'fa-user'"></i>
            <span>Роль</span>
            <strong>{{ isAdmin ? 'Администратор' : 'Пользователь' }}</strong>
          </div>
          <div class="stat-item" v-if="userData.email">
            <i class="fas fa-envelope"></i>
            <span>Email</span>
            <strong>{{ userData.email }}</strong>
          </div>
          <div class="stat-item" v-if="userData.phone_number">
            <i class="fas fa-phone"></i>
            <span>Телефон</span>
            <strong>{{ userData.phone_number }}</strong>
          </div>
          <div class="stat-item" v-if="userData.id">
            <i class="fas fa-id-card"></i>
            <span>ID пользователя</span>
            <strong>{{ userData.id }}</strong>
          </div>
        </div>
      </div>

      <!-- Дополнительные действия для админа -->
      <div v-if="isAdmin" class="profile-section">
        <h3><i class="fas fa-user-shield"></i> Административные функции</h3>
        <div class="admin-actions">
          <button class="btn btn-admin" onclick="window.location.href = '#/admin'">
            <i class="fas fa-cogs"></i> Перейти в админ-панель
          </button>
          <p class="admin-note">Как администратор вы имеете доступ к управлению пользователями, героями и событиями.</p>
        </div>
      </div>
    </div>

    <!-- Ошибка загрузки, но пользователь авторизован -->
    <div v-else class="profile-error">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>Ошибка загрузки профиля</h3>
      <p>{{ errors.general || 'Не удалось загрузить данные профиля' }}</p>
      <div class="error-actions">
        <button class="btn btn-primary" @click="getUserData">
          <i class="fas fa-redo"></i> Попробовать снова
        </button>
        <button class="btn btn-secondary" @click="logout">
          <i class="fas fa-sign-out-alt"></i> Выйти
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  min-height: 500px;
  position: relative;
}

.profile-not-authorized {
  padding: 80px 20px;
  text-align: center;
}

.unauthorized-message {
  max-width: 400px;
  margin: 0 auto;
}

.unauthorized-message i {
  font-size: 5rem;
  color: var(--secondary-color);
  margin-bottom: 20px;
}

.unauthorized-message h3 {
  color: var(--primary-color);
  margin-bottom: 10px;
}

.unauthorized-message p {
  color: var(--gray-color);
  margin-bottom: 30px;
}

.profile-loading {
  padding: 100px 20px;
  text-align: center;
}

.profile-loading i {
  font-size: 3rem;
  color: var(--secondary-color);
  margin-bottom: 20px;
}

.profile-loading p {
  color: var(--gray-color);
}

.profile-error {
  padding: 100px 20px;
  text-align: center;
}

.profile-error i {
  font-size: 4rem;
  color: var(--accent-color);
  margin-bottom: 20px;
}

.profile-error h3 {
  color: var(--primary-color);
  margin-bottom: 10px;
}

.profile-error p {
  color: var(--gray-color);
  margin-bottom: 30px;
}

.error-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.profile-content {
  padding: 30px;
}

/* Заголовок профиля */
.profile-header {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #eaeaea;
  flex-wrap: wrap;
}

.profile-avatar {
  position: relative;
  flex-shrink: 0;
}

.profile-avatar i {
  font-size: 5rem;
  color: var(--secondary-color);
  background-color: rgba(0, 176, 255, 0.1);
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.profile-avatar i.fa-user-shield {
  color: var(--accent-color);
  background-color: rgba(255, 64, 129, 0.1);
}

.role-badge {
  position: absolute;
  bottom: -5px;
  right: -5px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.role-badge.admin {
  background-color: var(--accent-color);
}

.role-badge.user {
  background-color: var(--secondary-color);
}

.profile-info {
  flex: 1;
  min-width: 250px;
}

.profile-info h2 {
  color: var(--primary-color);
  margin-bottom: 5px;
}

.profile-email {
  color: var(--gray-color);
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.profile-meta span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.profile-meta i {
  color: var(--secondary-color);
}

.profile-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-logout {
  background-color: transparent;
  color: var(--accent-color);
  border: 2px solid var(--accent-color);
}

.btn-logout:hover {
  background-color: var(--accent-color);
  color: white;
}

/* Уведомления */
.alert {
  padding: 15px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-success {
  background-color: rgba(76, 175, 80, 0.1);
  border: 1px solid var(--success-color);
  color: var(--success-color);
}

.alert-error {
  background-color: rgba(255, 64, 129, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
}

/* Форма редактирования */
.edit-form {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: var(--border-radius);
  margin-bottom: 30px;
}

.edit-form h3 {
  color: var(--primary-color);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-form .form-group {
  margin-bottom: 20px;
}

.edit-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--dark-color);
}

.edit-form label[for="edit-name"]::after {
  content: " *";
  color: var(--accent-color);
}

.edit-form input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: 1rem;
}

.edit-form input:focus {
  outline: none;
  border-color: var(--secondary-color);
}

.edit-form input.error {
  border-color: var(--accent-color);
}

.field-error {
  display: block;
  margin-top: 5px;
  color: var(--accent-color);
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
  flex-wrap: wrap;
}

.form-actions .btn {
  min-width: 160px;
}

.btn-danger {
  background-color: var(--accent-color);
  color: white;
  border: 2px solid var(--accent-color);
}

.btn-danger:hover {
  background-color: #e91e63;
  border-color: #e91e63;
}

/* Простая статистика */
.profile-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eaeaea;
}

.profile-section h3 {
  color: var(--primary-color);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.simple-stats {
  background: #f8f9fa;
  border-radius: var(--border-radius);
  padding: 25px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #eaeaea;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item i {
  font-size: 1.5rem;
  color: var(--secondary-color);
  width: 40px;
  text-align: center;
}

.stat-item i.fa-user-shield {
  color: var(--accent-color);
}

.stat-item span {
  flex: 1;
  color: var(--gray-color);
}

.stat-item strong {
  color: var(--primary-color);
  font-weight: 600;
}

/* Админские действия */
.admin-actions {
  background: rgba(255, 64, 129, 0.05);
  border: 1px solid rgba(255, 64, 129, 0.2);
  border-radius: var(--border-radius);
  padding: 25px;
}

.btn-admin {
  background-color: var(--accent-color);
  color: white;
  border: 2px solid var(--accent-color);
  padding: 12px 24px;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.btn-admin:hover {
  background-color: #e91e63;
  border-color: #e91e63;
  transform: translateY(-2px);
}

.admin-note {
  margin-top: 15px;
  color: var(--gray-color);
  font-size: 0.9rem;
  font-style: italic;
}

</style>