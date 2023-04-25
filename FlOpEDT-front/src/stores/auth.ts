import { defineStore } from 'pinia'
import { User } from '@/ts/type'
import { computed, ref } from 'vue'
import { api } from '@/utils/api'

export const useAuth = defineStore('auth', () => {
  const user = ref(new User)
  const fetchTried = ref(false)

  const isUserAuthenticated = computed(() => user.value.id !== -1)

  const isUserFetchTried = computed(() => fetchTried.value)

  async function fetchAuthUser() : Promise<void> {
    await api?.getCurrentUser().then((json: any) => user.value = json)
    fetchTried.value = true
  }

  const getUser = computed(() : User => {
    return user.value
  })

  function redirectLogin() : void {
    window.location.href = '/fr/accounts/login/'
  }

  return { isUserAuthenticated, fetchAuthUser, getUser, redirectLogin, isUserFetchTried }
})
