import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { StoreAction } from '@/stores/store'
import type { Department, Room, RoomAPI } from '@/ts/type'
import { useDepartmentStore } from '@/stores/department'
import { mapListId } from '@/helpers'


export const useRoomStore = defineStore('room', () => {
    const r = ref<Array<Room>>([])

    // Read-only value of the list of departments
    const rooms = computed<Array<Room>>(() => r.value)
    // Generate the default API functions

    const remote: StoreAction<Room, RoomAPI> = new StoreAction<Room, RoomAPI>(
        'rooms/room',
        convertToApp,
        convertToAPI,
        (value: Room[]) => (r.value = value)
    )

    const perId = computed(() => {
        return Object.fromEntries(r.value.map((r) => [r.id, r]))
    })

    const perDepartment = computed(() => {
        const departmentStore = useDepartmentStore()

        const out: {
            [deptId: string]: Array<Room>
        } = {}
        departmentStore.getAllDepartmentsFetched.forEach((dept : Department) => {
            out[dept.id] = r.value.filter((room) => room.departments.findIndex((d : Department) => d.id === dept.id) >= 0)
        })
        return out
    })

    function convertToApp(room: Partial<RoomAPI>): Room {
        const departmentStore = useDepartmentStore()
        const roomStore = useRoomStore()

        return {
            id: room.id ?? -1,
            departments: room.departments
                ? departmentStore.getAllDepartmentsFetched.filter((dept : Department) => room.departments?.includes(dept.id))
                : [],
            basic_rooms: room.basic_rooms ?? [],
            is_basic: room.is_basic ?? true,
            name: room.name ?? 'Unknown',
            subroom_of: roomStore.rooms.filter((r) => room.id === r.id),
        }
    }

    function convertToAPI(room: Partial<Room>): RoomAPI {
        return {
            id: room.id ?? -1,
            departments: room.departments ? mapListId(room.departments) : [],
            basic_rooms: room.basic_rooms ?? [],
            is_basic: room.is_basic ?? true,
            name: room.name ?? 'Unknown',
            subroom_of: room.subroom_of ? mapListId(room.subroom_of) : [],
        }
    }

    return { rooms, remote, perId, perDepartment }
})
