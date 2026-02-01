<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  mode: {
    type: String,
    default: 'login', // 'login' или 'register'
    validator: (value) => ['login', 'register'].includes(value)
  }
})

const emit = defineEmits(['success', 'close'])

const isLogin = computed(() => props.mode === 'login')

// Данные формы
const formData = ref({
  name: '',
  email: '',
  password: '',
  phone_number: ''
})

// Ошибки
const errors = ref({})
const isLoading = ref(false)
const successMessage = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000/user'

const validateForm = () => {
  errors.value = {}

  if (!formData.value.email) {
    errors.value.email = 'Email обязателен'
  } else if (!/\S+@\S+\.\S+/.test(formData.value.email)) {
    errors.value.email = 'Некорректный email'
  }

  if (!formData.value.password) {
    errors.value.password = 'Пароль обязателен'
  } else if (formData.value.password.length < 6) {
    errors.value.password = 'Пароль должен быть не менее 6 символов'
  }

  if (!isLogin.value) {
    if (!formData.value.name) {
      errors.value.name = 'Имя обязательно'
    }
    if (!formData.value.phone_number) {
      errors.value.phone_number = 'Номер телефона обязателен'
    }
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isLoading.value = true
  errors.value = {}

  try {
    const endpoint = isLogin.value ? '/login' : '/register'
    const payload = isLogin.value
        ? {
          email: formData.value.email,
          password: formData.value.password
        }
        : formData.value

    const response = await axios.post(`${API_BASE_URL}${endpoint}`, payload)

    if (isLogin.value) {
      // Сохраняем токен в localStorage
      const { access_token, role } = response.data
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('user_role', role)

      // Сохраняем данные пользователя
      const userData = {
        email: formData.value.email,
        role
      }
      localStorage.setItem('user_data', JSON.stringify(userData))

      successMessage.value = 'Успешный вход!'
      emit('success', { token: access_token, role })
    } else {
      successMessage.value = 'Регистрация успешна! Теперь вы можете войти.'
      emit('success', { message: 'Registration successful' })
    }

    // Очищаем форму через 2 секунды
    setTimeout(() => {
      if (isLogin.value) {
        closeModal()
      } else {
        // Переключаемся на форму входа
        emit('switch-mode', 'login')
      }
    }, 2000)

  } catch (error) {
    console.error('Auth error:', error)

    if (error.response?.data?.detail) {
      errors.value.general = error.response.data.detail
    } else if (error.response?.data) {
      errors.value.general = Object.values(error.response.data).join(', ')
    } else {
      errors.value.general = 'Произошла ошибка. Попробуйте снова.'
    }
  } finally {
    isLoading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

const switchMode = () => {
  emit('switch-mode', isLogin.value ? 'register' : 'login')
}

// Очистка формы при смене режима
const clearForm = () => {
  formData.value = {
    name: '',
    email: '',
    password: '',
    phone_number: ''
  }
  errors.value = {}
  successMessage.value = ''
}

defineExpose({ clearForm })
</script>

<template>
  <div class="auth-modal-overlay" @click.self="closeModal">
    <div class="auth-modal">
      <button class="close-btn" @click="closeModal">&times;</button>

      <div class="auth-header">
        <h2>{{ isLogin ? 'Вход в систему' : 'Регистрация' }}</h2>
        <p>{{ isLogin ? 'Введите ваши данные для входа' : 'Создайте новый аккаунт' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <!-- Общая ошибка -->
        <div v-if="errors.general" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ errors.general }}
        </div>

        <!-- Успешное сообщение -->
        <div v-if="successMessage" class="success-message">
          <i class="fas fa-check-circle"></i> {{ successMessage }}
        </div>

        <!-- Поле имени (только для регистрации) -->
        <div v-if="!isLogin" class="form-group">
          <label for="name">
            <i class="fas fa-user"></i> Имя и фамилия
          </label>
          <input
              id="name"
              v-model="formData.name"
              type="text"
              placeholder="Иван Иванов"
              :class="{ 'error': errors.name }"
          />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>

        <!-- Поле email -->
        <div class="form-group">
          <label for="email">
            <i class="fas fa-envelope"></i> Email
          </label>
          <input
              id="email"
              v-model="formData.email"
              type="email"
              placeholder="example@mail.com"
              :class="{ 'error': errors.email }"
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <!-- Поле пароля -->
        <div class="form-group">
          <label for="password">
            <i class="fas fa-lock"></i> Пароль
          </label>
          <input
              id="password"
              v-model="formData.password"
              type="password"
              placeholder="Не менее 6 символов"
              :class="{ 'error': errors.password }"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <!-- Поле телефона (только для регистрации) -->
        <div v-if="!isLogin" class="form-group">
          <label for="phone">
            <i class="fas fa-phone"></i> Номер телефона
          </label>
          <input
              id="phone"
              v-model="formData.phone_number"
              type="tel"
              placeholder="+7 (999) 123-45-67"
              :class="{ 'error': errors.phone_number }"
          />
          <span v-if="errors.phone_number" class="field-error">{{ errors.phone_number }}</span>
        </div>

        <button type="submit" class="btn btn-primary auth-btn" :disabled="isLoading">
          <template v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка...
          </template>
          <template v-else>
            {{ isLogin ? 'Войти' : 'Зарегистрироваться' }}
          </template>
        </button>
      </form>

      <div class="auth-footer">
        <p>
          {{ isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
          <a href="#" @click.prevent="switchMode">
            {{ isLogin ? 'Зарегистрироваться' : 'Войти' }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  padding: 20px;
}

.auth-modal {
  background: white;
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 500px;
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

.form-group input.error {
  border-color: var(--accent-color);
}

.field-error {
  display: block;
  margin-top: 5px;
  color: var(--accent-color);
  font-size: 0.85rem;
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

.success-message {
  background-color: rgba(76, 175, 80, 0.1);
  border: 1px solid var(--success-color);
  color: var(--success-color);
  padding: 12px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
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

</style>
