<script setup>
const props = defineProps({
  hero: {
    type: Object,
    default: null
  },
  isVisible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const closeModal = () => {
  console.log('ModalHeroComponent: close вызван')
  emit('close')
}
</script>

<template>
  <div v-if="isVisible" class="modal-hero-overlay" @click="closeModal">
    <div class="modal-hero" @click.stop>
      <div class="modal__content">
        <span class="close-modal" @click="closeModal">&times;</span>

        <div class="modal-header">
          <div class="modal-hero-image"
               :style="{ backgroundImage: `url(${hero?.image_url || '/placeholder.jpg'})` }">
            <span class="modal-hero-era">{{ hero?.era }}</span>
          </div>
          <div class="modal-hero-info">
            <h2>{{ hero?.name || 'Без названия' }}</h2>
            <p class="modal-hero-role">{{ hero?.role || 'Роль не указана' }}</p>
          </div>
        </div>

        <div class="modal-body">
          <div v-if="hero?.achievements" class="modal-section">
            <h3><i class="fas fa-award"></i> Достижения</h3>
            <p>{{ hero.achievements }}</p>
          </div>

          <div v-if="hero?.birth_date || hero?.death_date" class="modal-section">
            <h3><i class="fas fa-calendar-alt"></i> Даты жизни</h3>
            <div class="modal-dates">
              <div v-if="hero?.birth_date" class="date-item">
                <span class="date-label">Дата рождения:</span>
                <span class="date-value">{{ hero.birth_date }}</span>
              </div>
              <div v-if="hero?.death_date" class="date-item">
                <span class="date-label">Дата смерти:</span>
                <span class="date-value">{{ hero.death_date }}</span>
              </div>
            </div>
          </div>

          <div v-if="hero?.description" class="modal-section">
            <h3><i class="fas fa-file-alt"></i> Описание</h3>
            <p>{{ hero.description }}</p>
          </div>

          <div v-if="hero?.tags" class="modal-section">
            <h3><i class="fas fa-tags"></i> Характеристики</h3>
            <div class="modal-tags">
              <span v-if="Array.isArray(hero.tags)"
                    class="tag"
                    v-for="tag in hero.tags"
                    :key="tag">
                {{ tag }}
              </span>
              <span v-else-if="typeof hero.tags === 'string'"
                    class="tag"
                    v-for="(tag, index) in hero.tags.split(',').map(d => d.trim()).filter(d => d.length > 0)"
                    :key="index">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-primary" @click="closeModal">
            <i class="fas fa-check"></i> Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Оверлей модального окна */
.modal-hero-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 2000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

/* Модальное окно */
.modal-hero {
  background-color: white;
  border-radius: var(--border-radius);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal__content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.close-modal {
  position: absolute;
  top: 20px;
  right: 25px;
  font-size: 2.5rem;
  cursor: pointer;
  color: var(--gray-color);
  transition: var(--transition);
  background: none;
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  z-index: 10;
}

.close-modal:hover {
  color: var(--accent-color);
  background-color: rgba(0, 0, 0, 0.05);
}

/* Заголовок модального окна */
.modal-header {
  display: flex;
  gap: 25px;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7ff 0%, #e3eeff 100%);
  border-bottom: 1px solid #eaeaea;
}

.modal-hero-image {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  position: relative;
  flex-shrink: 0;
  border: 5px solid white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.modal-hero-era {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--accent-color);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.modal-hero-info {
  flex: 1;
}

.modal-hero-info h2 {
  color: var(--primary-color);
  margin: 0 0 10px 0;
  font-size: 2rem;
}

.modal-hero-role {
  color: var(--secondary-color);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

/* Тело модального окна */
.modal-body {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}

.modal-section {
  margin-bottom: 25px;
}

.modal-section h3 {
  color: var(--primary-color);
  margin-bottom: 10px;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-section h3 i {
  color: var(--secondary-color);
}

.modal-section p {
  line-height: 1.6;
  color: #555;
  margin: 0;
}

/* Даты */
.modal-dates {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.date-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-label {
  font-weight: 600;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.date-value {
  color: #555;
  font-size: 1.1rem;
}

/* Теги в модальном окне */
.modal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.modal-tags .tag {
  background-color: rgba(0, 176, 255, 0.1);
  color: var(--secondary-color);
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Футер модального окна */
.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #eaeaea;
  text-align: right;
  background-color: #f9f9f9;
}

.modal-footer .btn {
  padding: 12px 30px;
  font-size: 1rem;
}
</style>