import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'node:path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy principal da API (Flask/FastAPI)
      '/api': {
        target: 'http://127.0.0.1:8000', // porta do backend local
        changeOrigin: true,
        secure: false,
        // 🔧 Adicione este rewrite para evitar duplicação de /api/v1
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },

      // Proxy para arquivos estáticos (thumbnails, imagens, etc.)
      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },

      // Proxy para WebSockets (streaming e alertas)
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },

  // Resolução de paths
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
