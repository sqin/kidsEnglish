import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { useUserStore } from './stores/user'
import { preloadCriticalResources, optimizeScroll, adjustQualityBasedOnDevice } from './utils/performance'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 初始化用户状态
const userStore = useUserStore()
userStore.initUser()

// 性能优化
preloadCriticalResources()
optimizeScroll()
adjustQualityBasedOnDevice()

app.mount('#app')
