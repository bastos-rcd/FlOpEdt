<template>
    <ModalForm
        :is-open="props.isOpen"
        :is-locked="isFormLocked"
        :on-cancel="onFormCancel"
        :on-save="onFormSave"
        @interface="onFormInterface"
        class="text-start"
    >
        <template #title>Room reservation</template>
        <template #body>
            <!-- Title -->
            <div class="form-floating mb-3">
                <input
                    :id="generateId('title')"
                    type="text"
                    class="form-control"
                    placeholder="Title"
                    maxlength="30"
                    v-model="title"
                />
                <label :for="generateId('title')" class="form-label">Title</label>
            </div>
            <!-- Description -->
            <div class="form-floating mb-3">
                <textarea
                    :id="generateId('description')"
                    type="text"
                    class="form-control"
                    placeholder="Description"
                    rows="2"
                    v-model="description"
                ></textarea>
                <label :for="generateId('description')" class="form-label">Description</label>
            </div>
            <!-- Room -->
            <div class="form-floating mb-3">
                <select class="form-select" :id="generateId('room')" v-model="selectedRoom">
                    <option value="-1" disabled>Select a room</option>
                    <option v-for="room in props.rooms" :key="room.id" :value="room.id">
                        {{ room.name }}
                    </option>
                </select>
                <label :for="generateId('room')" class="form-label">Room</label>
            </div>
            <!-- Date -->
            <div class="mb-3">
                <DayPicker
                    :start-date="date"
                    :should-reset="shouldDayPickerReset"
                    :on-reset="(shouldDayPickerReset = false)"
                    @update:date="updateDate"
                    :min-date="new Date()"
                    :clearable="false"
                >
                    <template #input="{ value }">
                        <div class="form-floating">
                            <input
                                :id="generateId('date')"
                                type="text"
                                class="form-control"
                                placeholder="Date"
                                :value="value"
                            />
                            <label :for="generateId('date')" class="form-label">Date</label>
                        </div>
                    </template>
                </DayPicker>
            </div>
            <div class="row m-0">
                <div class="col p-0 me-1" style="min-width: 100px">
                    <!-- Start time -->
                    <TimePicker
                        :hours="startTime.hours"
                        :minutes="startTime.minutes"
                        @update-time="updateStartTime"
                        :should-reset="shouldStartTimePickerReset"
                        @on-reset="shouldStartTimePickerReset = false"
                    >
                        <template #input="{ value }">
                            <div class="form-floating mb-3">
                                <input
                                    :id="generateId('startTime')"
                                    type="text"
                                    class="form-control"
                                    placeholder="Start time"
                                    :value="value"
                                    readonly
                                />
                                <label :for="generateId('startTime')" class="form-label">Start time</label>
                            </div>
                        </template>
                    </TimePicker>
                </div>
                <div class="col p-0" style="min-width: 100px">
                    <!-- End time -->
                    <TimePicker
                        :hours="endTime.hours"
                        :minutes="endTime.minutes"
                        @update-time="updateEndTime"
                        :should-reset="shouldEndTimePickerReset"
                        @on-reset="shouldEndTimePickerReset = false"
                    >
                        <template #input="{ value }">
                            <div class="form-floating mb-3">
                                <input
                                    :id="generateId('endTime')"
                                    type="text"
                                    class="form-control"
                                    placeholder="End time"
                                    :value="value"
                                    readonly
                                />
                                <label :for="generateId('endTime')" class="form-label">End time</label>
                            </div>
                        </template>
                    </TimePicker>
                </div>
            </div>
            <!-- Responsible -->
            <div class="form-floating mb-3">
                <input
                    :id="generateId('responsible')"
                    type="text"
                    class="form-control"
                    placeholder="Responsible"
                    :value="reservationResponsibleUsername"
                    disabled
                />
                <label :for="generateId('responsible')" class="form-label">Responsible</label>
            </div>
            <!-- Type -->
            <div class="form-floating mb-3">
                <select class="form-select" :id="generateId('reservationType')" v-model="selectedType">
                    <option :value="-1" disabled>Select a reservation type</option>
                    <option v-for="type in props.reservationTypes" :key="type.id" :value="type.id">
                        {{ type.name }}
                    </option>
                </select>
                <label :for="generateId('reservationType')" class="form-label">Reservation type</label>
            </div>
            <!-- Send email -->
            <div class="form-check form-switch">
                <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="email"
                    role="switch"
                    :id="generateId('email')"
                />
                <label class="form-check-label" :for="generateId('email')">Send a confirm email?</label>
            </div>
        </template>
    </ModalForm>
</template>

<script setup lang="ts">
import { parseReason } from '@/assets/js/helpers'
import { apiKey, apiToken, requireInjection } from '@/assets/js/keys'
import type { FormInterface, Room, RoomReservation, RoomReservationType, User } from '@/assets/js/types'
import DayPicker from '@/components/DayPicker.vue'
import ModalForm from '@/components/ModalForm.vue'
import TimePicker from '@/components/TimePicker.vue'
import { computed, defineProps, ref } from 'vue'

interface Emits {
    (e: 'saved', reservation: RoomReservation): void

    (e: 'closed'): void

    (e: 'cancelled'): void
}

const emit = defineEmits<Emits>()

interface Props {
    reservation: RoomReservation
    isOpen: boolean
    isNew: boolean
    rooms: { [roomId: number]: Room }
    reservationTypes: Array<RoomReservationType>
    users: { [userId: number]: User }
}

const props = defineProps<Props>()

const api = requireInjection(apiKey)
const authToken = requireInjection(apiToken)

class ReservationTime {
    hours = 0
    minutes = 0

    static toString = (time: ReservationTime): string => {
        return `${time.hours}:${time.minutes}:00`
    }

    public static fromString(time: string): ReservationTime {
        const array = time.split(':')
        const out = new ReservationTime()
        out.hours = parseInt(array[0])
        out.minutes = parseInt(array[1])
        return out
    }
}

const shouldDayPickerReset = ref(false)
const shouldStartTimePickerReset = ref(false)
const shouldEndTimePickerReset = ref(false)

const reservationResponsibleUsername = computed(() => {
    const user = props.users[props.reservation.responsible]
    return user ? `${user.first_name} ${user.last_name} (${user.username})` : 'Unknown'
})

const formInterface = ref<FormInterface>()
const isFormLocked = ref(false)

const title = ref(props.reservation.title)
const description = ref(props.reservation.description)
const selectedResponsible = ref(props.reservation.responsible)
const selectedRoom = ref(props.reservation.room)
const selectedType = ref(props.reservation.reservation_type)
const email = ref(props.reservation.email)
const startTime = ref(ReservationTime.fromString(props.reservation.start_time))
const endTime = ref(ReservationTime.fromString(props.reservation.end_time))
const date = ref(props.reservation.date)

function resetValues() {
    title.value = props.reservation.title
    description.value = props.reservation.description
    selectedResponsible.value = props.reservation.responsible
    selectedRoom.value = props.reservation.room
    selectedType.value = props.reservation.reservation_type
    email.value = props.reservation.email
    startTime.value = ReservationTime.fromString(props.reservation.start_time)
    endTime.value = ReservationTime.fromString(props.reservation.end_time)
    date.value = props.reservation.date

    shouldDayPickerReset.value = true
    shouldStartTimePickerReset.value = true
    shouldEndTimePickerReset.value = true
}

function onFormCancel() {
    resetValues()
    cancel()
}

function onFormSave() {
    isFormLocked.value = true
    const obj: RoomReservation = {
        date: date.value.replaceAll('/', '-'),
        description: description.value,
        email: email.value,
        end_time: ReservationTime.toString(endTime.value),
        id: Math.max(0, props.reservation.id),
        periodicity: 1,
        responsible: selectedResponsible.value,
        room: selectedRoom.value,
        start_time: ReservationTime.toString(startTime.value),
        title: title.value,
        reservation_type: selectedType.value,
    }
    const method = props.isNew ? api.post : api.put
    method
        .roomReservation(obj, authToken)
        .then(
            (value) => {
                obj.id = value.id
                emit('saved', obj)
                close()
            },
            (reason) => handleReason(reason)
        )
        .catch((reason) => handleReason(reason))
}

function handleReason(reason: unknown) {
    formInterface.value?.dismissAlerts()
    parseReason(reason, formInterface.value?.addAlert)
    isFormLocked.value = false
}

function onFormInterface(value: FormInterface) {
    formInterface.value = value
}

function updateDate(newDate: string) {
    date.value = newDate
}

function updateStartTime(time: { hours: number; minutes: number }) {
    startTime.value = time
}

function updateEndTime(time: { hours: number; minutes: number }) {
    endTime.value = time
}

function generateId(element: string) {
    return `edit-room-reservation-${element}-${props.reservation.id}`
}

function close() {
    isFormLocked.value = false
    formInterface.value?.close()
    emit('closed')
}

function cancel() {
    formInterface.value?.close()
    emit('cancelled')
}
</script>

<script lang="ts">
export default {
    name: 'RoomReservationForm',
    components: {},
}
</script>

<style scoped></style>
