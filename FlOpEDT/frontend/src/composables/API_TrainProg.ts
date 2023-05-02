import { useFetch } from "@/composables/api"
import { TrainProg } from "@/models/TrainProg"

const URL_GET_ALL = "/fr/api/fetch/idtrainprog"
/**
 * Load the train programms
 * @returns a map of TrainProg where key are id
 */
export async function getAllTrainProg(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<TrainProg> = []
        items.forEach((i:any) => {
            const curItem = TrainProg.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}

