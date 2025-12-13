import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // 本地开发默认使用 localhost，生产环境使用环境变量或远程服务器
  // 确保使用 HTTP 协议，不要使用 HTTPS
  let apiTarget = env.VITE_PROXY_TARGET || (mode === 'development' ? 'http://localhost:20000' : 'http://16.170.205.245:20000')
  
  // 强制使用 HTTP，移除任何 HTTPS
  if (apiTarget.startsWith('https://')) {
    apiTarget = apiTarget.replace('https://', 'http://')
    console.warn('警告: 代理目标已从 HTTPS 改为 HTTP，本地开发应使用 HTTP')
  }

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 30002,
      // 允许来自局域网的连接和域名
      allowedHosts: [
        '.lan',
        '.local',
        '.localnet',
        'kids.sql67.xyz',
        'sql67.xyz',
        'www.sql67.xyz'
      ],
      proxy: {
        // Forward API calls to backend to avoid mixed-content issues
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          // 确保使用 HTTP 协议
          ws: false
        }
      }
    }
  }
})
