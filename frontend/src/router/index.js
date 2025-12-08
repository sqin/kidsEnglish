import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/learn/:letter',
    name: 'Learn',
    component: () => import('../views/Learn.vue')
  },
  {
    path: '/record/:letter',
    name: 'Record',
    component: () => import('../views/Record.vue')
  },
  {
    path: '/progress',
    name: 'Progress',
    component: () => import('../views/Progress.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 如果未登录且访问需要认证的页面，跳转到登录页
  if (!token && to.path !== '/login') {
    next('/login')
  } else if (token && to.path === '/login') {
    // 如果已登录且访问登录页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
