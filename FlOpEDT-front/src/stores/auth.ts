import { defineStore } from 'pinia'
import { User } from '@/ts/type'
import { computed, ref } from 'vue'
import { api } from '@/composables/api'

export const useAuth = defineStore('auth', () => {
  const user = ref(new User)

  const isUserAuthenticated = computed(() => user.value.id !== -1)

  function getAuthUser() {
    api?.getCurrentUser().then((json: any) => user.value = json)
  }

  function getUser() : User {
    return user.value
  }

  return { user, isUserAuthenticated, getAuthUser, getUser }
})