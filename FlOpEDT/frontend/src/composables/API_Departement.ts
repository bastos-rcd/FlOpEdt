import { useFetch } from "@/composables/api"
import { Department } from "@/models/Department"

const URL_GET_ALL =  "/fr/api/fetch/alldepts"
/**
 * Load the departments
 * @returns a map of Department where key are id
 */
export async function getAllDepartement(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<Department> = []
        items.forEach((i:any) => {
            const curItem = Department.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}