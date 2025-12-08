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
    return http.post('/api/auth/login', null, {
      params: {
        username: nickname,
        password
      }
    })
  },

  // 获取当前用户信息
  getMe() {
    return http.get('/api/auth/me')
  }
}
