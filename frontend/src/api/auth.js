import http from './http'

export const authAPI = {
  // 用户注册
  register(nickname, password) {
    return http.post('/api/auth/register', {
      nickname,
      password
    })
  },

  // 用户登录
  login(nickname, password) {
    const formData = new URLSearchParams()
    formData.append('username', nickname)
    formData.append('password', password)

    return http.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 获取当前用户信息
  getMe() {
    return http.get('/api/auth/me')
  }
}
