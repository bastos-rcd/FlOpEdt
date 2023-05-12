import i18n from '@/i18n'
import { createPinia } from 'pinia'
import { defineSetupVue3 } from '@histoire/plugin-vue'
import QcalendarPlugin from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import '@quasar/quasar-ui-qcalendar/src/css/calendar-day.sass'
import { Quasar } from 'quasar'
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

export const setupVue3 = defineSetupVue3(({ app, story, variant }) => {
  const pinia = createPinia()
  app.use(pinia)
  app.use(QcalendarPlugin)
  app.use(i18n)
  app.use(Quasar, {
    plugins: {},
  })
})