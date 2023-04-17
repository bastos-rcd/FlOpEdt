import { api } from '@/assets/js/api'
import { apiKey, currentWeekKey } from '@/assets/js/keys'
import type { FlopWeek } from '@/assets/js/types'
// Import Bootstrap CSS
import '@/assets/scss/styles.scss'
import '@vuepic/vue-datepicker/dist/main.css'
import type { Ref } from 'vue'
import { createApp, readonly, ref } from 'vue'
import Popper from 'vue3-popper'
import { VueShowdown } from 'vue-showdown'

import RoomReservation from '@/views/RoomReservationView.vue'
import ConstraintManager from '@/views/ConstraintManager.vue'

import { createPinia } from 'pinia'

const roomreservation = createApp(RoomReservation).use(createPinia())
const constraintmanager = createApp(ConstraintManager).use(createPinia())

// Provide the current week and year
const now = new Date()
const startDate = new Date(now.getFullYear(), 0, 1)
const days = Math.floor((now.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))
const week = Math.ceil(days / 7)

const currentWeek: Ref<FlopWeek> = ref({
    week: week,
    year: now.getFullYear(),
})

//Find the user language
const currentUrl = window.location.pathname;
const regex = new RegExp('(/(?<lang>.*?)/).*')
const lang = currentUrl.match(regex)?.groups?.lang


const roomreservationImports=[{nameOfImport:'PopperComponent',valueOfImport:Popper}] 
const constraintmanagerImports=[{nameOfImport:'VueShowdown',valueOfImport:VueShowdown}] 

const apps = [
    { appName: 'roomreservation', app: roomreservation, importedComponents:roomreservationImports }, //importedComponent:Array('NomImport',NomComposant) et itérer dessus pour importer les trucs dans la bonnen app
    { appName: 'constraintmanager', app: constraintmanager,importedComponents:constraintmanagerImports },
]

const pinia = createPinia()

apps.forEach(({ appName, app, importedComponents }) => { //faire un if pour app.component() dans la bonne app
    // Provide the api access
    app.provide(apiKey, readonly(api))
    app.provide(currentWeekKey, readonly(currentWeek.value))
    app.provide('lang',lang)

    app.use(pinia)

    importedComponents.forEach(item=>{
        app.component(item.nameOfImport,item.valueOfImport)
    })
    app.mount(`#${appName}-app`)
})
