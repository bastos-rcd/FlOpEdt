import { api } from '@/utils/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { UserAPI } from '@/ts/type'
import { User } from '@/stores/declarations'

export const useTutorStore = defineStore('tutor', () => {
  const tutors = ref<Array<User>>([])
  const isAllTutorsFetched = ref<boolean>(false)
  const getTutorById = computed(() => {
    return async (tutorId: number) => {
      let tutor = tutors.value?.find((tutor) => tutor.id === tutorId)
      if (!tutor && tutorId !== null) {
        await api.getTutors(tutorId).then((result: UserAPI[]) => {
          if (result.length === 1) {
            tutor = {
              id: result[0].id,
              username: result[0].username,
              firstname: result[0].first_name,
              lastname: result[0].last_name,
              email: result[0].email,
              type: 'tutor',
              departments: new Map<number, boolean>(),
            }
            result[0].departments.forEach((dep) => {
              tutor?.departments.set(dep.department_id, dep.is_admin === 'true')
            })
          }
        })
      }
      return tutor
    }
  })

  async function fetchTutors(tutorId?: number): Promise<void> {
    if (!isAllTutorsFetched.value) {
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
