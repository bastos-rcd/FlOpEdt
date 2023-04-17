import { useFetch } from "@/composables/api"
import { Week } from "@/models/Week"

const URL_GET_ALL =  "/fr/api/base/weeks"
/**
 * Load the weeks
 * @returns a map of Week where key are id
 */
export async function getAllWeek(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<Week> = []
        items.forEach((i:any) => {
            const curItem = Week.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}