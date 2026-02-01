<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const users = ref([])
const heroes = ref([])
const timelineEvents = ref([])
const projects = ref([])
const isLoading = ref(false)
const activeTab = ref('projects')
const searchQuery = ref('')
const stats = ref({
  totalUsers: 0,
  activeUsers: 0,
  totalHeroes: 0,
  totalEvents: 0,
  totalProjects: 0,
  pendingProjects: 0
})

// Для редактирования
const editingHero = ref(null)
const editingEvent = ref(null)
const editingProject = ref(null)
const showHeroEditModal = ref(false)
const showEventEditModal = ref(false)
const showProjectEditModal = ref(false)
const showProjectDetailsModal = ref(false)

// Для нового элемента
const showAddHeroModal = ref(false)
const showAddEventModal = ref(false)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Получаем токен
const getToken = () => {
  return localStorage.getItem('auth_token')
}

// Проверка прав администратора
const isAdmin = computed(() => {
  const role = localStorage.getItem('user_role')
  return role && role.toLowerCase() === 'admin'
})

const fetchStats = async () => {
  try {
    if (!isAdmin.value) return

    const token = getToken()

    // Статистика пользователей
    const usersResponse = await axios.get(`${API_BASE_URL}/user/admin/statistics`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    stats.value.totalUsers = usersResponse.data.total_users
    stats.value.activeUsers = usersResponse.data.users

    // Получаем всех героев для подсчета
    const heroesResponse = await axios.get(`${API_BASE_URL}/heroes/getAllHeroes?limit=1000`)
    stats.value.totalHeroes = heroesResponse.data.length

    // Получаем все события для подсчета
    const eventsResponse = await axios.get(`${API_BASE_URL}/lineevent/getAllLineEvents?limit=1000`)
    stats.value.totalEvents = eventsResponse.data.length

    // Статистика проектов
    await fetchProjectsStats()

  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

const fetchProjectsStats = async () => {
  try {
    const token = getToken()
    const response = await axios.get(`${API_BASE_URL}/projects/`, {
      params: {
        limit: 1000
      },
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    const projectsData = response.data.projects || []
    stats.value.totalProjects = projectsData.length
    stats.value.pendingProjects = projectsData.filter(p => p.status === 'pending').length
  } catch (error) {
    console.error('Error fetching projects stats:', error)
  }
}

const fetchUsers = async () => {
  try {
    if (!isAdmin.value) return

    isLoading.value = true
    const token = getToken()

    const response = await axios.get(`${API_BASE_URL}/user/admin/users?limit=100`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    users.value = response.data
  } catch (error) {
    console.error('Error fetching users:', error)
    if (error.response?.status === 401) {
      logout()
    } else {
      alert('Ошибка загрузки пользователей: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    isLoading.value = false
  }
}

const fetchHeroes = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(`${API_BASE_URL}/heroes/getAllHeroes?limit=100`)
    heroes.value = response.data
  } catch (error) {
    console.error('Error fetching heroes:', error)
    alert('Ошибка загрузки героев')
  } finally {
    isLoading.value = false
  }
}

const fetchTimelineEvents = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(`${API_BASE_URL}/lineevent/getAllLineEvents?limit=100`)
    timelineEvents.value = response.data
  } catch (error) {
    console.error('Error fetching events:', error)
    alert('Ошибка загрузки событий')
  } finally {
    isLoading.value = false
  }
}

// Получение проектов
const fetchProjects = async () => {
  try {
    isLoading.value = true
    const token = getToken()

    const response = await axios.get(`${API_BASE_URL}/projects/`, {
      params: {
        limit: 100,
        offset: 0
      },
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    projects.value = response.data.projects || []
    await fetchProjectsStats()
  } catch (error) {
    console.error('Error fetching projects:', error)
    alert('Ошибка загрузки проектов')
  } finally {
    isLoading.value = false
  }
}

// Принудительное обновление проектов
const forceRefreshProjects = async () => {
  try {
    isLoading.value = true
    const token = getToken()
    const timestamp = new Date().getTime()

    const response = await axios.get(`${API_BASE_URL}/projects/`, {
      params: {
        limit: 100,
        offset: 0,
        _t: timestamp
      },
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    projects.value = response.data.projects || []
    await fetchProjectsStats()
    alert('Проекты обновлены!')
  } catch (error) {
    console.error('Error force refreshing projects:', error)
    alert('Ошибка при обновлении проектов')
  } finally {
    isLoading.value = false
  }
}

// Просмотр деталей проекта
const viewProjectDetails = async (project) => {
  try {
    isLoading.value = true
    const token = getToken()

    // Получаем полную информацию о проекте
    const response = await axios.get(`${API_BASE_URL}/projects/${project.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    editingProject.value = response.data
    showProjectDetailsModal.value = true
  } catch (error) {
    console.error('Error fetching project details:', error)
    alert('Ошибка загрузки деталей проекта')
  } finally {
    isLoading.value = false
  }
}

// Редактирование проекта
const editProject = (project) => {
  editingProject.value = {
    ...project,
    status: project.status || 'pending',
    admin_comment: project.admin_comment || '',
  }
  showProjectEditModal.value = true
}

// Сохранение изменений проекта
const saveProjectEdit = async () => {
  if (!editingProject.value) return

  try {
    const token = getToken()
    isLoading.value = true

    const updateData = {
      status: editingProject.value.status,
      admin_comment: editingProject.value.admin_comment || ''
    }

    console.log('Updating project:', editingProject.value.id, updateData)

    // Пробуем разные эндпоинты
    const endpoints = [
      `${API_BASE_URL}/projects/${editingProject.value.id}`,
      `${API_BASE_URL}/projects/${editingProject.value.id}/`,
      `${API_BASE_URL}/projects/update/${editingProject.value.id}`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.put(
            endpoint,
            updateData,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
        )
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      // Пробуем PATCH как запасной вариант
      for (const endpoint of endpoints) {
        try {
          await axios.patch(
              endpoint,
              updateData,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
          )
          success = true
          break
        } catch (error) {
          lastError = error
          console.log(`PATCH failed with endpoint ${endpoint}:`, error.message)
        }
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось обновить проект')
    }

    alert('Проект успешно обновлен!')
    showProjectEditModal.value = false
    editingProject.value = null
    await fetchProjects()
  } catch (error) {
    console.error('Error updating project:', error)
    alert('Ошибка при обновлении проекта: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoading.value = false
  }
}

// Изменение статуса проекта
const changeProjectStatus = async (projectId, newStatus, projectTitle) => {
  const statusTexts = {
    'pending': 'на рассмотрение',
    'approved': 'одобрено',
    'rejected': 'отклонено',
    'featured': 'в зал славы'
  }

  if (!confirm(`Изменить статус проекта "${projectTitle}" на "${statusTexts[newStatus]}"?`)) return

  try {
    const token = getToken()

    // Пробуем разные эндпоинты и методы
    const endpoints = [
      `${API_BASE_URL}/projects/${projectId}/status`,
      `${API_BASE_URL}/projects/${projectId}`,
      `${API_BASE_URL}/projects/update/${projectId}/status`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        // Пробуем PATCH
        await axios.patch(
            endpoint,
            { status: newStatus },
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
        )
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`PATCH failed with endpoint ${endpoint}:`, error.message)

        // Пробуем PUT как запасной вариант
        try {
          await axios.put(
              endpoint,
              { status: newStatus },
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
          )
          success = true
          break
        } catch (putError) {
          console.log(`PUT failed with endpoint ${endpoint}:`, putError.message)
        }
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось изменить статус проекта')
    }

    await fetchProjects()
    alert('Статус проекта изменен')
  } catch (error) {
    console.error('Error changing project status:', error)
    alert('Ошибка при изменении статуса: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление проекта
const deleteProject = async (projectId, projectTitle) => {
  if (!confirm(`Удалить проект "${projectTitle}"? Это действие необратимо.`)) return

  try {
    const token = getToken()

    await axios.delete(`${API_BASE_URL}/projects/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    await fetchProjects()
    alert('Проект удален')
  } catch (error) {
    console.error('Error deleting project:', error)
    alert('Ошибка при удалении проекта: ' + (error.response?.data?.detail || error.message))
  }
}

// Кнопка добавления нового элемента
const openAddHeroModal = () => {
  editingHero.value = {
    name: '',
    role: '',
    era: '',
    description: '',
    image_url: '',
    birth_date: '',
    death_date: '',
    achievements: '',
    biography: '',
    tags_json: ''
  }
  showAddHeroModal.value = true
}

const openAddEventModal = () => {
  editingEvent.value = {
    title: '',
    year: new Date().getFullYear(),
    description: ''
  }
  showAddEventModal.value = true
}

// Редактирование героя
const editHero = (hero) => {
  editingHero.value = {
    ...hero,
    image_url: hero.image_url || '',
    birth_date: hero.birth_date || '',
    death_date: hero.death_date || '',
    achievements: hero.achievements || '',
    biography: hero.biography || '',
    tags_json: hero.tags ? JSON.stringify(hero.tags) : ''
  }
  showHeroEditModal.value = true
}

const saveHeroEdit = async () => {
  if (!editingHero.value) return

  try {
    const token = getToken()
    isLoading.value = true

    // Преобразуем теги из JSON строки в массив
    let tags = []
    if (editingHero.value.tags_json) {
      try {
        tags = JSON.parse(editingHero.value.tags_json)
      } catch (error) {
        console.error('Ошибка парсинга тегов:', error)
        alert('Ошибка в формате тегов. Используйте формат: ["тег1", "тег2"]')
        return
      }
    }

    // Формируем данные для обновления героя
    const heroData = {
      name: editingHero.value.name,
      role: editingHero.value.role,
      era: editingHero.value.era,
      description: editingHero.value.description,
      image_url: editingHero.value.image_url || '',
      birth_date: editingHero.value.birth_date || '',
      death_date: editingHero.value.death_date || '',
      achievements: editingHero.value.achievements || '',
      biography: editingHero.value.biography || '',
      tags: tags.length > 0 ? tags : null
    }

    // Убираем пустые строки
    Object.keys(heroData).forEach(key => {
      if (heroData[key] === undefined || heroData[key] === null || heroData[key] === '') {
        delete heroData[key]
      }
    })

    console.log('Updating hero:', editingHero.value.id, heroData)

    // Пробуем разные эндпоинты для обновления
    const endpoints = [
      `${API_BASE_URL}/heroes/${editingHero.value.id}`,
      `${API_BASE_URL}/heroes/updateHero/${editingHero.value.id}`,
      `${API_BASE_URL}/heroes/${editingHero.value.id}/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.put(endpoint, heroData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось обновить героя')
    }

    alert('Герой успешно обновлен!')
    showHeroEditModal.value = false
    editingHero.value = null
    await fetchHeroes()
  } catch (error) {
    console.error('Error updating hero:', error)
    alert('Ошибка при обновлении героя: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoading.value = false
  }
}

// Создание нового героя
const saveNewHero = async () => {
  if (!editingHero.value) return

  try {
    const token = getToken()
    isLoading.value = true

    // Преобразуем теги из JSON строки в массив
    let tags = []
    if (editingHero.value.tags_json) {
      try {
        tags = JSON.parse(editingHero.value.tags_json)
      } catch (error) {
        console.error('Ошибка парсинга тегов:', error)
        alert('Ошибка в формате тегов. Используйте формат: ["тег1", "тег2"]')
        return
      }
    }

    // Формируем данные для создания героя
    const heroData = {
      name: editingHero.value.name,
      role: editingHero.value.role,
      era: editingHero.value.era,
      description: editingHero.value.description,
      image_url: editingHero.value.image_url || '',
      birth_date: editingHero.value.birth_date || '',
      death_date: editingHero.value.death_date || '',
      achievements: editingHero.value.achievements || '',
      biography: editingHero.value.biography || '',
      tags: tags.length > 0 ? tags : null
    }

    console.log('Creating new hero:', heroData)

    // Пробуем разные эндпоинты для создания
    const endpoints = [
      `${API_BASE_URL}/heroes/createHero`,
      `${API_BASE_URL}/heroes`,
      `${API_BASE_URL}/heroes/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.post(endpoint, heroData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось создать героя')
    }

    alert('Герой успешно создан!')
    showAddHeroModal.value = false
    editingHero.value = null
    await fetchHeroes()
  } catch (error) {
    console.error('Error creating hero:', error)
    alert('Ошибка при создании героя: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoading.value = false
  }
}

// Редактирование события
const editEvent = (event) => {
  editingEvent.value = {
    ...event
  }
  showEventEditModal.value = true
}

const saveEventEdit = async () => {
  if (!editingEvent.value) return

  try {
    const token = getToken()
    isLoading.value = true

    // Формируем данные для обновления события
    const eventData = {
      title: editingEvent.value.title,
      year: editingEvent.value.year,
      description: editingEvent.value.description
    }

    console.log('Updating event:', editingEvent.value.id, eventData)

    // Пробуем разные эндпоинты для обновления
    const endpoints = [
      `${API_BASE_URL}/lineevent/${editingEvent.value.id}`,
      `${API_BASE_URL}/lineevent/updateLineEvent/${editingEvent.value.id}`,
      `${API_BASE_URL}/lineevent/${editingEvent.value.id}/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.put(endpoint, eventData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось обновить событие')
    }

    alert('Событие успешно обновлено!')
    showEventEditModal.value = false
    editingEvent.value = null
    await fetchTimelineEvents()
  } catch (error) {
    console.error('Error updating event:', error)
    alert('Ошибка при обновлении события: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoading.value = false
  }
}

// Создание нового события
const saveNewEvent = async () => {
  if (!editingEvent.value) return

  try {
    const token = getToken()
    isLoading.value = true

    // Формируем данные для создания события
    const eventData = {
      title: editingEvent.value.title,
      year: editingEvent.value.year,
      description: editingEvent.value.description
    }

    console.log('Creating new event:', eventData)

    // Пробуем разные эндпоинты для создания
    const endpoints = [
      `${API_BASE_URL}/lineevent/createLineEvent`,
      `${API_BASE_URL}/lineevent`,
      `${API_BASE_URL}/lineevent/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.post(endpoint, eventData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось создать событие')
    }

    alert('Событие успешно создано!')
    showAddEventModal.value = false
    editingEvent.value = null
    await fetchTimelineEvents()
  } catch (error) {
    console.error('Error creating event:', error)
    alert('Ошибка при создании события: ' + (error.response?.data?.detail || error.message))
  } finally {
    isLoading.value = false
  }
}

// Изменение роли пользователя
const changeUserRole = async (userId, newRole) => {
  if (!confirm(`Изменить роль пользователя на "${newRole}"?`)) return

  try {
    const token = getToken()

    await axios.put(
        `${API_BASE_URL}/user/admin/users/${userId}/role?new_role=${newRole}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
    )

    await fetchUsers()
    alert('Роль успешно изменена')
  } catch (error) {
    console.error('Error changing role:', error)
    alert('Ошибка при изменении роли: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление пользователя
const deleteUser = async (userId, userName) => {
  if (!confirm(`Удалить пользователя "${userName}"? Это действие необратимо.`)) return

  try {
    const token = getToken()

    await axios.delete(`${API_BASE_URL}/user/admin/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    await fetchUsers()
    alert('Пользователь удален')
  } catch (error) {
    console.error('Error deleting user:', error)
    alert('Ошибка при удалении пользователя: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление героя
const deleteHero = async (heroId, heroName) => {
  if (!confirm(`Удалить героя "${heroName}"?`)) return

  try {
    const token = getToken()

    // Пробуем разные эндпоинты для удаления
    const endpoints = [
      `${API_BASE_URL}/heroes/${heroId}`,
      `${API_BASE_URL}/heroes/deleteHero/${heroId}`,
      `${API_BASE_URL}/heroes/${heroId}/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.delete(endpoint, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось удалить героя')
    }

    await fetchHeroes()
    alert('Герой удален')
  } catch (error) {
    console.error('Error deleting hero:', error)
    alert('Ошибка при удалении героя: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление события
const deleteEvent = async (eventId, eventTitle) => {
  if (!confirm(`Удалить событие "${eventTitle}"?`)) return

  try {
    const token = getToken()

    // Пробуем разные эндпоинты для удаления
    const endpoints = [
      `${API_BASE_URL}/lineevent/${eventId}`,
      `${API_BASE_URL}/lineevent/deleteLineEvent/${eventId}`,
      `${API_BASE_URL}/lineevent/${eventId}/`
    ]

    let success = false
    let lastError = null

    for (const endpoint of endpoints) {
      try {
        await axios.delete(endpoint, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        success = true
        break
      } catch (error) {
        lastError = error
        console.log(`Failed with endpoint ${endpoint}:`, error.message)
      }
    }

    if (!success) {
      throw lastError || new Error('Не удалось удалить событие')
    }

    await fetchTimelineEvents()
    alert('Событие удалено')
  } catch (error) {
    console.error('Error deleting event:', error)
    alert('Ошибка при удалении события: ' + (error.response?.data?.detail || error.message))
  }
}

// Фильтрация
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value

  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user =>
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      (user.role && user.role.toLowerCase().includes(query))
  )
})

const filteredHeroes = computed(() => {
  if (!searchQuery.value) return heroes.value

  const query = searchQuery.value.toLowerCase()
  return heroes.value.filter(hero =>
      hero.name.toLowerCase().includes(query) ||
      (hero.role && hero.role.toLowerCase().includes(query)) ||
      (hero.era && hero.era.toLowerCase().includes(query))
  )
})

const filteredEvents = computed(() => {
  if (!searchQuery.value) return timelineEvents.value

  const query = searchQuery.value.toLowerCase()
  return timelineEvents.value.filter(event =>
      event.title.toLowerCase().includes(query) ||
      (event.description && event.description.toLowerCase().includes(query)) ||
      event.year.toString().includes(query)
  )
})

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value

  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(project =>
      project.title.toLowerCase().includes(query) ||
      (project.description && project.description.toLowerCase().includes(query)) ||
      project.user_name.toLowerCase().includes(query) ||
      project.project_type.toLowerCase().includes(query)
  )
})

// Фильтрация по статусу
const filteredProjectsByStatus = computed(() => {
  if (activeProjectFilter.value === 'all') return filteredProjects.value
  return filteredProjects.value.filter(project => project.status === activeProjectFilter.value)
})

// Фильтры для проектов
const projectFilters = [
  { value: 'all', label: 'Все', icon: 'fas fa-list' },
  { value: 'pending', label: 'На рассмотрении', icon: 'fas fa-clock', color: '#ffc107' },
  { value: 'approved', label: 'Одобренные', icon: 'fas fa-check-circle', color: '#28a745' },
  { value: 'rejected', label: 'Отклоненные', icon: 'fas fa-times-circle', color: '#dc3545' },
  { value: 'featured', label: 'В зале славы', icon: 'fas fa-star', color: '#ff4081' }
]

const activeProjectFilter = ref('all')

const getRoleColor = (role) => {
  const roleLower = role ? role.toLowerCase() : ''
  switch (roleLower) {
    case 'admin': return '#ff4081'
    case 'user': return '#00b0ff'
    default: return '#6c757d'
  }
}

const getRoleDisplay = (role) => {
  const roleLower = role ? role.toLowerCase() : ''
  switch (roleLower) {
    case 'admin': return 'Админ'
    case 'user': return 'Пользователь'
    default: return role || 'Не указана'
  }
}

// Получение цвета статуса проекта
const getProjectStatusColor = (status) => {
  switch(status) {
    case 'pending': return '#ffc107'
    case 'approved': return '#28a745'
    case 'rejected': return '#dc3545'
    case 'featured': return '#ff4081'
    default: return '#6c757d'
  }
}

// Получение текста статуса проекта
const getProjectStatusText = (status) => {
  switch(status) {
    case 'pending': return 'На рассмотрении'
    case 'approved': return 'Одобрено'
    case 'rejected': return 'Отклонено'
    case 'featured': return 'В зале славы'
    default: return status || 'Неизвестно'
  }
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

// Получение текста типа проекта
const getProjectTypeText = (type) => {
  switch(type) {
    case 'drawing': return 'Рисунок'
    case 'project': return 'Проект'
    case 'idea': return 'Идея'
    default: return type
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Форматирование размера файла
const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const logout = () => {
  localStorage.clear()
  window.location.href = '/'
}

const backToHome = () => {
  window.location.hash = ''
}

onMounted(() => {
  if (isAdmin.value) {
    fetchStats()
    fetchProjects()
  }
})
</script>

<template>
  <div class="admin-panel">
    <!-- Кнопка назад -->
    <div class="admin-back">
      <button class="btn btn-secondary" @click="backToHome">
        <i class="fas fa-arrow-left"></i> На главную
      </button>
    </div>

    <!-- Проверка прав -->
    <div v-if="!getToken()" class="admin-not-authorized">
      <div class="unauthorized-message">
        <i class="fas fa-lock"></i>
        <h3>Доступ запрещен</h3>
        <p>Для доступа к админ-панели необходимо войти в систему</p>
        <button class="btn btn-primary" @click="window.location.hash = '#/login'">
          <i class="fas fa-sign-in-alt"></i> Войти
        </button>
      </div>
    </div>

    <div v-else-if="!isAdmin" class="admin-not-authorized">
      <div class="unauthorized-message">
        <i class="fas fa-user-shield"></i>
        <h3>Недостаточно прав</h3>
        <p>Для доступа к админ-панели требуются права администратора</p>
        <p>Ваша роль: {{ localStorage.getItem('user_role') || 'Не определена' }}</p>
        <button class="btn btn-primary" @click="backToHome">
          <i class="fas fa-home"></i> Вернуться на главную
        </button>
      </div>
    </div>

    <div v-else class="admin-content">
      <!-- Заголовок -->
      <div class="admin-header">
        <h1><i class="fas fa-user-shield"></i> Административная панель</h1>
        <p class="admin-subtitle">Управление пользователями, героями, событиями и проектами</p>
      </div>

      <!-- Статистика -->
      <div class="admin-stats">
        <div class="stat-card">
          <div class="stat-icon" style="background-color: rgba(0, 176, 255, 0.1);">
            <i class="fas fa-users" style="color: var(--secondary-color);"></i>
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ stats.totalUsers }}</span>
            <span class="stat-label">Пользователей</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background-color: rgba(255, 64, 129, 0.1);">
            <i class="fas fa-user-astronaut" style="color: var(--accent-color);"></i>
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ stats.totalHeroes }}</span>
            <span class="stat-label">Героев</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background-color: rgba(255, 193, 7, 0.1);">
            <i class="fas fa-history" style="color: #ffc107;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ stats.totalEvents }}</span>
            <span class="stat-label">Событий</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background-color: rgba(40, 167, 69, 0.1);">
            <i class="fas fa-rocket" style="color: #28a745;"></i>
          </div>
          <div class="stat-info">
            <span class="stat-number">{{ stats.totalProjects }}</span>
            <span class="stat-label">Проектов</span>
            <small v-if="stats.pendingProjects > 0" class="stat-badge">
              {{ stats.pendingProjects }} на рассмотрении
            </small>
          </div>
        </div>
      </div>

      <!-- Панель навигации -->
      <div class="admin-tabs">
        <button
            class="tab-btn"
            :class="{ active: activeTab === 'projects' }"
            @click="activeTab = 'projects'; fetchProjects()"
        >
          <i class="fas fa-rocket"></i> Проекты
          <span v-if="stats.pendingProjects > 0" class="tab-badge">
            {{ stats.pendingProjects }}
          </span>
        </button>
        <button
            class="tab-btn"
            :class="{ active: activeTab === 'users' }"
            @click="activeTab = 'users'; fetchUsers()"
        >
          <i class="fas fa-users"></i> Пользователи
        </button>
        <button
            class="tab-btn"
            :class="{ active: activeTab === 'heroes' }"
            @click="activeTab = 'heroes'; fetchHeroes()"
        >
          <i class="fas fa-user-astronaut"></i> Герои
        </button>
        <button
            class="tab-btn"
            :class="{ active: activeTab === 'events' }"
            @click="activeTab = 'events'; fetchTimelineEvents()"
        >
          <i class="fas fa-history"></i> События
        </button>
      </div>

      <!-- Управление проектами -->
      <div v-if="activeTab === 'projects'" class="projects-management">
        <div class="management-header">
          <div class="project-filters">
            <div class="filter-buttons">
              <button
                  v-for="filter in projectFilters"
                  :key="filter.value"
                  class="filter-btn"
                  :class="{ active: activeProjectFilter === filter.value }"
                  @click="activeProjectFilter = filter.value"
                  :style="{ '--filter-color': filter.color }"
              >
                <i :class="filter.icon"></i>
                {{ filter.label }}
                <span v-if="filter.value !== 'all'" class="filter-count">
                  {{ projects.filter(p => p.status === filter.value).length }}
                </span>
              </button>
            </div>
          </div>

          <div class="refresh-controls">
            <button class="btn btn-secondary" @click="fetchProjects" :disabled="isLoading">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
              Обновить
            </button>
            <button class="btn btn-outline" @click="forceRefreshProjects" :disabled="isLoading" title="Принудительное обновление">
              <i class="fas fa-redo"></i>
            </button>
          </div>
        </div>

        <!-- Поиск -->
        <div class="admin-search">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по проектам..."
            />
          </div>
          <div class="search-info">
            Найдено: {{ filteredProjectsByStatus.length }}
          </div>
        </div>

        <!-- Таблица проектов -->
        <div class="projects-table-container">
          <div v-if="isLoading" class="loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка проектов...
          </div>

          <div v-else-if="filteredProjectsByStatus.length === 0" class="no-data">
            <i class="fas fa-inbox"></i>
            <p>Проекты не найдены</p>
            <button class="btn btn-secondary" @click="activeProjectFilter = 'all'; searchQuery = ''">
              <i class="fas fa-sync-alt"></i> Сбросить фильтры
            </button>
          </div>

          <div v-else class="projects-grid">
            <div v-for="project in filteredProjectsByStatus" :key="project.id" class="project-card-admin">
              <div class="project-header">
                <div class="project-type">
                  <i :class="getProjectTypeIcon(project.project_type)"></i>
                  <span>{{ getProjectTypeText(project.project_type) }}</span>
                </div>
                <div class="project-status" :style="{ backgroundColor: getProjectStatusColor(project.status) }">
                  {{ getProjectStatusText(project.status) }}
                </div>
              </div>

              <h4 class="project-title" :title="project.title">{{ project.title }}</h4>

              <p v-if="project.description" class="project-description">
                {{ project.description.substring(0, 100) }}{{ project.description.length > 100 ? '...' : '' }}
              </p>

              <div class="project-info">
                <div class="info-item">
                  <i class="fas fa-user"></i>
                  <span>{{ project.user_name }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-calendar"></i>
                  <span>{{ formatDate(project.created_at) }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-file"></i>
                  <span>{{ project.file_name }}</span>
                </div>
                <div class="info-item">
                  <i class="fas fa-weight"></i>
                  <span>{{ formatFileSize(project.file_size) }}</span>
                </div>
              </div>

              <div class="project-actions">
                <button
                    class="btn btn-sm btn-info"
                    @click="viewProjectDetails(project)"
                    title="Просмотреть детали"
                >
                  <i class="fas fa-eye"></i> Подробнее
                </button>

                <div class="action-buttons">
                  <button
                      v-if="project.status !== 'approved'"
                      class="btn-action btn-approve"
                      @click="changeProjectStatus(project.id, 'approved', project.title)"
                      title="Одобрить проект"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button
                      v-if="project.status !== 'rejected'"
                      class="btn-action btn-reject"
                      @click="changeProjectStatus(project.id, 'rejected', project.title)"
                      title="Отклонить проект"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                  <button
                      v-if="project.status === 'approved' && project.status !== 'featured'"
                      class="btn-action btn-featured"
                      @click="changeProjectStatus(project.id, 'featured', project.title)"
                      title="Добавить в зал славы"
                  >
                    <i class="fas fa-star"></i>
                  </button>
                  <button
                      class="btn-action btn-edit"
                      @click="editProject(project)"
                      title="Редактировать проект"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                      class="btn-action btn-delete"
                      @click="deleteProject(project.id, project.title)"
                      title="Удалить проект"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Управление пользователями -->
      <div v-if="activeTab === 'users'" class="users-management">
        <div class="management-header">
          <h3>Управление пользователями</h3>
          <button class="btn btn-secondary" @click="fetchUsers" :disabled="isLoading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            Обновить
          </button>
        </div>

        <!-- Поиск -->
        <div class="admin-search">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по пользователям..."
            />
          </div>
          <div class="search-info">
            Найдено: {{ filteredUsers.length }}
          </div>
        </div>

        <!-- Таблица пользователей -->
        <div class="admin-table-container">
          <div v-if="isLoading" class="loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка пользователей...
          </div>

          <div v-else-if="filteredUsers.length === 0" class="no-data">
            <i class="fas fa-users-slash"></i>
            <p>Пользователи не найдены</p>
          </div>

          <div v-else class="table-responsive">
            <table class="admin-table">
              <thead>
              <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Email</th>
                <th>Телефон</th>
                <th>Роль</th>
                <th>Действия</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone_number || '—' }}</td>
                <td>
                    <span class="role-badge" :style="{ backgroundColor: getRoleColor(user.role) }">
                      {{ getRoleDisplay(user.role) }}
                    </span>
                </td>
                <td class="actions">
                  <button
                      class="btn-action btn-change-role"
                      @click="changeUserRole(user.id, user.role === 'ADMIN' || user.role === 'admin' ? 'USER' : 'ADMIN')"
                      :title="user.role === 'ADMIN' || user.role === 'admin' ? 'Сделать пользователем' : 'Сделать администратором'"
                  >
                    <i class="fas" :class="(user.role === 'ADMIN' || user.role === 'admin') ? 'fa-user' : 'fa-user-shield'"></i>
                  </button>
                  <button
                      class="btn-action btn-delete"
                      @click="deleteUser(user.id, user.name)"
                      title="Удалить пользователя"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Управление героями -->
      <div v-if="activeTab === 'heroes'" class="heroes-management">
        <div class="management-header">
          <h3>Управление героями</h3>
          <div class="header-actions">
            <button class="btn btn-primary" @click="openAddHeroModal">
              <i class="fas fa-plus"></i> Добавить героя
            </button>
            <button class="btn btn-secondary" @click="fetchHeroes" :disabled="isLoading">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
              Обновить
            </button>
          </div>
        </div>

        <!-- Поиск -->
        <div class="admin-search">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по героям..."
            />
          </div>
          <div class="search-info">
            Найдено: {{ filteredHeroes.length }}
          </div>
        </div>

        <!-- Таблица героев -->
        <div class="admin-table-container">
          <div v-if="isLoading" class="loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка героев...
          </div>

          <div v-else-if="filteredHeroes.length === 0" class="no-data">
            <i class="fas fa-user-slash"></i>
            <p>Герои не найдены</p>
          </div>

          <div v-else class="table-responsive">
            <table class="admin-table">
              <thead>
              <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Роль</th>
                <th>Эпоха</th>
                <th>Описание</th>
                <th>Действия</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="hero in filteredHeroes" :key="hero.id">
                <td>{{ hero.id }}</td>
                <td>{{ hero.name }}</td>
                <td>{{ hero.role }}</td>
                <td>{{ hero.era }}</td>
                <td>{{ hero.description?.substring(0, 50) }}...</td>
                <td class="actions">
                  <button
                      class="btn-action btn-edit"
                      @click="editHero(hero)"
                      title="Редактировать героя"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                      class="btn-action btn-delete"
                      @click="deleteHero(hero.id, hero.name)"
                      title="Удалить героя"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Управление событиями -->
      <div v-if="activeTab === 'events'" class="events-management">
        <div class="management-header">
          <h3>Управление событиями</h3>
          <div class="header-actions">
            <button class="btn btn-primary" @click="openAddEventModal">
              <i class="fas fa-plus"></i> Добавить событие
            </button>
            <button class="btn btn-secondary" @click="fetchTimelineEvents" :disabled="isLoading">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
              Обновить
            </button>
          </div>
        </div>

        <!-- Поиск -->
        <div class="admin-search">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по событиям..."
            />
          </div>
          <div class="search-info">
            Найдено: {{ filteredEvents.length }}
          </div>
        </div>

        <!-- Таблица событий -->
        <div class="admin-table-container">
          <div v-if="isLoading" class="loading">
            <i class="fas fa-spinner fa-spin"></i> Загрузка событий...
          </div>

          <div v-else-if="filteredEvents.length === 0" class="no-data">
            <i class="fas fa-calendar-times"></i>
            <p>События не найдены</p>
          </div>

          <div v-else class="table-responsive">
            <table class="admin-table">
              <thead>
              <tr>
                <th>ID</th>
                <th>Год</th>
                <th>Название</th>
                <th>Описание</th>
                <th>Действия</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="event in filteredEvents" :key="event.id">
                <td>{{ event.id }}</td>
                <td><strong>{{ event.year }}</strong></td>
                <td>{{ event.title }}</td>
                <td>{{ event.description?.substring(0, 50) }}...</td>
                <td class="actions">
                  <button
                      class="btn-action btn-edit"
                      @click="editEvent(event)"
                      title="Редактировать событие"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                      class="btn-action btn-delete"
                      @click="deleteEvent(event.id, event.title)"
                      title="Удалить событие"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно просмотра проекта -->
  <div v-if="showProjectDetailsModal" class="modal-overlay" @click.self="showProjectDetailsModal = false">
    <div class="modal modal-large">
      <div class="modal-header">
        <h3><i class="fas fa-rocket"></i> Детали проекта</h3>
        <button class="modal-close" @click="showProjectDetailsModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingProject" class="project-details">
          <div class="project-header-details">
            <div class="project-title-details">
              <h2>{{ editingProject.title }}</h2>
              <div class="project-meta">
                <span class="project-type" :style="{ color: getProjectStatusColor(editingProject.status) }">
                  <i :class="getProjectTypeIcon(editingProject.project_type)"></i>
                  {{ getProjectTypeText(editingProject.project_type) }}
                </span>
                <span class="project-status-details" :style="{ backgroundColor: getProjectStatusColor(editingProject.status) }">
                  {{ getProjectStatusText(editingProject.status) }}
                </span>
              </div>
            </div>
          </div>

          <div class="project-info-details">
            <div class="info-section">
              <h4><i class="fas fa-user"></i> Информация об авторе</h4>
              <div class="info-grid">
                <div class="info-item">
                  <strong>Имя:</strong> {{ editingProject.user_name }}
                </div>
                <div class="info-item">
                  <strong>Email:</strong> {{ editingProject.user_email }}
                </div>
                <div class="info-item">
                  <strong>Телефон:</strong> {{ editingProject.user_phone }}
                </div>
                <div class="info-item">
                  <strong>Дата загрузки:</strong> {{ formatDate(editingProject.created_at) }}
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4><i class="fas fa-info-circle"></i> Описание проекта</h4>
              <div class="description-box">
                {{ editingProject.description || 'Описание отсутствует' }}
              </div>
            </div>

            <div class="info-section">
              <h4><i class="fas fa-file"></i> Информация о файле</h4>
              <div class="info-grid">
                <div class="info-item">
                  <strong>Имя файла:</strong> {{ editingProject.file_name }}
                </div>
                <div class="info-item">
                  <strong>Размер файла:</strong> {{ formatFileSize(editingProject.file_size) }}
                </div>
                <div class="info-item">
                  <strong>Тип проекта:</strong> {{ getProjectTypeText(editingProject.project_type) }}
                </div>
                <div class="info-item">
                  <strong>ID проекта:</strong> {{ editingProject.id }}
                </div>
              </div>
            </div>

            <div v-if="editingProject.admin_comment" class="info-section">
              <h4><i class="fas fa-comment-dots"></i> Комментарий администратора</h4>
              <div class="comment-box">
                {{ editingProject.admin_comment }}
              </div>
            </div>
          </div>

          <div class="project-actions-details">
            <button class="btn btn-secondary" @click="showProjectDetailsModal = false">
              <i class="fas fa-times"></i> Закрыть
            </button>
            <button class="btn btn-primary" @click="editProject(editingProject)">
              <i class="fas fa-edit"></i> Редактировать
            </button>
            <button v-if="editingProject.status !== 'approved'"
                    class="btn btn-success"
                    @click="changeProjectStatus(editingProject.id, 'approved', editingProject.title)">
              <i class="fas fa-check"></i> Одобрить
            </button>
            <button v-if="editingProject.status === 'approved' && editingProject.status !== 'featured'"
                    class="btn btn-featured"
                    @click="changeProjectStatus(editingProject.id, 'featured', editingProject.title)">
              <i class="fas fa-star"></i> В зал славы
            </button>
            <button v-if="editingProject.status !== 'rejected'"
                    class="btn btn-danger"
                    @click="changeProjectStatus(editingProject.id, 'rejected', editingProject.title)">
              <i class="fas fa-times"></i> Отклонить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования проекта -->
  <div v-if="showProjectEditModal" class="modal-overlay" @click.self="showProjectEditModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3><i class="fas fa-edit"></i> Редактирование проекта</h3>
        <button class="modal-close" @click="showProjectEditModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingProject" class="edit-form">
          <div class="form-section">
            <h4>Основные настройки</h4>
            <div class="form-group">
              <label>Статус проекта:</label>
              <select v-model="editingProject.status" class="status-select">
                <option value="pending">На рассмотрении</option>
                <option value="approved">Одобрено</option>
                <option value="rejected">Отклонено</option>
                <option value="featured">В зале славы</option>
              </select>
            </div>

            <div class="form-group">
              <label>Комментарий администратора:</label>
              <textarea
                  v-model="editingProject.admin_comment"
                  rows="3"
                  placeholder="Комментарий для пользователя..."
              ></textarea>
              <small class="form-hint">Будет виден автору проекта</small>
            </div>
          </div>

          <div class="form-section">
            <h4>Информация о проекте</h4>
            <div class="info-display">
              <p><strong>Название:</strong> {{ editingProject.title }}</p>
              <p><strong>Автор:</strong> {{ editingProject.user_name }}</p>
              <p><strong>Email:</strong> {{ editingProject.user_email }}</p>
              <p><strong>Тип:</strong> {{ getProjectTypeText(editingProject.project_type) }}</p>
              <p><strong>Дата загрузки:</strong> {{ formatDate(editingProject.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showProjectEditModal = false">Отмена</button>
        <button class="btn btn-primary" @click="saveProjectEdit" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Сохранение...
          </span>
          <span v-else>Сохранить изменения</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования героя -->
  <div v-if="showHeroEditModal" class="modal-overlay" @click.self="showHeroEditModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3><i class="fas fa-user-astronaut"></i> Редактирование героя</h3>
        <button class="modal-close" @click="showHeroEditModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingHero" class="edit-form">
          <!-- Основные данные для карточки -->
          <div class="form-section">
            <h4>Основные данные для карточки</h4>
            <div class="form-group">
              <label>Имя *:</label>
              <input v-model="editingHero.name" type="text" placeholder="Имя героя" required>
            </div>
            <div class="form-group">
              <label>Роль *:</label>
              <input v-model="editingHero.role" type="text" placeholder="Роль (пилот, космонавт, конструктор и т.д.)" required>
            </div>
            <div class="form-group">
              <label>Эпоха *:</label>
              <input v-model="editingHero.era" type="text" placeholder="Эпоха (XX век, XXI век, Золотой век авиации и т.д.)" required>
            </div>
            <div class="form-group">
              <label>URL изображения:</label>
              <input v-model="editingHero.image_url" type="text" placeholder="URL изображения (необязательно)">
              <small class="form-hint">Ссылка на фотографию героя</small>
            </div>
            <div class="form-group">
              <label>Описание для карточки *:</label>
              <textarea v-model="editingHero.description" rows="3" placeholder="Краткое описание для карточки" required></textarea>
              <small class="form-hint">Будет отображаться в карточке на главной странице</small>
            </div>
            <div class="form-group">
              <label>Теги (JSON):</label>
              <input v-model="editingHero.tags_json" type="text" placeholder='["авиация", "космонавтика", "пилот"]'>
              <small class="form-hint">В формате JSON массива строк</small>
            </div>
          </div>

          <!-- Данные для модального окна -->
          <div class="form-section">
            <h4>Детальная информация (для модального окна)</h4>
            <div class="form-group">
              <label>Дата рождения:</label>
              <input v-model="editingHero.birth_date" type="text" placeholder="Например: 12 апреля 1961 г.">
            </div>
            <div class="form-group">
              <label>Дата смерти:</label>
              <input v-model="editingHero.death_date" type="text" placeholder="Например: 27 марта 1968 г. (если применимо)">
            </div>
            <div class="form-group">
              <label>Достижения:</label>
              <textarea v-model="editingHero.achievements" rows="3" placeholder="Основные достижения и награды"></textarea>
              <small class="form-hint">Будет отображаться в модальном окне</small>
            </div>
            <div class="form-group">
              <label>Подробная биография:</label>
              <textarea v-model="editingHero.biography" rows="4" placeholder="Подробная биографическая информация"></textarea>
              <small class="form-hint">Полная биография для модального окна</small>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showHeroEditModal = false">Отмена</button>
        <button class="btn btn-primary" @click="saveHeroEdit" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Сохранение...
          </span>
          <span v-else>Сохранить</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Модальное окно создания нового героя -->
  <div v-if="showAddHeroModal" class="modal-overlay" @click.self="showAddHeroModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3><i class="fas fa-user-astronaut"></i> Создание нового героя</h3>
        <button class="modal-close" @click="showAddHeroModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingHero" class="edit-form">
          <!-- Основные данные для карточки -->
          <div class="form-section">
            <h4>Основные данные для карточки</h4>
            <div class="form-group">
              <label>Имя *:</label>
              <input v-model="editingHero.name" type="text" placeholder="Имя героя" required>
            </div>
            <div class="form-group">
              <label>Роль *:</label>
              <input v-model="editingHero.role" type="text" placeholder="Роль (пилот, космонавт, конструктор и т.д.)" required>
            </div>
            <div class="form-group">
              <label>Эпоха *:</label>
              <input v-model="editingHero.era" type="text" placeholder="Эпоха (XX век, XXI век, Золотой век авиации и т.д.)" required>
            </div>
            <div class="form-group">
              <label>URL изображения:</label>
              <input v-model="editingHero.image_url" type="text" placeholder="URL изображения (необязательно)">
              <small class="form-hint">Ссылка на фотографию героя</small>
            </div>
            <div class="form-group">
              <label>Описание для карточки *:</label>
              <textarea v-model="editingHero.description" rows="3" placeholder="Краткое описание для карточки" required></textarea>
              <small class="form-hint">Будет отображаться в карточке на главной странице</small>
            </div>
            <div class="form-group">
              <label>Теги (JSON):</label>
              <input v-model="editingHero.tags_json" type="text" placeholder='["авиация", "космонавтика", "пилот"]'>
              <small class="form-hint">В формате JSON массива строк</small>
            </div>
          </div>

          <!-- Данные для модального окна -->
          <div class="form-section">
            <h4>Детальная информация (для модального окна)</h4>
            <div class="form-group">
              <label>Дата рождения:</label>
              <input v-model="editingHero.birth_date" type="text" placeholder="Например: 12 апреля 1961 г.">
            </div>
            <div class="form-group">
              <label>Дата смерти:</label>
              <input v-model="editingHero.death_date" type="text" placeholder="Например: 27 марта 1968 г. (если применимо)">
            </div>
            <div class="form-group">
              <label>Достижения:</label>
              <textarea v-model="editingHero.achievements" rows="3" placeholder="Основные достижения и награды"></textarea>
              <small class="form-hint">Будет отображаться в модальном окне</small>
            </div>
            <div class="form-group">
              <label>Подробная биография:</label>
              <textarea v-model="editingHero.biography" rows="4" placeholder="Подробная биографическая информация"></textarea>
              <small class="form-hint">Полная биография для модального окна</small>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showAddHeroModal = false">Отмена</button>
        <button class="btn btn-primary" @click="saveNewHero" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Создание...
          </span>
          <span v-else>Создать</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования события -->
  <div v-if="showEventEditModal" class="modal-overlay" @click.self="showEventEditModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3><i class="fas fa-history"></i> Редактирование события</h3>
        <button class="modal-close" @click="showEventEditModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingEvent" class="edit-form">
          <div class="form-group">
            <label>Название *:</label>
            <input v-model="editingEvent.title" type="text" placeholder="Название события" required>
          </div>
          <div class="form-group">
            <label>Год *:</label>
            <input v-model="editingEvent.year" type="text" placeholder="Год события (например: 1903)" required>
            <small class="form-hint">В формате строки, например: "1903" или "1961 г."</small>
          </div>
          <div class="form-group">
            <label>Описание *:</label>
            <textarea v-model="editingEvent.description" rows="4" placeholder="Описание события" required></textarea>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showEventEditModal = false">Отмена</button>
        <button class="btn btn-primary" @click="saveEventEdit" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Сохранение...
          </span>
          <span v-else>Сохранить</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Модальное окно создания нового события -->
  <div v-if="showAddEventModal" class="modal-overlay" @click.self="showAddEventModal = false">
    <div class="modal">
      <div class="modal-header">
        <h3><i class="fas fa-history"></i> Создание нового события</h3>
        <button class="modal-close" @click="showAddEventModal = false">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="editingEvent" class="edit-form">
          <div class="form-group">
            <label>Название *:</label>
            <input v-model="editingEvent.title" type="text" placeholder="Название события" required>
          </div>
          <div class="form-group">
            <label>Год *:</label>
            <input v-model="editingEvent.year" type="text" placeholder="Год события (например: 1903)" required>
            <small class="form-hint">В формате строки, например: "1903" или "1961 г."</small>
          </div>
          <div class="form-group">
            <label>Описание *:</label>
            <textarea v-model="editingEvent.description" rows="4" placeholder="Описание события" required></textarea>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showAddEventModal = false">Отмена</button>
        <button class="btn btn-primary" @click="saveNewEvent" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i> Создание...
          </span>
          <span v-else>Создать</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-panel {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
  min-height: 600px;
  position: relative;
}

.admin-back {
  padding: 20px;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 10;
}

.admin-back .btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
}

.admin-not-authorized {
  padding: 100px 20px;
  text-align: center;
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

.admin-content {
  padding: 30px;
  padding-top: 80px;
}

.admin-header {
  margin-bottom: 30px;
}

.admin-header h1 {
  color: var(--primary-color);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.admin-subtitle {
  color: var(--gray-color);
  font-size: 1.1rem;
}

/* Статистика */
.admin-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
  transition: var(--transition);
  position: relative;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon i {
  font-size: 1.8rem;
}

.stat-info {
  flex: 1;
}

.stat-number {
  display: block;
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--gray-color);
  display: block;
}

.stat-badge {
  display: inline-block;
  background-color: #ffc107;
  color: #212529;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 5px;
  font-weight: 600;
}

/* Табы */
.admin-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 10px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 12px 24px;
  background: none;
  border: none;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-weight: 600;
  color: var(--gray-color);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.tab-btn:hover {
  color: var(--primary-color);
  background-color: #f5f7ff;
}

.tab-btn.active {
  color: white;
  background-color: var(--primary-color);
}

.tab-btn.active i {
  color: white;
}

.tab-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: var(--accent-color);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Фильтры проектов */
.project-filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: var(--border-radius);
}

.filter-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-weight: 600;
  color: var(--gray-color);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.filter-btn.active {
  border-color: var(--primary-color);
  background-color: var(--primary-color);
  color: white;
}

.filter-btn.active i {
  color: white;
}

.filter-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: 5px;
}

/* Поиск */
.admin-search {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  gap: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  max-width: 400px;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-color);
}

.search-box input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 2px solid #e0e0e0;
  border-radius: 50px;
  font-family: var(--font-body);
  font-size: 1rem;
  transition: var(--transition);
}

.search-box input:focus {
  outline: none;
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(0, 176, 255, 0.1);
}

.search-info {
  color: var(--gray-color);
  font-size: 0.9rem;
  white-space: nowrap;
}

/* Таблицы проектов */
.projects-table-container {
  margin-bottom: 40px;
  min-height: 300px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.project-card-admin {
  background: white;
  border-radius: var(--border-radius);
  padding: 20px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  border: 1px solid #eaeaea;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.project-card-admin:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--secondary-color);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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
  font-size: 0.7rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  color: white;
  text-transform: uppercase;
}

.project-title {
  color: var(--dark-color);
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-description {
  color: var(--gray-color);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

.project-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 15px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--gray-color);
  overflow: hidden;
}

.info-item i {
  color: var(--secondary-color);
  font-size: 0.8rem;
  width: 16px;
}

.info-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-action {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  color: white;
}

.btn-approve {
  background-color: #28a745;
}

.btn-reject {
  background-color: #dc3545;
}

.btn-featured {
  background-color: #ff4081;
}

.btn-edit {
  background-color: #ffc107;
}

.btn-delete {
  background-color: var(--accent-color);
}

.btn-action:hover {
  transform: scale(1.1);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.btn-info {
  background-color: var(--secondary-color);
  color: white;
}

.btn-info:hover {
  background-color: var(--primary-color);
  color: white;
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

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
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

.project-meta {
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
  color: white;
  text-transform: uppercase;
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

.btn-featured {
  background-color: #ff4081;
  color: white;
  border: none;
}

.btn-featured:hover {
  background-color: #e91e63;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
  border: none;
}

.btn-success:hover {
  background-color: #218838;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #c82333;
  color: white;
}

/* Формы редактирования проекта */
.edit-form .form-group {
  margin-bottom: 20px;
}

.edit-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--dark-color);
}

.status-select {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: 1rem;
}

.info-display {
  background: white;
  padding: 15px;
  border-radius: var(--border-radius);
  border: 1px solid #e0e0e0;
}

.info-display p {
  margin: 8px 0;
}

/* Остальные стили (users, heroes, events таблицы) остаются без изменений */

.loading {
  text-align: center;
  padding: 60px 20px;
  color: var(--secondary-color);
}

.loading i {
  margin-right: 10px;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-color);
}

.no-data i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: rgba(0, 0, 0, 0.1);
}

.table-responsive {
  overflow-x: auto;
  border-radius: var(--border-radius);
  border: 1px solid #eaeaea;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  min-width: 800px;
}

.admin-table thead {
  background-color: var(--primary-color);
  color: white;
}

.admin-table th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  font-family: var(--font-heading);
  white-space: nowrap;
}

.admin-table tbody tr {
  border-bottom: 1px solid #eaeaea;
  transition: var(--transition);
}

.admin-table tbody tr:hover {
  background-color: #f8f9fa;
}

.admin-table td {
  padding: 15px;
  vertical-align: middle;
}

.role-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.actions {
  display: flex;
  gap: 10px;
  white-space: nowrap;
}

.btn-change-role {
  background-color: var(--secondary-color);
}

.btn-edit {
  background-color: #ffc107;
}

.btn-delete {
  background-color: var(--accent-color);
}

/* Формы редактирования героя и события */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-section {
  background: #f8f9fa;
  border-radius: var(--border-radius);
  padding: 20px;
  border-left: 4px solid var(--primary-color);
}

.form-section h4 {
  color: var(--primary-color);
  margin-top: 0;
  margin-bottom: 15px;
  font-family: var(--font-heading);
  font-size: 1.1rem;
}

.edit-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.edit-form label {
  font-weight: 600;
  color: var(--dark-color);
  font-size: 0.9rem;
}

.edit-form input,
.edit-form textarea,
.edit-form select {
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: 1rem;
  transition: var(--transition);
  width: 100%;
}

.edit-form input:focus,
.edit-form textarea:focus,
.edit-form select:focus {
  outline: none;
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(0, 176, 255, 0.1);
}

.edit-form textarea {
  resize: vertical;
  min-height: 100px;
}

.edit-form input[required],
.edit-form textarea[required],
.edit-form select[required] {
  border-color: #ffc107;
}

.form-hint {
  color: var(--gray-color);
  font-size: 0.8rem;
  margin-top: 4px;
}

</style>