/**
 * 性能优化工具
 */

/**
 * 预加载关键资源
 */
export function preloadCriticalResources() {
  // 预加载首屏需要的资源
  const preloadLinks = [
    { href: '/audio/a.mp3', as: 'audio' },
    { href: '/audio/e.mp3', as: 'audio' },
    { href: '/audio/i.mp3', as: 'audio' },
    { href: '/audio/o.mp3', as: 'audio' },
    { href: '/audio/u.mp3', as: 'audio' }
  ]

  preloadLinks.forEach(link => {
    const preloadLink = document.createElement('link')
    preloadLink.rel = 'preload'
    preloadLink.href = link.href
    preloadLink.as = link.as
    document.head.appendChild(preloadLink)
  })
}

/**
 * 图片懒加载
 */
export function lazyLoadImages() {
  const images = document.querySelectorAll('img[data-src]')
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.remove('lazy')
        imageObserver.unobserve(img)
      }
    })
  })

  images.forEach(img => imageObserver.observe(img))
}

/**
 * 防抖函数
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 监听页面可见性变化
 */
export function onVisibilityChange(callback) {
  document.addEventListener('visibilitychange', () => {
    callback(document.visibilityState)
  })
}

/**
 * 优化滚动性能
 */
export function optimizeScroll() {
  // 禁用滚动时的动画
  let scrollTimeout
  window.addEventListener('scroll', () => {
    document.body.classList.add('is-scrolling')
    clearTimeout(scrollTimeout)
    scrollTimeout = setTimeout(() => {
      document.body.classList.remove('is-scrolling')
    }, 100)
  }, { passive: true })
}

/**
 * 内存优化：清理事件监听器
 */
export function cleanup() {
  // 清理定时器
  const timers = window.setTimeout(() => {})
  for (let i = 1; i <= timers; i++) {
    clearTimeout(i)
  }

  // 清理动画
  if (window.gsap) {
    gsap.globalTimeline.clear()
  }
}

/**
 * 检测设备性能
 */
export function getDevicePerformance() {
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection

  const info = {
    isLowEndDevice: false,
    connectionType: connection?.effectiveType || 'unknown',
    saveData: connection?.saveData || false
  }

  // 根据设备内存判断
  if (navigator.deviceMemory && navigator.deviceMemory < 4) {
    info.isLowEndDevice = true
  }

  // 根据CPU核心数判断
  if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
    info.isLowEndDevice = true
  }

  return info
}

/**
 * 自适应质量调整
 */
export function adjustQualityBasedOnDevice() {
  const perf = getDevicePerformance()

  if (perf.isLowEndDevice || perf.saveData) {
    // 低端设备或节省数据模式
    document.body.classList.add('low-quality-mode')

    // 减少动画
    const style = document.createElement('style')
    style.textContent = `
      .low-quality-mode *,
      .low-quality-mode *::before,
      .low-quality-mode *::after {
        animation-duration: 0.1s !important;
        animation-delay: 0s !important;
        transition-duration: 0.1s !important;
        transition-delay: 0s !important;
      }
    `
    document.head.appendChild(style)
  }
}
