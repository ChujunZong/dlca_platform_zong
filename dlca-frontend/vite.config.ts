import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',                 // 确保根路径
  server: {
    host: '0.0.0.0',         // 允许外部访问（关键）
    port: 5173,
    allowedHosts: true,      // 允许 ngrok 域名（关键）
    proxy: {
      '/api': {            
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})