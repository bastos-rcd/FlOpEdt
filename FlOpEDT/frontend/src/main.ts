import { api } from '@/assets/js/api'
import { apiKey, currentWeekKey } from '@/assets/js/keys'
import type { FlopWeek } from '@/assets/js/types'
// Import Bootstrap CSS
import '@/assets/scss/styles.scss'
import '@vuepic/vue-datepicker/dist/main.css'
import type { Ref } from 'vue'
import { createApp, readonly, ref } from 'vue'
import Popper from 'vue3-popper'

import RoomReservation from '@/views/RoomReservationView.vue'
import { createPinia } from 'pinia'

const roomreservation = createApp(RoomReservation).use(createPinia())

// Provide the current week and year
const now = new Date()
const startDate = new Date(now.getFullYear(), 0, 1)
const days = Math.floor((now.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))
const week = Math.ceil(days / 7)

const currentWeek: Ref<FlopWeek> = ref({
    week: week,
    year: now.getFullYear(),
})

const apps = [{ appName: 'roomreservation', app: roomreservation }]

const pinia = createPinia()

apps.forEach(({ appName, app }) => {
    // Provide the api access
    app.provide(apiKey, readonly(api))

    app.provide(currentWeekKey, readonly(currentWeek.value))

    app.use(pinia)

    app.component('PopperComponent', Popper)
    app.mount(`#${appName}-app`)
})
