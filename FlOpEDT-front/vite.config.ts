import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import * as path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
                '@': path.resolve(__dirname, 'src'),
                '~bootstrap': path.resolve(__dirname, 'node_modules/bootstrap'),
        },
    },
    server: {
        proxy: {
            '/fr': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                /*
                configure: (proxy, _options) => {
                    proxy.on('error', (err, _req, _res) => {
                    console.log('proxy error', err)
                    })
                    proxy.on('proxyReq', (proxyReq, req, _res) => {
                        console.log('Sending Request to the Target:', req.method, req.url)
                        proxyReq.getHeaderNames().forEach((hn) => {
                            console.log(`Header ${hn} of the request: `, proxyReq.getHeader(hn))
                        })
                    })
                    proxy.on('proxyRes', (proxyRes, req, _res) => {
                        console.log('Received Response from the Target:', proxyRes.statusCode, req.url)
                    })
                }
                */
            },
            '/en': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
            '/static': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
})
