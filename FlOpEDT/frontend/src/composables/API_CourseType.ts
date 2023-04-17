import { useFetch } from "@/composables/api"
import { CourseType } from "@/models/CourseType"

const URL_GET_ALL = "/fr/api/fetch/idcoursetype"
/**
 * Load the course types
 * 
 * @returns a map of CourseType where key are id
 */
export async function getAllCourseType(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<CourseType> = []
        items.forEach((i:any) => {
            const curItem = CourseType.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}