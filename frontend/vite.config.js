import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_PROXY_TARGET || 'http://16.170.205.245:20000'

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
          secure: false
        }
      }
    }
  }
})
