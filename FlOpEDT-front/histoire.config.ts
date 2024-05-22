import { defineConfig } from 'histoire'
import { HstVue } from '@histoire/plugin-vue'

export default defineConfig({
  setupFile: '/src/histoire.setup.ts',
  plugins: [HstVue()],

  // Make it a pure SPA without router
  // Allows it to be viewed from CI artifacts and other static places
  routerMode: 'hash',
  vite: {
    base: './',
    server: {
      host: '0.0.0.0',
      port: 6006,
    },
  },
})
