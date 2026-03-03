import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import history from 'connect-history-api-fallback'

// Custom plugin to handle history API fallback
const historyApiFallback = () => ({
  name: 'history-api-fallback',
  configureServer(server) {
    server.middlewares.use(history())
  },
})

export default defineConfig({
  plugins: [react(), historyApiFallback()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    port: 3000,
    // Fix for React dev server CSP issues
    // Disable the default eval-based source maps that trigger CSP violations
    // This allows 'eval' in dev mode
    hmr: {
      overlay: true,
    },
    // Proxy all /api requests to backend
    proxy: {
      // Proxy API requests to FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Proxy health checks
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Build configuration for production
  build: {
    // Generate source maps for debugging (can be disabled in production)
    sourcemap: false,
  },
  // Optimize deps
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
})
