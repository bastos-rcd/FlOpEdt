<template>
    <BaseCalendar ref="calendar">
        <template #table>
            <table class="w-100">
                <tr class="p-0 flex-nowrap">
                    <th class="p-0 me-3"></th>
                    <th
                        v-for="day in props.values.days"
                        :key="day.date"
                        class="col text-center border-dark border-bottom border-end border-top"
                        :class="{
                            'border-start border-dark': day === props.values.days[0],
                        }"
                    >
                        <div>{{ day.name }} {{ day.date }}</div>
                    </th>
                </tr>
                <tr class="flex-nowrap position-relative" :style="{ height: height }">
                    <td class="p-0 h-100" style="min-width: 50px; width: 50px">
                        <div
                            v-for="hour in hourIndicators"
                            :key="hour.value"
                            :style="computeHourStyle(hour)"
                            class="translate-middle-y"
                        >
                            <h6 class="text-wrap">{{ hour.text }}</h6>
                            <hr
                                class="border border-primary border-1 w-100 position-absolute top-0"
                                style="transform: translateY(-3px)"
                            />
                        </div>
                    </td>
                    <td
                        v-for="day in props.values.days"
                        :key="day.date"
                        class="col border-dark border-bottom border-end p-0"
                        :class="{
                            'border-start border-dark': day === props.values.days[0],
                        }"
                        :style="{ height: height }"
                        style="min-width: 65px"
                    >
                        <div
                            class="position-relative h-100"
                            @mousedown.left.self="dayColumnMouseDown(day.date, $event)"
                            @mouseup.left.self="dayColumnMouseUp(day.date, $event)"
                        >
                            <component
                                :is="slot.component.value"
                                v-for="slot in displayableSlots[day.date]"
                                :key="slot.slotData.id"
                                :data="slot.slotData"
                                :actions="slot.actions"
                                :style="computeStyle(slot.slotData)"
                                class="noselect slot m-0 border border-dark"
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
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
import type {
    CalendarDragEvent,
    CalendarSlot,
    CalendarSlotData,
    CalendarSlotInterface,
    HourCalendarProps,
    Time,
} from '@/assets/js/types'
import type { StyleValue, VueElementConstructor } from 'vue'
import { computed, defineProps, ref } from 'vue'
import BaseCalendar from '@/components/calendar/BaseCalendar.vue'

interface Emits {
    (e: 'drag', event: CalendarDragEvent): void
}

const emit = defineEmits<Emits>()

interface Props {
    values: HourCalendarProps
}

const props = defineProps<Props>()

/**
 * Value used to fit drag&drop slot creation when pressing the button, in minutes.
 * Should be set among [15, 30, 60]
 * @type {number}
 */
const snapValueStart = 15

/**
 * Value used to fit drag&drop slot creation when releasing the button, in minutes.
 * Should be set among [15, 30, 60]
 * @type {number}
 */
const snapStep = 30

const displayableSlots = computed(() => {
    const out: { [index: string]: Array<CalendarSlot> } = {}
    Object.keys(props.values.slots).forEach((index) => {
        if (!(index in out)) {
            out[index] = []
        }
        out[index] = props.values.slots[index].filter((tmpSlot) => canBeDisplayed(tmpSlot.slotData))
    })
    return out
})

const hourIndicators = computed(() => {
    const start = Math.trunc(props.values.startTime / 60)
    const end = Math.trunc(props.values.endTime / 60)
    const hours = []
    for (let hour = start; hour <= end; ++hour) {
        const time: Time = {
            value: hour * 60,
            text: convertDecimalTimeToHuman(hour),
        }
        hours.push(time)
    }
    return hours
})

const dragEvent: CalendarDragEvent = {
    startDate: new Date(),
    startTime: { text: '', value: 0 },
    endDate: new Date(),
    endTime: { text: '', value: 0 },
}

/**
 * Takes a click position in the Y-axis relative to the concerned column.
 * Returns the time in minutes from midnight corresponding to this position and taking the starting time offset into account.
 * @param {number} y The position in the Y-axis.
 * @param snap
 * @returns {number} The value of the time.
 */
function clickHeightToTime(y: number, snap: number): number {
    return Math.round((props.values.startTime + (y / pixelsPerHour) * 60) / snap) * snap
}

function dayColumnMouseDown(day: string, event: MouseEvent): void {
    const dayArray = day.split('/')
    dragEvent.startDate = new Date(`${props.values.year}-${dayArray[1]}-${dayArray[0]}`)
    const time = clickHeightToTime(event.offsetY, snapValueStart)
    dragEvent.startTime = {
        text: convertDecimalTimeToHuman(time / 60),
        value: time,
    }
}

function dayColumnMouseUp(day: string, event: MouseEvent): void {
    const dayArray = day.split('/')
    dragEvent.endDate = new Date(`${props.values.year}-${dayArray[1]}-${dayArray[0]}`)
    const startTime = dragEvent.startTime.value
    let time = clickHeightToTime(event.offsetY, snapStep)
    if (time - startTime < 5) {
        time = startTime + 60
    }
    time = startTime + Math.round((time - startTime) / snapStep) * snapStep
    dragEvent.endTime = {
        text: convertDecimalTimeToHuman(time / 60),
        value: time,
    }
    emit('drag', dragEvent)
}

// Positioning and sizing

const pixelsPerHour = 50
const heightValue = computed(() => {
    return pixelsPerHour * (Math.trunc(props.values.endTime / 60) - Math.trunc(props.values.startTime / 60))
})

const height = computed(() => {
    return `${heightValue.value}px`
})

function positionRelativeToColumn(value: number): number {
    return (100 * (value - props.values.startTime)) / (props.values.endTime - props.values.startTime)
}

function computeHeight(slot: CalendarSlotData): string {
    const startPos = positionRelativeToColumn(slot.startTime.value)
    const endPos = positionRelativeToColumn(slot.endTime.value)

    const out = endPos - startPos
    return `${out}%`
}

function computeYOffset(time: number): string {
    const out = positionRelativeToColumn(time)
    return `${out}%`
}

function canBeDisplayed(slot: CalendarSlotData): boolean {
    const out = slot.startTime.value >= props.values.startTime
    if (!out) {
        console.log(`Slot ${slot.title} cannot be displayed because it does not begin after day start time`)
    }
    return out
}

function computeStyle(slot: CalendarSlotData): StyleValue {
    const top = computeYOffset(slot.startTime.value)
    const height = computeHeight(slot)
    return {
        height: height,
        top: top,
        position: 'absolute',
        'text-align': 'center',
    }
}

function computeHourStyle(hour: Time): StyleValue {
    const top = computeYOffset(hour.value)
    return {
        top: top,
        position: 'absolute',
        width: '100%',
    }
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
    name: 'HourCalendar',
    components: {},
}
</script>

<style>
.slot > div {
    height: 100%;
}
</style>
