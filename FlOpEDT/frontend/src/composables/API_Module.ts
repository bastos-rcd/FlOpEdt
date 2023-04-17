import { useFetch } from "@/composables/api"
import { Module } from "@/models/Module"

const URL_GET_ALL = "/fr/api/fetch/idmodule"
/**
 * Load the modules
 * @returns a map of modules where key are id
 */
export async function getAllModule(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<Module> = []
        items.forEach((i:any) => {
            const curItem = Module.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}