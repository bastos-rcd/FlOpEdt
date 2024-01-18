import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { UserAPI } from '@/ts/type'
import { User } from '@/stores/declarations'

export const useTutorStore = defineStore('tutor', () => {
  const tutors = ref<Array<User>>([])
  const isAllTutorsFetched = ref<boolean>(false)
  const getTutorById = computed(() => {
    return (tutorId: number) => {
      return tutors.value?.find((tutor) => tutor.id === tutorId)
    }
  })

  async function fetchTutors(tutorId?: number): Promise<void> {
    await api.getTutors(tutorId).then((result: UserAPI[]) => {
      result.forEach((user: UserAPI) => {
        const newTutor = {
          id: user.id,
          username: user.username,
          firstname: user.first_name,
          lastname: user.last_name,
          email: user.email,
          type: 'tutor',
          departments: new Map<number, boolean>(),
        }
        user.departments.forEach((dep) => {
          newTutor.departments.set(dep.department_id, dep.is_admin === 'true')
        })
        tutors.value.push(newTutor)
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
    clearTutors,
    getTutorById,
  }
})
