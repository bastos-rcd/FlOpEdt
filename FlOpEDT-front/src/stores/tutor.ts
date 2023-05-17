import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { User, Department } from '@/ts/type'


export const useTutorStore = defineStore('tutor', () => {
    const tutors = ref<Array<User>>([])
    const isAllTutorsFetched = ref<boolean>(false)
    const getTutorById = computed(() => {
        return (tutorId: number) => {
            return tutors.value?.find(tutor => tutor.id === tutorId)
        }
    })

    const getAllTutorsById = computed(() => {
        return Object.fromEntries(tutors.value.map((tutor : User) => [tutor.id, tutor]))
    })

    async function fetchTutors(department? : Department) : Promise<void> {
        await api.getTutors(department)
            .then((value: User[]) => {
                tutors.value = value
                isAllTutorsFetched.value = true
            })
    }

    async function fetchTutorById(tutorId:number) {
        await api.getTutorById(tutorId)
            .then((value: User) => {
                tutors.value.push(value)
                isAllTutorsFetched.value = true
            })
    }

    function clearTutors() : void {
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
        getAllTutorsById
    }
})