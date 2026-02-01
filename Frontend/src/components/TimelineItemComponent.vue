<script setup>
defineProps({
  event: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="timeline-item">
    <div class="timeline-date">{{ event.year }}</div>
    <div class="timeline-content">
      <h3>{{ event.title }}</h3>
      <p>{{ event.description }}</p>
    </div>
  </div>
</template>

<style scoped>
.timeline-item {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  position: relative;
}

.timeline-item:nth-child(odd) {
  flex-direction: row;
}

.timeline-item:nth-child(even) {
  flex-direction: row-reverse;
}

.timeline-date {
  flex: 0 0 120px;
  background-color: var(--primary-color);
  color: white;
  padding: 12px 20px;
  border-radius: 50px;
  text-align: center;
  font-weight: 700;
  font-family: var(--font-heading);
  font-size: 1.2rem;
  z-index: 1;
}

.timeline-content {
  flex: 0 0 calc(50% - 80px);
  background-color: white;
  padding: 25px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin: 0 20px;
}
</style>