<template>
  <div class="home">
    <!-- 顶部状态栏 -->
    <header class="header">
      <div class="streak" v-if="store.streakDays > 0">
        <span class="fire">🔥</span>
        <span>{{ store.streakDays }}天</span>
      </div>
      <div class="stars">
        <span class="star-icon">⭐</span>
        <span>{{ store.totalStars }}</span>
      </div>
      <button class="logout-btn" @click="logout">登出</button>
    </header>

    <!-- 标题 -->
    <h1 class="title">学字母</h1>

    <!-- 字母网格 -->
    <div class="letter-grid">
      <LetterCard
        v-for="item in store.letters"
        :key="item.id"
        :letter="item.letter"
        :word="item.word"
        :image="item.image"
        :progress="store.getLetterProgress(item.id)"
        @click="goToLearn(item.letter)"
      />
    </div>

    <!-- 底部导航 -->
    <nav class="bottom-nav">
      <button class="nav-btn active">
        <span class="nav-icon">📚</span>
        <span>学习</span>
      </button>
      <button class="nav-btn" @click="$router.push('/progress')">
        <span class="nav-icon">🏆</span>
        <span>成就</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { useLearningStore } from '../stores/learning'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import LetterCard from '../components/LetterCard.vue'

const store = useLearningStore()
const userStore = useUserStore()
const router = useRouter()

const goToLearn = (letter) => {
  router.push(`/learn/${letter}`)
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-bottom: 100px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.logout-btn {
  background: rgba(255,255,255,0.3);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(255,255,255,0.5);
}

.streak, .stars {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,0.2);
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.fire { font-size: 24px; }
.star-icon { font-size: 24px; }

.title {
  text-align: center;
  color: white;
  font-size: 36px;
  margin: 20px 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.letter-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  max-width: 500px;
  margin: 0 auto;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  background: white;
  padding: 15px 0;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
}

.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  padding: 10px 30px;
}

.nav-btn.active {
  color: #667eea;
}

.nav-icon {
  font-size: 28px;
}
</style>
