import { useFetch } from "@/composables/api"
import { Room } from "@/models/Room"

const URL_GET_ALL = "/fr/api/rooms/room"
/**
 * Load the rooms
 * @returns a map of room where key are id
 */
export async function getAllRoom(){
    return useFetch(URL_GET_ALL,{})
    .then(items => {
        const res: Array<Room> = []
        items.forEach((i:any) => {
            const curItem = Room.unserialize(i)
            res.push(curItem)
        })
        return res
    })
}

