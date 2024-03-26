import i18n from '@/i18n'
import { createPinia } from 'pinia'
import { defineSetupVue3 } from '@histoire/plugin-vue'
import Plugin from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'
import '@quasar/quasar-ui-qcalendar/src/css/calendar-day.sass'

export const setupVue3 = defineSetupVue3(({ app }) => {
  const pinia = createPinia()
  app.use(pinia)
  // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
  app.use(Plugin)
  app.use(i18n)
})
