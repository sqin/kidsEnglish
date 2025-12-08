<template>
  <div class="progress-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="$router.push('/')">
      ← 返回
    </button>

    <h1 class="title">我的成就</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-icon">⭐</span>
        <span class="stat-value">{{ store.totalStars }}</span>
        <span class="stat-label">总星星</span>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🔥</span>
        <span class="stat-value">{{ store.streakDays }}</span>
        <span class="stat-label">连续打卡</span>
      </div>
      <div class="stat-card">
        <span class="stat-icon">📚</span>
        <span class="stat-value">{{ completedLetters }}</span>
        <span class="stat-label">已学字母</span>
      </div>
    </div>

    <!-- 成就徽章 -->
    <div class="badges-section">
      <h2>成就徽章</h2>
      <div class="badges-grid">
        <div
          class="badge"
          v-for="badge in badges"
          :key="badge.id"
          :class="{ earned: badge.earned }"
        >
          <span class="badge-icon">{{ badge.icon }}</span>
          <span class="badge-name">{{ badge.name }}</span>
          <span class="badge-desc">{{ badge.description }}</span>
        </div>
      </div>
    </div>

    <!-- 字母进度 -->
    <div class="letters-progress">
      <h2>学习进度</h2>
      <div class="letters-grid">
        <div
          class="letter-item"
          v-for="letter in store.letters"
          :key="letter.id"
          :class="getProgressClass(letter.id)"
        >
          <span class="letter-char">{{ letter.letter }}</span>
          <div class="letter-stars">
            <span
              v-for="i in 3"
              :key="i"
              :class="{ active: i <= store.getLetterProgress(letter.id).score }"
            >★</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLearningStore } from '../stores/learning'

const store = useLearningStore()

const completedLetters = computed(() => {
  return Object.values(store.progress).filter(p => p.completed).length
})

const badges = computed(() => [
  {
    id: 1,
    icon: '🌟',
    name: '初学者',
    description: '完成第1个字母',
    earned: completedLetters.value >= 1
  },
  {
    id: 2,
    icon: '📖',
    name: '小学徒',
    description: '完成5个字母',
    earned: completedLetters.value >= 5
  },
  {
    id: 3,
    icon: '🎓',
    name: '字母达人',
    description: '完成全部26个字母',
    earned: completedLetters.value >= 26
  },
  {
    id: 4,
    icon: '🔥',
    name: '坚持者',
    description: '连续打卡7天',
    earned: store.streakDays >= 7
  },
  {
    id: 5,
    icon: '⭐',
    name: '发音之星',
    description: '获得30颗星星',
    earned: store.totalStars >= 30
  },
  {
    id: 6,
    icon: '👑',
    name: '满星王者',
    description: '所有字母获得3星',
    earned: store.letters.every(l => store.getLetterProgress(l.id).score >= 3)
  }
])

const getProgressClass = (letterId) => {
  const progress = store.getLetterProgress(letterId)
  if (progress.score >= 3) return 'perfect'
  if (progress.score >= 1) return 'learned'
  return ''
}
</script>

<style scoped>
.progress-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 40px;
}

.back-btn {
  background: rgba(255,255,255,0.3);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 18px;
  cursor: pointer;
  margin-bottom: 20px;
}

.title {
  text-align: center;
  color: white;
  font-size: 32px;
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.stat-icon {
  font-size: 36px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.badges-section, .letters-progress {
  background: rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.badges-section h2, .letters-progress h2 {
  color: white;
  font-size: 22px;
  margin-bottom: 15px;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.badge {
  background: rgba(255,255,255,0.2);
  border-radius: 15px;
  padding: 15px 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  filter: grayscale(100%);
  opacity: 0.5;
  transition: all 0.3s;
}

.badge.earned {
  filter: none;
  opacity: 1;
  background: rgba(255,255,255,0.9);
}

.badge-icon {
  font-size: 36px;
}

.badge-name {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.badge-desc {
  font-size: 12px;
  color: #666;
}

.letters-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}

.letter-item {
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
  padding: 10px 5px;
  text-align: center;
}

.letter-item.learned {
  background: rgba(255,255,255,0.5);
}

.letter-item.perfect {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.letter-char {
  font-size: 24px;
  font-weight: bold;
  color: white;
  display: block;
}

.letter-item.learned .letter-char,
.letter-item.perfect .letter-char {
  color: #333;
}

.letter-stars {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
}

.letter-stars span.active {
  color: #ffd700;
}
</style>
