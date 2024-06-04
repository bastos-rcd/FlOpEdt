import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

export const usePageStore = defineStore('page', () => {
  const { t } = useI18n()
  const name = ref(t('navbar.home'))

  return { name }
})
