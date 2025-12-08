<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="title">开始学习</h1>

      <div class="tabs">
        <button
          class="tab"
          :class="{ active: isLogin }"
          @click="isLogin = true"
        >
          登录
        </button>
        <button
          class="tab"
          :class="{ active: !isLogin }"
          @click="isLogin = false"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="input-group">
          <label>昵称</label>
          <input
            v-model="nickname"
            type="text"
            placeholder="给自己起个名字"
            required
          />
        </div>

        <div class="input-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="设置一个密码"
            required
            minlength="6"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <p class="error" v-if="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const isLogin = ref(true)
const nickname = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    if (isLogin.value) {
      // 登录
      await userStore.login(nickname.value, password.value)
    } else {
      // 注册
      await userStore.register(nickname.value, password.value)
    }

    // 跳转到首页
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 30px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.title {
  text-align: center;
  color: #333;
  font-size: 32px;
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: #f0f0f0;
  border-radius: 15px;
  padding: 5px;
}

.tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.tab.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 16px;
  color: #333;
  font-weight: bold;
}

.input-group input {
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
}

.submit-btn {
  padding: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 15px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
  margin-top: 10px;
}

.submit-btn:active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #ff4444;
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}
</style>
