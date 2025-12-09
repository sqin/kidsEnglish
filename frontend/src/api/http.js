import axios from 'axios'

// 创建axios实例
const http = axios.create({
  baseURL: `http://${window.location.hostname}:20000`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 自动添加token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理401错误
http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 如果是登录接口本身的401，不进行跳转，直接返回错误给页面处理
      if (error.config.url.includes('/auth/login')) {
        return Promise.reject(error)
      }
      
      // 其他接口的401才认为是token过期
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default http
