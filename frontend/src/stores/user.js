import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  // 是否已登录
  const isLoggedIn = computed(() => !!token.value)

  // 设置用户信息
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  // 登录
  const login = async (nickname, password) => {
    const response = await authAPI.login(nickname, password)
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)

    // 获取用户信息
    const userInfo = await authAPI.getMe()
    setUser(userInfo)

    return response
  }

  // 注册
  const register = async (nickname, password) => {
    const response = await authAPI.register(nickname, password)
    // 注册成功后自动登录
    return await login(nickname, password)
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 初始化时从localStorage恢复用户信息
  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('Failed to parse saved user:', e)
        logout()
      }
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    initUser
  }
})
