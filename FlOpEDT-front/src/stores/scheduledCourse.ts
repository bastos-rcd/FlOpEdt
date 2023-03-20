import { api } from '@/composables/api'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ScheduledCourse, FlopWeek, Department, WeekDay } from '@/ts/type'


export const useScheduledCourseStore = defineStore('scheduledCourse', () => {
    const scheduledCourses = ref<Array<ScheduledCourse>>([])
    const isAllScheduledFetched = ref<boolean>(false)
    const getScheduledCoursesFetched = computed(() => scheduledCourses.value)
    const getIsAllScheduledFetched = computed(() => isAllScheduledFetched.value)

    async function fetchScheduledCourses(week : FlopWeek) : Promise<void> {
        await api.fetch
            .scheduledCourses({ week: week.week, year: week.year })
            .then((value: ScheduledCourse[]) => {
                scheduledCourses.value = value
                scheduledCourses.value.forEach(sc => {
                    sc.start_time = new Date(sc.start_time)
                    sc.end_time = new Date(sc.end_time)
                })
            })
        isAllScheduledFetched.value = true
    }

    function clearScheduledCourses() : void {
        scheduledCourses.value = []
        isAllScheduledFetched.value = false
    }
    function getScheduledCoursesPerDepartment(department : Department) : Array<ScheduledCourse> {
        if(isAllScheduledFetched.value)
            return scheduledCourses.value.filter(sc => sc.course.type.department.abbrev === department.abbrev)
        else
            return []
    }

    function getScheduledCoursesForDay(weekday : WeekDay) : Array<ScheduledCourse> {
        if(isAllScheduledFetched) {
            return scheduledCourses.value.filter(sc => sc.start_time.getDay() === weekday.num)
        }
        else
            return []
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