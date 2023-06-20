import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { Department, UserAPI } from '@/ts/type'
import { User } from '@/stores/declarations'

export const useTutorStore = defineStore('tutor', () => {
  const tutors = ref<Array<User>>([])
  const isAllTutorsFetched = ref<boolean>(false)
  const getTutorById = computed(() => {
    return (tutorId: number) => {
      return tutors.value?.find((tutor) => tutor.id === tutorId)
    }
  })

  async function fetchTutors(department?: Department): Promise<void> {
    await api.getTutors(department).then((result: UserAPI[]) => {
      result.forEach((user: UserAPI) => {
        tutors.value.push({
          id: user.id,
          username: user.name,
          firstname: '',
          lastname: '',
          email: '',
          type: 'tutor',
          departments: [],
        })
      })
      isAllTutorsFetched.value = true
    })
  }

  async function fetchTutorById(tutorId: number): Promise<void> {
    await api.getTutorById(tutorId).then((user: UserAPI) => {
      tutors.value.push({
        id: user.id,
        username: user.name,
        firstname: '',
        lastname: '',
        email: '',
        type: 'tutor',
        departments: [],
      })
      isAllTutorsFetched.value = true
    })
  }

  function clearTutors(): void {
    tutors.value = []
    isAllTutorsFetched.value = false
  }

  return {
    tutors,
    isAllTutorsFetched,
    fetchTutors,
    fetchTutorById,
    clearTutors,
    getTutorById,
  }
})
