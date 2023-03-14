import { Department, ScheduledCourse } from "@/ts/type"
import { ComputedRef, Ref } from "vue"

export interface ScheduledCourses {
    list: ComputedRef<Array<ScheduledCourse>>
    perDepartment: Ref<{ [departmentId: string]: Array<ScheduledCourse> }>
    perDepartmentFilterByDepartmentsAndRooms: ComputedRef<{ [departmentId: string]: Array<ScheduledCourse> }>
    perDay: ComputedRef<{ [day: string]: Array<ScheduledCourse> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{
        [day: string]: { [roomId: string]: Array<ScheduledCourse> }
    }>
    perDayPerRoom: ComputedRef<{
        [day: string]: { [roomId: string]: Array<ScheduledCourse> }
    }>
}

/**
 * Takes an object having departments id as key and an array.
 * Returns the filtered entries of selected departments.
 * @param object
 */
export function filterBySelectedDepartments<T>(object: { [key: string]: Array<T> }, selectedDepartments: Array<Department>) {
    const out: { [departmentId: string]: Array<T> } = Object.fromEntries(
        Object.entries(object).filter(
            ([key]) => selectedDepartments.findIndex((dept) => `${dept.id}` === key) >= 0
        )
    )
    return out
}