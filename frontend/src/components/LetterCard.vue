<template>
  <div class="letter-card" :class="{ completed: progress.completed }" @click="$emit('click')">
    <div class="card-inner animate-pop">
      <span class="letter">{{ letter }}</span>
      <span class="image">{{ image }}</span>
      <div class="stars-earned" v-if="progress.score > 0" :class="{ 'animate-twinkle': progress.score > 0 }">
        <span v-for="i in progress.score" :key="i" class="star animate-fly-in">⭐</span>
      </div>
      <div class="lock-overlay" v-if="false">
        🔒
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  letter: String,
  word: String,
  image: String,
  progress: {
    type: Object,
    default: () => ({ stage: 0, score: 0, completed: false })
  }
})

defineEmits(['click'])
</script>

<style scoped>
.letter-card {
  aspect-ratio: 1;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.letter-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

.letter-card:active {
  transform: scale(0.95);
}

.letter-card.completed {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.card-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px;
  position: relative;
}

.letter {
  font-size: 42px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.image {
  font-size: 32px;
  margin-top: 5px;
}

.stars-earned {
  position: absolute;
  bottom: 8px;
  display: flex;
  gap: 2px;
  font-size: 14px;
}

.lock-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
}
</style>
