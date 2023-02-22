<template>
    <BaseCalendar ref="calendar">
        <template #table>
            <table class="w-100">
                <tr>
                    <th class="col text-center border-dark border">Room</th>
                    <th v-for="day in props.values.days" :key="day.date" class="col text-center border-dark border">
                        {{ day.name }} {{ day.date }}
                    </th>
                </tr>
                <tr v-for="room in props.values.rooms" :key="room.id" class="border-dark border align-top h-100">
                    <td class="h-100">
                        <button
                            type="button"
                            class="btn btn-outline-dark h-100 w-100 align-middle rounded-0"
                            @click="$emit('rowHeaderClick', room.id)"
                        >
                            {{ room.name }}
                        </button>
                    </td>
                    <td
                        v-for="day in props.values.days"
                        :key="day.date"
                        class="border-dark border pb-3"
                        @click.self.left="createSlot(day.date, room.id)"
                    >
                        <div v-if="day.date in props.values.slots && room.id in props.values.slots[day.date]">
                            <component
                                :is="slot.component.value"
                                v-for="slot in props.values.slots[day.date][room.id]"
                                :key="slot.slotData.id"
                                :data="slot.slotData"
                                :actions="slot.actions"
                                class="col noselect slot m-0 border border-dark"
                                @click.right.prevent
                                @contextmenu="contextMenu(slot.slotData.id)"
                                @interface="storeSlotInterface"
                            >
                            </component>
                        </div>
                    </td>
                </tr>
            </table>
        </template>
    </BaseCalendar>
</template>

<script setup lang="ts">
import type { CalendarSlotInterface, RoomCalendarProps } from '@/assets/js/types'
import BaseCalendar from '@/components/BaseCalendar.vue'
import { ref } from 'vue'

interface Props {
    values: RoomCalendarProps
}

const props = defineProps<Props>()

interface Emits {
    (e: 'newSlot', day: Date, roomId: string): void

    (e: 'rowHeaderClick', id: number): void
}

const emit = defineEmits<Emits>()

function createSlot(day: string, roomId: string | number) {
    // Format the date as yyyy-MM-dd
    const dayArray = day.split('/')
    emit('newSlot', new Date(`${props.values.year}-${dayArray[1]}-${dayArray[0]}`), `${roomId}`)
}

const calendar = ref()

function contextMenu(id: string) {
    if (calendar.value) {
        calendar.value.openContextMenu(id)
    }
}

function storeSlotInterface(id: string, slotInterface: CalendarSlotInterface) {
    if (calendar.value) {
        calendar.value.storeSlotInterface(id, slotInterface)
    }
}
</script>

<script lang="ts">
export default {
    name: 'RoomCalendar',
    components: {},
}
</script>

<style scoped></style>
