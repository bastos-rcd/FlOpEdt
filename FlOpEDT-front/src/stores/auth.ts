import { defineStore } from 'pinia'
import { User } from '@/ts/type'
import { computed, ref } from 'vue'
import { api } from '@/composables/api'

export const useAuth = defineStore('auth', () => {
  const user = ref(new User)

  const isUserAuthenticated = computed(() => user.value.id !== -1)

  function fetchAuthUser() : void {
    api?.getCurrentUser().then((json: any) => user.value = json)
  }

  const getUser = computed(() : User => {
    return user.value
  })

  function redirectLogin() : void {
    window.location.href = 'http://localhost:5173/fr/accounts/login/'
  }

  return { isUserAuthenticated, fetchAuthUser, getUser, redirectLogin }
})