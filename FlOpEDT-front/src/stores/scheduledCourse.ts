import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department, WeekDay } from '@/ts/type'


export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
    const scheduledCourses = ref<Array<ScheduledCourse>>([])
    const isAllScheduledFetched = ref<boolean>(false)
    const getScheduledCoursesFetched = computed(() => scheduledCourses.value)
    const getIsAllScheduledFetched = computed(() => isAllScheduledFetched.value)
    const getScheduledCoursesPerDepartment = computed((department : Department) => {
        if(isAllScheduledFetched.value)
            return scheduledCourses.value.filter(sc => sc.course.type.department.abbrev === department.abbrev)
        else
            return []
    })
    const getScheduledCoursesForDay = computed((weekday : WeekDay) => {
        if(isAllScheduledFetched) {
            return scheduledCourses.value.filter(sc => sc.day === weekday.ref)
        }
    } )

    async function fetchScheduledCourses(week : FlopWeek) : Promise<void> {
        await api.fetch
            .scheduledCourses({ week: week.week, year: week.year })
            .then((value: ScheduledCourse[]) => {
                scheduledCourses.value = value
            })
        isAllScheduledFetched.value = true
    }

    function clearScheduledCourses() : void {
        scheduledCourses.value = []
        isAllScheduledFetched.value = false

    }


    return { 
        getScheduledCoursesFetched,
        fetchScheduledCourses,
        getScheduledCoursesPerDepartment,
        getIsAllScheduledFetched,
        clearScheduledCourses,
        getScheduledCoursesForDay
    }
})