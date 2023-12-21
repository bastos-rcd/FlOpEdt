import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import * as path from 'path'
import { quasar, transformAssetUrls } from '@quasar/vite-plugin'

const FLOP_BACKEND_URL = process.env.FLOP_BACKEND_URL || 'http://127.0.0.1:8000'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue({ template: { transformAssetUrls } }), quasar({ sassVariables: 'src/quasar-variables.sass' })],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
    },
  },
  server: {
    proxy: {
      '/fr': {
        target: FLOP_BACKEND_URL,
        changeOrigin: true,
      },
      '/en': {
        target: FLOP_BACKEND_URL,
        changeOrigin: true,
      },
      '/es': {
        target: FLOP_BACKEND_URL,
        changeOrigin: true,
      },
      '/static': {
        target: FLOP_BACKEND_URL,
        changeOrigin: true,
      },
      '/api': {
        target: FLOP_BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
})
