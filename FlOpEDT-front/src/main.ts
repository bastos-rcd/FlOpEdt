import { api } from '@/assets/js/api'
import { apiKey, currentWeekKey } from '@/assets/js/keys'
import type { FlopWeek } from '@/assets/js/types'
// Import Bootstrap CSS
import '@/assets/scss/styles.scss'
import CustomDatePicker from '@/components/DatePicker.vue'
import router from '@/router'
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import type { Ref } from 'vue'
import { createApp, readonly, ref } from 'vue'
import { useRoute } from 'vue-router'
import Popper from 'vue3-popper'
import App from './App.vue'

const app = createApp(App)

app.use(router)

// Provide the api access
app.provide(apiKey, readonly(api))

// Provide the current week and year
const now = new Date()
const startDate = new Date(now.getFullYear(), 0, 1)
const days = Math.floor(
    (now.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000)
)
const week = Math.ceil(days / 7)

const currentWeek: Ref<FlopWeek> = ref({
    week: week,
    year: now.getFullYear(),
})
app.provide(currentWeekKey, readonly(currentWeek.value))

export function getDepartment(): string | null {
    const dept = useRoute().params.dept
    if (dept instanceof Array) {
        if (dept.length === 0) {
            return null
        }
        return dept[0]
    }
    return dept
}

app.component('DatePicker', Datepicker)
    .component('CustomDatePicker', CustomDatePicker)
    .component('Popper', Popper)

app.mount('#app')
