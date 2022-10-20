<template>
    <PopperComponent
        :id="props.data.id"
        class="frame"
        :show="isContextMenuOpened"
        :style="props.data.displayStyle"
        arrow
        @click.left="onClick"
    >
        <div>
            <RoomReservationForm
                :reservation="props.data.reservation"
                :is-open="isEditing"
                :is-new="props.data.reservation.id < 0"
                :rooms="props.data.rooms"
                :reservation-types="props.data.reservationTypes"
                :users="props.data.users"
                @closed="closeEdit"
                @saved="onSave"
                @cancelled="onCancel"
            ></RoomReservationForm>
            <div class="row m-0 h-100">
                <slot name="text"></slot>
            </div>
        </div>
        <template #content>
            <slot name="contextmenu">
                <CalendarSlotContextMenu
                    :data="props.data"
                    :on-delete="onDelete"
                    :on-edit="onDoubleClick"
                    :on-duplicate="onDuplicate"
                ></CalendarSlotContextMenu>
            </slot>
        </template>
    </PopperComponent>
</template>

<script setup lang="ts">
import type {
    CalendarRoomReservationSlotData,
    CalendarSlotActions,
    CalendarSlotInterface,
    RoomReservation,
} from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import RoomReservationForm from '@/components/RoomReservationForm.vue'
import { onMounted, ref } from 'vue'

interface Props {
    data: CalendarRoomReservationSlotData
    actions: CalendarSlotActions
}

const props = defineProps<Props>()

interface Emits {
    (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)
const clickCount = ref(0)
const timer = ref()
const isEditing = ref(false)

function onClick() {
    if (++clickCount.value == 1) {
        timer.value = setTimeout(() => {
            clickCount.value = 0
            onSingleClick()
        }, 300)
        return
    }
    clearTimeout(timer.value)
    clickCount.value = 0
    onDoubleClick()
}

function onSingleClick() {
    if (isEditing.value) {
        // Ignore click when form is open
        return
    }
    console.log(`Click on ${props.data.title}`)
}

function onDoubleClick() {
    if (isEditing.value) {
        // Ignore click when form is open
        return
    }
    openEdit()
}

function onSave(reservation: RoomReservation) {
    const slot = Object.assign({}, props.data)
    slot.reservation = reservation
    props.actions.save?.(slot, props.data)
}

function onDelete() {
    props.actions.delete?.(props.data)
}

function onDuplicate() {
    // TODO: Duplicate reservation and open edit form
    console.log('On duplicate')
}

function onCancel() {
    closeEdit()
    if (props.data.reservation.id < 0) {
        onDelete()
    }
}

function openContextMenu(): boolean {
    isContextMenuOpened.value = true
    return isContextMenuOpened.value
}

function closeContextMenu() {
    isContextMenuOpened.value = false
}

function openEdit() {
    isEditing.value = true
}

function closeEdit() {
    isEditing.value = false
}

function emitInterface() {
    emit('interface', props.data.id, {
        openContextMenu: openContextMenu,
        closeContextMenu: closeContextMenu,
    })
}

onMounted(() => {
    emitInterface()
    // Open the form if the slot has just been created
    if (props.data.reservation.id < 0) {
        isEditing.value = true
    }
})
</script>

<script lang="ts">
export default {
    name: 'CalendarRoomReservationSlot',
    components: {},
}
</script>

<style scoped>
.frame {
    border-radius: 5px;
    width: 100%;
}

:slotted(p) {
    font-size: 0.75em;
    font-weight: bold;
    margin: 0;
    padding: 0 5px 0 5px;
}
</style>
