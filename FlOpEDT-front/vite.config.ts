import vue from '@vitejs/plugin-vue'
import * as path from 'path'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
        },
    },
})
