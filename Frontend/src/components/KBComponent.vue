<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const isLoggedIn = computed(() => {
  const token = localStorage.getItem('auth_token')
  const role = localStorage.getItem('user_role')
  return !!token && !!role
})

const userData = computed(() => {
  const data = localStorage.getItem('user_data')
  return data ? JSON.parse(data) : null
})

// Данные формы
const projectTitle = ref('')
const projectDescription = ref('')
const projectType = ref('drawing')
const selectedFile = ref(null)
const fileName = ref('')

// Состояния
const isLoading = ref(false)
const uploadSuccess = ref(false)
const errorMessage = ref('')
const projects = ref([])
const showProjects = ref(false)

// Модальное окно просмотра проекта
const showProjectDetailsModal = ref(false)
const selectedProject = ref(null)
const projectDetailsLoading = ref(false)

// Типы проектов
const projectTypes = [
  { value: 'drawing', label: '🎨 Рисунок' },
  { value: 'project', label: '📝 Проект (чертеж, план)' },
  { value: 'idea', label: '💡 Идея (текстовое описание)' }
]

// Обработка выбора файла
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Проверяем размер файла (10MB)
    if (file.size > 10 * 1024 * 1024) {
      errorMessage.value = 'Файл слишком большой. Максимальный размер: 10MB'
      selectedFile.value = null
      fileName.value = ''
      event.target.value = ''
      return
    }

    // Проверяем расширение
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
    const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))

    if (!allowedExtensions.includes(fileExt)) {
      errorMessage.value = `Недопустимый тип файла. Разрешены: ${allowedExtensions.join(', ')}`
      selectedFile.value = null
      fileName.value = ''
      event.target.value = ''
      return
    }

    selectedFile.value = file
    fileName.value = file.name
    errorMessage.value = ''
  }
}

// Отправка проекта
const submitProject = async () => {
  if (!isLoggedIn.value) {
    errorMessage.value = 'Для загрузки проекта необходимо войти в систему'
    return
  }

  if (!projectTitle.value.trim()) {
    errorMessage.value = 'Введите название проекта'
    return
  }

  if (!selectedFile.value) {
    errorMessage.value = 'Выберите файл для загрузки'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('title', projectTitle.value)
    formData.append('description', projectDescription.value)
    formData.append('project_type', projectType.value)
    formData.append('file', selectedFile.value)

    const token = localStorage.getItem('auth_token')

    const response = await axios.post('http://127.0.0.1:8000/projects/upload', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })

    console.log('Проект успешно загружен:', response.data)

    // Сбрасываем форму
    resetForm()
    uploadSuccess.value = true

    // Обновляем список проектов
    await fetchProjects()

    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
      uploadSuccess.value = false
    }, 5000)

  } catch (error) {
    console.error('Ошибка при загрузке проекта:', error)
    if (error.response) {
      errorMessage.value = error.response.data.detail || 'Произошла ошибка при загрузке'
    } else if (error.request) {
      errorMessage.value = 'Не удалось соединиться с сервером'
    } else {
      errorMessage.value = 'Произошла ошибка'
    }
  } finally {
    isLoading.value = false
  }
}

// Сброс формы
const resetForm = () => {
  projectTitle.value = ''
  projectDescription.value = ''
  projectType.value = 'drawing'
  selectedFile.value = null
  fileName.value = ''
  const fileInput = document.getElementById('fileInput')
  if (fileInput) fileInput.value = ''
}

// Получение списка проектов
const fetchProjects = async () => {
  try {
    isLoading.value = true
    const response = await axios.get('http://127.0.0.1:8000/projects/', {
      params: {
        limit: 10,
        offset: 0
      }
    })

    // FIXED: response.data содержит объект с полем projects
    projects.value = response.data.projects || []
    showProjects.value = true
  } catch (error) {
    console.error('Ошибка при загрузке проектов:', error)
  } finally {
    isLoading.value = false
  }
}

// Просмотр деталей проекта
const viewProjectDetails = async (project) => {
  try {
    projectDetailsLoading.value = true

    // Получаем полную информацию о проекте
    const response = await axios.get(`http://127.0.0.1:8000/projects/${project.id}`)

    selectedProject.value = response.data
    showProjectDetailsModal.value = true
  } catch (error) {
    console.error('Ошибка при загрузке деталей проекта:', error)
    alert('Ошибка при загрузке деталей проекта')
  } finally {
    projectDetailsLoading.value = false
  }
}

// Открытие модального окна авторизации
const openAuthModal = () => {
  window.dispatchEvent(new CustomEvent('open-auth-modal', {
    detail: { mode: 'login' }
  }))
}

// Форматирование размера файла
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Получение иконки по типу проекта
const getProjectTypeIcon = (type) => {
  switch(type) {
    case 'drawing': return 'fas fa-palette'
    case 'project': return 'fas fa-file-alt'
    case 'idea': return 'fas fa-lightbulb'
    default: return 'fas fa-file'
  }
}

// Получение цвета статуса
const getStatusColor = (status) => {
  const statusLower = status ? status.toLowerCase() : 'pending'
  switch(statusLower) {
    case 'approved': return '#28a745'
    case 'pending': return '#ffc107'
    case 'rejected': return '#dc3545'
    case 'featured': return '#ff4081'
    default: return '#6c757d'
  }
}

// Получение текста статуса
const getStatusText = (status) => {
  const statusLower = status ? status.toLowerCase() : 'pending'
  switch(statusLower) {
    case 'approved': return 'Одобрено'
    case 'pending': return 'На рассмотрении'
    case 'rejected': return 'Отклонено'
    case 'featured': return 'В зале славы'
    default: return status
  }
}

// Получение текста типа проекта
const getProjectTypeText = (type) => {
  switch(type) {
    case 'drawing': return 'Рисунок'
    case 'project': return 'Проект'
    case 'idea': return 'Идея'
    default: return type
  }
}

onMounted(() => {
  // Загружаем последние проекты при загрузке компонента
  fetchProjects()
})
</script>

<template>
  <!-- КБ Будущего -->
  <section class="section section__accent" id="future">
    <div class="container">
      <h2 class="section__accent-title"><i class="fas fa-satellite"></i> КБ Будущего</h2>
      <p class="section__accent-subtitle">Нарисуй свой космический корабль или придумай миссию!</p>

      <!-- Форма загрузки проекта -->
      <div class="upload-section" v-if="isLoggedIn">
        <div class="upload-card">
          <h3><i class="fas fa-upload"></i> Загрузить новый проект</h3>

          <div v-if="uploadSuccess" class="success-message">
            <i class="fas fa-check-circle"></i>
            <p>Проект успешно загружен! Он появится в списке после проверки модератором.</p>
          </div>

          <div v-if="errorMessage" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>{{ errorMessage }}</p>
          </div>

          <form @submit.prevent="submitProject">
            <div class="form-group">
              <label for="projectTitle">
                <i class="fas fa-heading"></i> Название проекта *
              </label>
              <input
                  id="projectTitle"
                  v-model="projectTitle"
                  type="text"
                  placeholder="Мой космический корабль"
                  required
                  maxlength="200"
              />
            </div>

            <div class="form-group">
              <label for="projectDescription">
                <i class="fas fa-align-left"></i> Описание проекта
              </label>
              <textarea
                  id="projectDescription"
                  v-model="projectDescription"
                  placeholder="Опишите ваш проект, его особенности и идеи..."
                  rows="4"
                  maxlength="1000"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="projectType">
                <i class="fas fa-tag"></i> Тип проекта *
              </label>
              <select id="projectType" v-model="projectType" required>
                <option v-for="type in projectTypes" :value="type.value" :key="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="fileInput">
                <i class="fas fa-file-upload"></i> Файл проекта *
              </label>
              <div class="file-upload">
                <input
                    id="fileInput"
                    type="file"
                    @change="handleFileSelect"
                    required
                    accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip,.rar"
                />
                <label for="fileInput" class="file-upload-label">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <span v-if="fileName">{{ fileName }}</span>
                  <span v-else>Выберите файл (макс. 10MB)</span>
                </label>
              </div>
              <small class="file-hint">
                Поддерживаемые форматы: JPG, PNG, GIF, PDF, DOC, TXT, ZIP, RAR
              </small>
            </div>

            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading">
                <i class="fas fa-spinner fa-spin"></i> Загрузка...
              </span>
              <span v-else>
                <i class="fas fa-upload"></i> Загрузить проект
              </span>
            </button>
          </form>
        </div>
      </div>

      <!-- Призыв к авторизации для неавторизованных -->
      <div v-else class="auth-required">
        <div class="auth-card">
          <h3><i class="fas fa-user-lock"></i> Требуется авторизация</h3>
          <p>Для загрузки проектов необходимо войти в систему или зарегистрироваться</p>
          <button class="btn btn-primary" @click="openAuthModal">
            <i class="fas fa-sign-in-alt"></i> Войти / Зарегистрироваться
          </button>
        </div>
      </div>

      <!-- Последние проекты -->
      <div class="projects-section">
        <div class="section-header">
          <h3><i class="fas fa-history"></i> Последние проекты</h3>
          <button class="btn btn-secondary" @click="fetchProjects" :disabled="isLoading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            Обновить
          </button>
        </div>

        <div v-if="isLoading && projects.length === 0" class="loading">
          <i class="fas fa-spinner fa-spin"></i> Загрузка проектов...
        </div>

        <div v-else-if="projects.length === 0" class="no-projects">
          <i class="fas fa-inbox"></i>
          <p>Пока нет загруженных проектов. Будьте первым!</p>
        </div>

        <div v-else class="projects-grid">
          <div v-for="project in projects" :key="project.id" class="project-card">
            <div class="project-header">
              <div class="project-type">
                <i :class="getProjectTypeIcon(project.project_type)"></i>
                <span>{{ getProjectTypeText(project.project_type) }}</span>
              </div>
              <div class="project-status" :style="{ color: getStatusColor(project.status) }">
                {{ getStatusText(project.status) }}
              </div>
            </div>

            <h4 class="project-title">{{ project.title }}</h4>

            <p v-if="project.description" class="project-description">
              {{ project.description.substring(0, 150) }}{{ project.description.length > 150 ? '...' : '' }}
            </p>

            <div class="project-meta">
              <div class="meta-item">
                <i class="fas fa-user"></i>
                <span>{{ project.user_name }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-calendar"></i>
                <span>{{ formatDate(project.created_at) }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-file"></i>
                <span>{{ project.file_name }}</span>
              </div>
            </div>

            <div class="project-footer">
              <div class="project-rating">
                <span>Статус: {{ getStatusText(project.status) }}</span>
              </div>
              <div class="project-actions">
                <button
                    class="btn btn-sm btn-outline"
                    @click="viewProjectDetails(project)"
                    title="Подробнее"
                >
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="projects-footer">
          <p>Хотите увидеть больше проектов? <a href="#" @click.prevent="fetchProjects">Обновить список</a></p>
        </div>
      </div>
    </div>
  </section>

  <!-- Модальное окно просмотра проекта -->
  <div v-if="showProjectDetailsModal" class="modal-overlay" @click.self="showProjectDetailsModal = false">
    <div class="modal modal-large">
      <div class="modal-header">
        <h3><i class="fas fa-rocket"></i> Детали проекта</h3>
        <button class="modal-close" @click="showProjectDetailsModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="projectDetailsLoading" class="loading">
          <i class="fas fa-spinner fa-spin"></i> Загрузка деталей...
        </div>
        <div v-else-if="selectedProject" class="project-details">
          <div class="project-header-details">
            <div class="project-title-details">
              <h2>{{ selectedProject.title }}</h2>
              <div class="project-meta-details">
                <span class="project-type" :style="{ color: getStatusColor(selectedProject.status) }">
                  <i :class="getProjectTypeIcon(selectedProject.project_type)"></i>
                  {{ getProjectTypeText(selectedProject.project_type) }}
                </span>
                <span class="project-status-details" :style="{ color: getStatusColor(selectedProject.status) }">
                  {{ getStatusText(selectedProject.status) }}
                </span>
              </div>
            </div>
          </div>

          <div class="project-info-details">
            <div class="info-section">
              <h4><i class="fas fa-user"></i> Информация об авторе</h4>
              <div class="info-grid">
                <div class="info-item">
                  <strong>Имя:</strong> {{ selectedProject.user_name }}
                </div>
                <div v-if="selectedProject.user_email" class="info-item">
                  <strong>Email:</strong> {{ selectedProject.user_email }}
                </div>
                <div v-if="selectedProject.user_phone" class="info-item">
                  <strong>Телефон:</strong> {{ selectedProject.user_phone }}
                </div>
                <div class="info-item">
                  <strong>Дата загрузки:</strong> {{ formatDate(selectedProject.created_at) }}
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4><i class="fas fa-info-circle"></i> Описание проекта</h4>
              <div class="description-box">
                {{ selectedProject.description || 'Описание отсутствует' }}
              </div>
            </div>

            <div class="info-section">
              <h4><i class="fas fa-file"></i> Информация о файле</h4>
              <div class="info-grid">
                <div class="info-item">
                  <strong>Имя файла:</strong> {{ selectedProject.file_name }}
                </div>
                <div class="info-item">
                  <strong>Размер файла:</strong> {{ formatFileSize(selectedProject.file_size) }}
                </div>
                <div class="info-item">
                  <strong>Тип проекта:</strong> {{ getProjectTypeText(selectedProject.project_type) }}
                </div>
                <div class="info-item">
                  <strong>ID проекта:</strong> {{ selectedProject.id }}
                </div>
              </div>
            </div>

            <div v-if="selectedProject.admin_comment" class="info-section">
              <h4><i class="fas fa-comment-dots"></i> Комментарий администратора</h4>
              <div class="comment-box">
                {{ selectedProject.admin_comment }}
              </div>
            </div>
          </div>

          <div class="project-actions-details">
            <button class="btn btn-secondary" @click="showProjectDetailsModal = false">
              <i class="fas fa-times"></i> Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* КБ Будущего */
.upload-section {
  margin: 40px 0;
}

.upload-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.upload-card h3 {
  color: var(--primary-color);
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.success-message {
  background-color: rgba(46, 204, 113, 0.1);
  border: 1px solid var(--success-color);
  color: var(--success-color);
  padding: 15px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message {
  background-color: rgba(255, 64, 129, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
  padding: 15px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
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

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: 1rem;
  transition: var(--transition);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(0, 176, 255, 0.1);
}

.file-upload {
  position: relative;
}

.file-upload input[type="file"] {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.file-upload-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border: 2px dashed var(--secondary-color);
  border-radius: var(--border-radius);
  background-color: rgba(0, 176, 255, 0.05);
  cursor: pointer;
  transition: var(--transition);
}

.file-upload-label:hover {
  background-color: rgba(0, 176, 255, 0.1);
}

.file-upload-label i {
  color: var(--secondary-color);
}

.file-hint {
  display: block;
  margin-top: 5px;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.auth-required {
  margin: 40px 0;
}

.auth-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 40px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.auth-card h3 {
  color: var(--primary-color);
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.auth-card p {
  color: var(--gray-color);
  margin-bottom: 25px;
}

.projects-section {
  margin-top: 60px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h3 {
  color: var(--dark-color);
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--secondary-color);
}

.loading i {
  margin-right: 10px;
}

.no-projects {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-color);
}

.no-projects i {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.3;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.project-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 25px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.project-type {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--secondary-color);
  font-weight: 600;
  font-size: 0.9rem;
}

.project-status {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  background-color: rgba(0, 0, 0, 0.05);
}

.project-title {
  color: var(--dark-color);
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.project-description {
  color: var(--gray-color);
  line-height: 1.5;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--gray-color);
  font-size: 0.85rem;
}

.meta-item i {
  font-size: 0.8rem;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--dark-color);
  font-weight: 600;
}

.project-actions {
  display: flex;
  gap: 5px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
  min-width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--secondary-color);
  color: var(--secondary-color);
}

.btn-outline:hover:not(:disabled) {
  background: var(--secondary-color);
  color: white;
}

.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.projects-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.projects-footer a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
}

.projects-footer a:hover {
  text-decoration: underline;
}

/* Модальные окна */
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
  z-index: 3000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: var(--border-radius);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;
}

.modal-large {
  max-width: 800px;
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

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  color: var(--primary-color);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--gray-color);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.modal-close:hover {
  color: var(--accent-color);
  background-color: rgba(0, 0, 0, 0.05);
}

.modal-body {
  padding: 20px;
}

/* Детали проекта */
.project-details {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.project-header-details {
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 20px;
}

.project-title-details h2 {
  color: var(--primary-color);
  margin: 0 0 15px 0;
  font-size: 1.8rem;
}

.project-meta-details {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.project-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.9rem;
}

.project-status-details {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 5px 15px;
  border-radius: 20px;
  background-color: rgba(0, 0, 0, 0.05);
}

.project-info-details {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-section {
  background: #f8f9fa;
  border-radius: var(--border-radius);
  padding: 20px;
  border-left: 4px solid var(--secondary-color);
}

.info-section h4 {
  color: var(--primary-color);
  margin-top: 0;
  margin-bottom: 15px;
  font-family: var(--font-heading);
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  padding: 10px;
  background: white;
  border-radius: var(--border-radius);
  border: 1px solid #e0e0e0;
}

.info-item strong {
  color: var(--primary-color);
  margin-right: 5px;
}

.description-box {
  background: white;
  padding: 15px;
  border-radius: var(--border-radius);
  border: 1px solid #e0e0e0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.comment-box {
  background: white;
  padding: 15px;
  border-radius: var(--border-radius);
  border: 1px solid #ffc107;
  line-height: 1.6;
  white-space: pre-wrap;
  background-color: #fff8e1;
}

.project-actions-details {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

</style>