import { createApp, readonly, ref, Ref } from 'vue'

import { createPinia } from 'pinia'

import '@/assets/scss/styles.scss'
import './style.css'

import App from './App.vue'
import '@vuepic/vue-datepicker/dist/main.css'

import router from '@/router'
import { FlopWeek } from '@/ts/type'
import Popper from 'vue3-popper'


import { createI18n } from 'vue-i18n'
import fr from '@/locales/fr.json'
import en from '@/locales/en.json'

const app = createApp(App)
const i18n = createI18n({
    legacy: false,
    locale: 'fr',
    fallbackLocale: 'en',
    messages: {fr, en}
})
// Provide the current week and year
const now = new Date()
const startDate = new Date(now.getFullYear(), 0, 1)
const days = Math.floor((now.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))
const week = Math.ceil(days / 7)

const currentWeek: Ref<FlopWeek> = ref({
    week: week,
    year: now.getFullYear(),
})

app.provide('currentWeek', readonly(currentWeek.value))
app.component('PopperComponent', Popper)
app.use(router).use(createPinia()).use(i18n).mount('#app')

