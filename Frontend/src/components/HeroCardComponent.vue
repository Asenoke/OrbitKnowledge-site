<script setup>
const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['openModal'])

const handleClick = () => {
  console.log('HeroCardComponent: Клик по кнопке, hero:', props.event)
  emit('openModal', props.event)
}
</script>

<template>
  <div class="hero-card">
    <div class="hero-card-image" :style="{ backgroundImage: `url(${event.image_url || '/placeholder.jpg'})` }">
      <span class="hero-era">{{ event.era }}</span>
    </div>
    <div class="hero-card__content">
      <h3>{{ event.name || 'Без названия' }}</h3>
      <p class="hero-card-role">{{ event.role || 'Роль не указана' }}</p>
      <p class="hero-card-achievements">{{ event.achievements || event.description || 'Достижения не указаны' }}</p>

      <div class="hero-tags" v-if="event.tags">
        <span class="tag" v-if="Array.isArray(event.tags)" v-for="tag in event.tags" :key="tag">
          {{ tag }}
        </span>
        <span class="tag" v-else-if="typeof event.tags === 'string'" v-for="(tag, index) in event.tags.split(',').map(t => t.trim()).filter(t => t.length > 0)" :key="index">
          {{ tag }}
        </span>
      </div>

      <button class="btn-card" @click="handleClick">
        Изучить досье <i class="fas fa-external-link-alt"></i>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Карточки героев */
.hero-card {
  background-color: white;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--box-shadow);
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 450px;
}

.hero-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.hero-card-image {
  height: 200px;
  min-height: 200px;
  background-size: cover;
  background-position: center;
  position: relative;
  background-color: #f0f0f0;
  flex-shrink: 0;
}

.hero-era {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: var(--accent-color);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  z-index: 1;
}

.hero-card__content {
  padding: 25px;
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
}

.hero-card__content h3 {
  margin: 0 0 12px 0;
  color: var(--primary-color);
  font-size: 1.3rem;
  line-height: 1.3;
  min-height: 35px;
  display: flex;
  align-items: center;
}

.hero-card-role {
  color: var(--secondary-color);
  font-weight: 600;
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  min-height: 20px;
}

.hero-card-achievements {
  margin: 0 0 15px 0;
  font-size: 0.9rem;
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 67.5px;
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 20px 0;
  min-height: 32px;
}

.tag {
  background-color: rgba(0, 176, 255, 0.1);
  color: var(--secondary-color);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-block;
  white-space: nowrap;
  height: fit-content;
  word-break: keep-all;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.btn-card {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  width: 100%;
  height: 46px;
  flex-shrink: 0;
  margin-top: auto;
  box-sizing: border-box;
}

.btn-card:hover {
  background-color: var(--secondary-color);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 176, 255, 0.3);
}

.btn-card i {
  font-size: 0.8rem;
}

</style>