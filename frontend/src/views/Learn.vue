<template>
  <div class="learn-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="$router.back()">
      ← 返回
    </button>

    <!-- 字母展示区 -->
    <div class="letter-display" ref="letterRef" @click="handlePlayLetter">
      <div class="big-letter">{{ currentLetter.letter }}</div>
      <div class="small-letter">{{ currentLetter.letter.toLowerCase() }}</div>
    </div>

    <!-- 关联单词 -->
    <div class="word-section" @click="handlePlayWord">
      <span class="word-image">{{ currentLetter.image }}</span>
      <span class="word-text">{{ currentLetter.word }}</span>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <!-- 跟读练习 -->
      <button class="action-btn record-btn" @click="goToRecord">
        <span class="btn-icon">🎤</span>
        <span>跟读</span>
      </button>
    </div>

    <!-- 进度指示 -->
    <div class="progress-indicator">
      <div
        class="progress-dot"
        :class="{ active: progress.stage >= 1 }"
      >1</div>
      <div class="progress-line" :class="{ active: progress.stage >= 2 }"></div>
      <div
        class="progress-dot"
        :class="{ active: progress.stage >= 2 }"
      >2</div>
      <div class="progress-line" :class="{ active: progress.stage >= 3 }"></div>
      <div
        class="progress-dot"
        :class="{ active: progress.stage >= 3 }"
      >3</div>
    </div>

    <!-- 阶段提示 -->
    <div class="stage-hint">
      <span v-if="progress.stage === 0">第一步：点击字母或单词听发音 👆</span>
      <span v-else-if="progress.stage === 1">第二步：跟着读一读 🎤</span>
      <span v-else-if="progress.stage >= 2">太棒了！继续练习 🌟</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '../stores/learning'
import { useAudio } from '../composables/useAudio'
import gsap from 'gsap'

const route = useRoute()
const router = useRouter()
const store = useLearningStore()
const letterRef = ref(null)
const { playLetterSound, playWordSound, playRewardSound } = useAudio()

const currentLetter = computed(() => {
  const letter = route.params.letter.toUpperCase()
  return store.letters.find(l => l.letter === letter) || store.letters[0]
})

const progress = computed(() => {
  return store.getLetterProgress(currentLetter.value.id)
})

// 播放字母发音
const handlePlayLetter = () => {
  playLetterSound(currentLetter.value.letter)

  if (letterRef.value) {
    gsap.fromTo(letterRef.value,
      { scale: 1 },
      { scale: 1.1, duration: 0.3, yoyo: true, repeat: 1 }
    )
  }

  if (progress.value.stage === 0) {
    store.updateProgress(currentLetter.value.id, 1, 0)
  }
}

// 播放单词发音
const handlePlayWord = () => {
  playWordSound(currentLetter.value.word)

  if (progress.value.stage === 0) {
    store.updateProgress(currentLetter.value.id, 1, 0)
  }
}

// 跳转到录音页
const goToRecord = () => {
  router.push(`/record/${currentLetter.value.letter}`)
}

// 入场动画
onMounted(() => {
  if (letterRef.value) {
    gsap.from(letterRef.value, {
      scale: 0,
      rotation: -180,
      duration: 0.8,
      ease: 'back.out(1.7)'
    })
  }
})
</script>

<style scoped>
.learn-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.back-btn {
  align-self: flex-start;
  background: rgba(255,255,255,0.3);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 18px;
  cursor: pointer;
  margin-bottom: 20px;
}

.letter-display {
  background: white;
  border-radius: 30px;
  padding: 40px 60px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  margin-bottom: 30px;
  cursor: pointer;
}

.big-letter {
  font-size: 120px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.small-letter {
  font-size: 80px;
  color: #666;
  margin-top: 10px;
}

.word-section {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255,255,255,0.9);
  padding: 20px 40px;
  border-radius: 20px;
  margin-bottom: 40px;
  cursor: pointer;
}

.word-image {
  font-size: 50px;
}

.word-text {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 25px 35px;
  border: none;
  border-radius: 20px;
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.2s;
  min-width: 120px;
}

.action-btn:active {
  transform: scale(0.95);
}

.listen-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.record-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-icon {
  font-size: 40px;
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 20px;
}

.progress-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  transition: background 0.3s;
}

.progress-dot.active {
  background: #4CAF50;
}

.progress-line {
  width: 50px;
  height: 4px;
  background: rgba(255,255,255,0.3);
  transition: background 0.3s;
}

.progress-line.active {
  background: #4CAF50;
}

.stage-hint {
  color: white;
  font-size: 20px;
  text-align: center;
  padding: 15px 30px;
  background: rgba(255,255,255,0.2);
  border-radius: 15px;
}
</style>
