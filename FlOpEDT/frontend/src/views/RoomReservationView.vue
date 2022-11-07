<template>
    <div>
        <div class="loader" v-if="loaderIsVisible"></div>
        <DeletePeriodicReservationDialog
            :is-open="isReservationDeletionDialogOpen"
            :reservation="reservationToDelete"
            :on-confirm-current="reservationDeletionConfirmed"
            :on-confirm-all="reservationRemoveAllSamePeriodicity"
            :on-confirm-future="reservationRemoveCurrentAndFutureSamePeriodicity"
            :on-cancel="closeReservationDeletionDialog"
        ></DeletePeriodicReservationDialog>
        <div class="container-fluid">
            <div class="row">
                <!-- Week picker and filters -->
                <div class="col-6 col-md-5 col-lg-4 col-xl-3">
                    <WeekPicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></WeekPicker>
                    <div class="row">
                        <!-- Filters -->
                        <div class="col">
                            <!-- Room filter -->
                            <div class="row mb-3">
                                <label for="select-room" class="form-label">Room:</label>
                                <div v-if="selectedRoom" class="col-auto pe-0">
                                    <button type="button" class="btn-close" @click="handleRoomNameClick(-1)"></button>
                                </div>

                                <div class="col-auto">
                                    <select
                                        id="select-room"
                                        v-model="selectedRoom"
                                        class="form-select w-auto"
                                        aria-label="Select room"
                                    >
                                        <option :value="undefined">All rooms</option>
                                        <option
                                            v-for="room in Object.values(rooms.perIdFilterBySelectedDepartments.value)
                                                .filter((r) => r.is_basic)
                                                .sort((r1, r2) => {
                                                    return r1.name.toLowerCase().localeCompare(r2.name.toLowerCase())
                                                })"
                                            :key="room.id"
                                            :value="room"
                                        >
                                            {{ room.name }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <!-- Department filter -->
                            <div class="row mb-3">
                                <label for="select-department" class="form-label">Department:</label>
                                <div v-if="selectedDepartment" class="col-auto pe-0">
                                    <button
                                        type="button"
                                        class="btn-close"
                                        @click="handleDepartmentNameClick(-1)"
                                    ></button>
                                </div>

                                <div class="col-auto">
                                    <select
                                        id="select-department"
                                        v-model="selectedDepartment"
                                        class="form-select w-auto ms-1"
                                        aria-label="Select department"
                                    >
                                        <option :value="undefined">All departments</option>
                                        <option
                                            v-for="dept in departmentStore.departments"
                                            :key="dept.id"
                                            :value="dept"
                                        >
                                            {{ dept.abbrev }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <!-- Room attribute and name filters -->
                            <div v-if="!selectedRoom" class="row">
                                <div class="mb-3">
                                    <ClearableInput
                                        :input-id="'filter-input-roomName'"
                                        :label="'Filter by room name:'"
                                        v-model:text="roomNameFilter"
                                    ></ClearableInput>
                                </div>
                                <div class="mb-3">
                                    <DynamicSelect
                                        v-bind="{
                                            id: 'filter-select-attribute',
                                            label: 'Filter by attributes:',
                                            values: createFiltersValues(),
                                        }"
                                        v-model:selected-values="selectedRoomAttributes"
                                    ></DynamicSelect>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Calendar -->
                <div class="col">
                    <!-- Caption -->
                    <div class="row">
                        <div class="col-auto">
                            <div><span :style="{ color: scheduledCourseColor }">■ </span>Course</div>
                        </div>
                        <div v-for="type in roomReservationTypes.list.value" :key="type.id" class="col-auto">
                            <div><span :style="{ color: type.bg_color }">■ </span>{{ type.name }}</div>
                        </div>
                    </div>
                    <HourCalendar v-if="selectedRoom" @drag="handleDrag" :values="hourCalendarValues"></HourCalendar>
                    <RoomCalendar
                        v-else
                        @new-slot="handleNewSlot"
                        :values="roomCalendarValues"
                        @row-header-click="handleRoomNameClick"
                    ></RoomCalendar>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { createTime, listGroupBy, parseReason, toStringAtLeastTwoDigits } from '@/helpers'
import { apiKey, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type {
    BooleanRoomAttributeValue,
    CalendarDragEvent,
    CalendarProps,
    CalendarRoomReservationSlotData,
    CalendarScheduledCourseSlotData,
    CalendarSlot,
    CourseType,
    DynamicSelectElementBooleanValue,
    DynamicSelectElementNumericValue,
    DynamicSelectElementValue,
    FlopWeek,
    HourCalendarProps,
    NumericRoomAttributeValue,
    ReservationPeriodicity,
    ReservationPeriodicityType,
    RoomAttribute,
    RoomAttributeValue,
    RoomCalendarProps,
    RoomReservation,
    RoomReservationType,
    TimeSettings,
    User,
    WeekDay,
} from '@/assets/js/types'
import { ScheduledCourse, Time } from '@/assets/js/types'
import HourCalendar from '@/components/HourCalendar.vue'
import WeekPicker from '@/components/WeekPicker.vue'
import type { ComputedRef, Ref } from 'vue'
import { computed, markRaw, onMounted, ref, shallowRef, watchEffect } from 'vue'
import RoomCalendar from '@/components/RoomCalendar.vue'
import HourCalendarRoomReservationSlot from '@/components/HourCalendarRoomReservationSlot.vue'
import RoomCalendarRoomReservationSlot from '@/components/RoomCalendarRoomReservationSlot.vue'
import HourCalendarScheduledCourseSlot from '@/components/HourCalendarScheduledCourseSlot.vue'
import RoomCalendarScheduledCourseSlot from '@/components/RoomCalendarScheduledCourseSlot.vue'
import DynamicSelect from '@/components/DynamicSelect.vue'
import DynamicSelectedElementNumeric from '@/components/DynamicSelectedElementNumeric.vue'
import DynamicSelectedElementBoolean from '@/components/DynamicSelectedElementBoolean.vue'
import ClearableInput from '@/components/ClearableInput.vue'
import DeletePeriodicReservationDialog from '@/components/DeletePeriodicReservationDialog.vue'
import type { Department } from '@/stores/department'
import { useDepartmentStore } from '@/stores/department'
import { Room, useRoomStore } from '@/stores/room'

const api = ref<FlopAPI>(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))
let currentDepartment = ''
let currentUserId = -1
let loadingCounter = 0

interface RoomAttributeEntry {
    component: any
    value: DynamicSelectElementValue
}

interface Rooms {
    perDepartmentFilterBySelectedDepartments: ComputedRef<{ [departmentId: string]: Array<Room> }>
    listFilterBySelectedDepartments: ComputedRef<Array<Room>>
    perIdFilterBySelectedDepartments: ComputedRef<{ [roomId: string]: Room }>
    listFilterBySelectedDepartmentsAndFilters: ComputedRef<Array<Room>>
}

interface ScheduledCourses {
    list: ComputedRef<Array<ScheduledCourse>>
    perDepartment: Ref<{ [departmentId: string]: Array<ScheduledCourse> }>
    perDepartmentFilterByDepartmentsAndRooms: ComputedRef<{ [departmentId: string]: Array<ScheduledCourse> }>
    perDay: ComputedRef<{ [day: string]: Array<ScheduledCourse> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{
        [day: string]: { [roomId: string]: Array<ScheduledCourse> }
    }>
}

interface CourseTypes {
    perDepartment: Ref<{ [departmentId: string]: Array<CourseType> }>
    listFilterBySelectedDepartments: ComputedRef<Array<CourseType>>
}

interface RoomReservations {
    list: Ref<Array<RoomReservation>>
    perDay: ComputedRef<{ [day: string]: Array<RoomReservation> }>
}

interface RoomReservationTypes {
    list: Ref<Array<RoomReservationType>>
    perId: ComputedRef<{ [typeId: string]: RoomReservationType }>
}

interface ReservationPeriodicities {
    list: Ref<Array<ReservationPeriodicity>>
    perId: ComputedRef<{ [periodicityId: string]: ReservationPeriodicity }>
}

interface Users {
    list: Ref<Array<User>>
    perId: ComputedRef<{ [userId: string]: User }>
}

interface RoomAttributes {
    booleanList: Ref<Array<RoomAttribute>>
    numericList: Ref<Array<RoomAttribute>>
}

interface RoomAttributeValues {
    booleanList: Ref<Array<BooleanRoomAttributeValue>>
    numericList: Ref<Array<NumericRoomAttributeValue>>
}

const departmentStore = useDepartmentStore()
const roomStore = useRoomStore()

const weekDays = {
    list: ref<Array<WeekDay>>([]),
}

const rooms: Rooms = {
    perDepartmentFilterBySelectedDepartments: computed(() => {
        return filterBySelectedDepartments(roomStore.perDepartment)
    }),
    listFilterBySelectedDepartments: computed(() => {
        const out: Array<Room> = []
        Object.values(rooms.perDepartmentFilterBySelectedDepartments.value).forEach((rooms) => {
            out.push(...rooms.filter((room) => !out.find((r) => r.id === room.id)))
        })
        roomStore.rooms.forEach((room) => {
            if (room.departments.length === 0 && out.findIndex((r) => r.id === room.id) < 0) {
                out.push(room)
            }
        })
        return out
    }),
    perIdFilterBySelectedDepartments: computed(() => {
        return Object.fromEntries(
            rooms.listFilterBySelectedDepartments.value
                .filter((r) => r.is_basic)
                .sort((r1, r2) => {
                    return r1.name.toLowerCase().localeCompare(r2.name.toLowerCase())
                })
                .map((r) => [r.id, r])
        )
    }),
    listFilterBySelectedDepartmentsAndFilters: computed(() => {
        const attributeFilters: Array<
            [
                Array<DynamicSelectElementValue>,
                Array<RoomAttributeValue>,
                // Comparison between the filter value and the room's attribute value
                (filterVal: any, attributeVal: any) => boolean
            ]
        > = [
            [
                selectedBooleanAttributes.value,
                roomAttributeValues.booleanList.value,
                (filterVal: DynamicSelectElementBooleanValue, attributeVal: BooleanRoomAttributeValue) =>
                    filterVal.value !== attributeVal.value,
            ],
            [
                selectedNumericAttributes.value,
                roomAttributeValues.numericList.value,
                (filterVal: DynamicSelectElementNumericValue, attributeVal: NumericRoomAttributeValue) => {
                    return Number(attributeVal.value) >= filterVal.min && Number(attributeVal.value) <= filterVal.max
                },
            ],
        ]

        // Filter by room name
        let out = Object.values(rooms.perIdFilterBySelectedDepartments.value).filter((room) =>
            room.name.toLowerCase().includes(roomNameFilter.value.toLowerCase())
        )

        // Filter by attributes
        out = out.filter((room) => {
            const roomId = room.id
            let matchFilters = true

            attributeFilters.forEach((filterEntry) => {
                if (!matchFilters) {
                    // Skip the next checks if one failed
                    return
                }
                const selectedFilterAttributes = filterEntry[0]
                const attributeValues = filterEntry[1]
                const comparisonPredicate = filterEntry[2]
                // Consider only filters if at least one is selected
                if (selectedFilterAttributes.length > 0) {
                    selectedFilterAttributes.forEach((selectedFilterAttribute) => {
                        // Get the values of the current attribute
                        const filteredAttributeValues = attributeValues.filter(
                            (attributeValue) => attributeValue.attribute === selectedFilterAttribute.id
                        )
                        // Consider only attributes with at least one value
                        if (filteredAttributeValues.length > 0) {
                            // Try to find the value matching the room
                            const attributeValue = filteredAttributeValues.find((filt) => filt.room === roomId)
                            if (attributeValue && !comparisonPredicate(selectedFilterAttribute, attributeValue)) {
                                // The room has an attribute with a value which does not match the filter
                                matchFilters = false
                                return
                            }
                        }
                    })
                }
            })
            return matchFilters
        })
        return out
    }),
}

const scheduledCourses: ScheduledCourses = {
    list: computed(() => {
        return Object.values(scheduledCourses.perDepartment.value).flat(1)
    }),
    perDepartment: ref({}),
    perDepartmentFilterByDepartmentsAndRooms: computed(() => {
        return Object.fromEntries(
            Object.entries(scheduledCourses.perDepartment.value).map((entry) => [
                entry[0],
                entry[1].filter(
                    (course) => isRoomSelected(course.room.id) && isRoomInSelectedDepartments(course.room.id)
                ),
            ])
        )
    }),
    perDay: computed(() => {
        return listGroupBy(scheduledCourses.list.value, (course) => {
            // Make sure the day is valid
            const date = weekDays.list.value.find((weekDay) => {
                return weekDay.ref === course.day
            })?.date
            return date ? date : 'dateNotFound'
        })
    }),
    perDayPerRoomFilterBySelectedDepartments: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<ScheduledCourse> } } = {}
        Object.entries(scheduledCourses.perDay.value).forEach((entry) => {
            const day = entry[0]
            const courses = entry[1].filter((course) => {
                const dept = getScheduledCourseDepartment(course)
                return dept && selectedDepartments.value.includes(dept)
            })
            out[day] = listGroupBy(courses, (course) => `${course.room.id}`)
        })
        return out
    }),
}

const courseTypes: CourseTypes = {
    perDepartment: ref({}),
    listFilterBySelectedDepartments: computed(() => {
        return Object.values(filterBySelectedDepartments(courseTypes.perDepartment.value)).flat(1)
    }),
}

const roomReservations: RoomReservations = {
    list: ref([]),
    perDay: computed(() => {
        return listGroupBy(roomReservations.list.value, (reserv) => {
            const date = new Date(reserv.date)
            return createDateId(date.getDate(), date.getMonth() + 1)
        })
    }),
}

const roomReservationTypes: RoomReservationTypes = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(roomReservationTypes.list.value.map((t) => [t.id, t]))
    }),
}

const reservationPeriodicities: ReservationPeriodicities = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(reservationPeriodicities.list.value.map((p) => [p.periodicity.id, p]))
    }),
}

const reservationPeriodicityTypes = ref<Array<ReservationPeriodicityType>>([])

const users: Users = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(users.list.value.map((user) => [user.id, user]))
    }),
}

const roomAttributes: RoomAttributes = {
    booleanList: ref([]),
    numericList: ref([]),
}

const roomAttributeValues: RoomAttributeValues = {
    booleanList: ref([]),
    numericList: ref([]),
}

// Time Settings
const timeSettings = ref<Array<TimeSettings>>()
const dayStartTime = ref<Time>({ value: 0, text: '' })
const dayFinishTime = ref<Time>({ value: 0, text: '' })
const lunchBreakStartTime = ref<Time>({ value: 0, text: '' })
const lunchBreakFinishTime = ref<Time>({ value: 0, text: '' })

// Duration of new reservations by default, in minutes
const newReservationDefaultDuration = 60

// Background color of the course slots
const scheduledCourseColor = '#3399ff'

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
    week: currentWeek.value.week,
    year: currentWeek.value.year,
})

const loaderIsVisible = ref(false)

const reservationToDelete = ref<RoomReservation>()
const isReservationDeletionDialogOpen = ref(false)

const selectedRoom = ref<Room>()
const selectedDepartment = ref<Department>()
const selectedDepartments = computed(() => {
    let selected: Array<Department> = []

    if (!selectedDepartment.value) {
        // All departments
        if (!departmentStore.departments) {
            // No department fetched, cannot continue
            return []
        }
        selected = departmentStore.departments
    } else {
        // Department selected, get its name
        selected.push(selectedDepartment.value)
    }
    return selected
})

const selectedRoomAttributes = ref<Array<RoomAttributeEntry>>([])

// The boolean attributes selected in the filter
const selectedBooleanAttributes = computed(() => {
    return selectedRoomAttributes.value
        .filter((entry) => entry.component === markRaw(DynamicSelectedElementBoolean))
        .map((entry) => entry.value)
})

// The numeric  attributes selected in the filter
const selectedNumericAttributes = computed(() => {
    return selectedRoomAttributes.value
        .filter((entry) => entry.component === markRaw(DynamicSelectedElementNumeric))
        .map((entry) => entry.value)
})

const roomNameFilter = ref('')

/**
 * Computes the slots to display all the room reservations, grouped by day.
 */

interface RoomReservationSlots {
    list: ComputedRef<Array<CalendarSlot>>
    perDay: ComputedRef<{ [day: string]: Array<CalendarSlot> }>
    perDayFilterBySelectedDepartmentsAndRooms: ComputedRef<{ [day: string]: Array<CalendarSlot> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{ [day: string]: { [roomId: string]: Array<CalendarSlot> } }>
}

const roomReservationSlots: RoomReservationSlots = {
    list: computed(() => {
        return roomReservations.list.value.map(createRoomReservationSlot)
    }),
    perDay: computed(() => {
        const out: { [day: string]: Array<CalendarSlot> } = Object.fromEntries(
            Object.entries(
                listGroupBy(roomReservationSlots.list.value, (slot) => {
                    const date = new Date((slot.slotData as CalendarRoomReservationSlotData).reservation.date)
                    return createDateId(date.getDate(), date.getMonth() + 1)
                })
            )
        )
        return out
    }),
    perDayFilterBySelectedDepartmentsAndRooms: computed(() => {
        const out: { [day: string]: Array<CalendarSlot> } = Object.fromEntries(
            Object.entries(roomReservationSlots.perDay.value).map((entry) => [
                entry[0],
                entry[1].filter((slot) => {
                    const room = (slot.slotData as CalendarRoomReservationSlotData).reservation.room
                    return isRoomSelected(room) && isRoomInSelectedDepartments(room)
                }),
            ])
        )
        return out
    }),
    perDayPerRoomFilterBySelectedDepartments: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<CalendarSlot> } } = Object.fromEntries(
            Object.entries(roomReservationSlots.perDay.value).map((entry) => [
                // First value is the day
                entry[0],
                // Group the list by room
                listGroupBy(
                    // Filter the rooms not in the selected departments
                    entry[1].filter((slot) =>
                        isRoomInSelectedDepartments((slot.slotData as CalendarRoomReservationSlotData).reservation.room)
                    ),
                    (slot) => `${(slot.slotData as CalendarRoomReservationSlotData).reservation.room}`
                ),
            ])
        )
        return out
    }),
}

/**
 * Computes the slots to display all the scheduled courses, grouped by day.
 */
interface ScheduledCourseSlots {
    perDepartmentFilterBySelectedDepartmentsAndRooms: ComputedRef<{
        [departmentId: string]: Array<CalendarSlot>
    }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{ [day: string]: { [roomId: string]: Array<CalendarSlot> } }>
}

const scheduledCoursesSlots: ScheduledCourseSlots = {
    perDepartmentFilterBySelectedDepartmentsAndRooms: computed(() => {
        const out: { [date: string]: Array<CalendarSlot> } = {}
        Object.entries(scheduledCourses.perDepartmentFilterByDepartmentsAndRooms.value).map((entry) => {
            const deptId = entry[0]
            entry[1].forEach((course) => {
                // Make sure the day is valid
                const day = weekDays.list.value.find((weekDay) => {
                    return weekDay.ref === course.day
                })
                if (!day) {
                    return
                }
                // Make sure the course type belongs to the selected departments
                const courseType = courseTypes.listFilterBySelectedDepartments.value.find((courseType) => {
                    return courseType.name === course.course.type
                })
                if (!courseType) {
                    return
                }
                const date = day.date
                const slot = createScheduledCourseSlot(course, courseType, deptId)
                addTo(out, date, slot)
            })
        })
        return out
    }),
    perDayPerRoomFilterBySelectedDepartments: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<CalendarSlot> } } = {}
        Object.entries(scheduledCourses.perDayPerRoomFilterBySelectedDepartments.value).forEach((entry) => {
            out[entry[0]] = Object.fromEntries(
                Object.entries(entry[1]).map((e) => {
                    const slots: Array<CalendarSlot> = []
                    e[1].forEach((course) => {
                        // Make sure the course's room is in the selected departments
                        if (!isRoomInSelectedDepartments(course.room.id)) {
                            return
                        }

                        // Make sure the course type belongs to the selected departments
                        const courseType = courseTypes.listFilterBySelectedDepartments.value.find((courseType) => {
                            return courseType.name === course.course.type
                        })
                        if (!courseType) {
                            return
                        }

                        // Get the course's department
                        const dept = getScheduledCourseDepartment(course)
                        if (!dept) {
                            return
                        }
                        const deptId = `${dept.id}`
                        slots.push(createScheduledCourseSlot(course, courseType, deptId))
                    })
                    return [e[0], slots]
                })
            )
        })
        return out
    }),
}

const temporaryReservation = ref<RoomReservation>()

interface TemporaryCalendarSlots {
    perDay: ComputedRef<{ [day: string]: Array<CalendarSlot> }>
    perDayPerRoom: ComputedRef<{ [day: string]: { [roomId: string]: Array<CalendarSlot> } }>
}

const temporaryCalendarSlots: TemporaryCalendarSlots = {
    perDay: computed(() => {
        const out: { [index: string]: Array<CalendarSlot> } = {}
        if (temporaryReservation.value) {
            const reservation = temporaryReservation.value
            const slot = createRoomReservationSlot(reservation)
            const date = new Date(reservation.date)
            const id = createDateId(date.getDate(), date.getMonth() + 1)
            addTo(out, id, slot)
        }
        return out
    }),
    perDayPerRoom: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<CalendarSlot> } } = {}
        if (temporaryReservation.value) {
            const reservation = temporaryReservation.value
            const slot = createRoomReservationSlot(reservation)
            const date = new Date(reservation.date)
            const day = createDateId(date.getDate(), date.getMonth() + 1)
            out[day] = {}
            addTo(out[day], reservation.room, slot)
        }
        return out
    }),
}

const calendarValues = computed<CalendarProps>(() => {
    return {
        days: weekDays.list.value,
        year: `${selectedDate.value.year}`,
    }
})

const hourCalendarValues = computed<HourCalendarProps>(() => {
    const slots: { [index: string]: Array<CalendarSlot> } = {}

    for (const obj of [
        roomReservationSlots.perDayFilterBySelectedDepartmentsAndRooms.value,
        scheduledCoursesSlots.perDepartmentFilterBySelectedDepartmentsAndRooms.value,
        temporaryCalendarSlots.perDay.value,
    ]) {
        Object.keys(obj).forEach((key) => {
            obj[key].forEach((slot) => {
                addTo(slots, key, slot)
            })
        })
    }
    Object.entries(slots).forEach((entry) => {
        entry[1].sort((slot1, slot2) => slot1.slotData.startTime.value - slot2.slotData.startTime.value)
    })
    return Object.assign(
        {
            slots: slots,
            startTime: dayStartTime.value.value,
            endTime: dayFinishTime.value.value,
        },
        calendarValues.value
    )
})

const roomCalendarValues = computed<RoomCalendarProps>(() => {
    const slots: { [day: string]: { [roomId: string]: CalendarSlot[] } } = {}

    for (const obj of [
        roomReservationSlots.perDayPerRoomFilterBySelectedDepartments.value,
        scheduledCoursesSlots.perDayPerRoomFilterBySelectedDepartments.value,
        temporaryCalendarSlots.perDayPerRoom.value,
    ]) {
        Object.entries(obj).forEach((entry) => {
            const day = entry[0]
            if (!(day in slots)) {
                slots[day] = {}
            }
            Object.entries(entry[1]).forEach((e) => {
                e[1].forEach((slot) => addTo(slots[day], e[0], slot))
            })
        })
    }
    Object.values(slots).forEach((roomArrayPair) => {
        Object.values(roomArrayPair).forEach((array) =>
            array.sort((slot1, slot2) => slot1.slotData.startTime.value - slot2.slotData.startTime.value)
        )
    })
    return Object.assign(
        {
            slots: slots,
            rooms: rooms.listFilterBySelectedDepartments.value
                .filter(
                    (room) =>
                        room.is_basic &&
                        rooms.listFilterBySelectedDepartmentsAndFilters.value.findIndex((r) => r.id === room.id) >= 0
                )
                .sort((r1, r2) => r1.name.localeCompare(r2.name)),
        },
        calendarValues.value
    )
})

// Update weekDays
watchEffect(() => {
    console.log('Updating Week days')
    api.value.fetch.weekdays({ week: selectedDate.value.week, year: selectedDate.value.year }).then((value) => {
        weekDays.list.value = value
    })
})

// Week selection watcher
watchEffect(() => {
    console.log('Updating Rooms reservations')
    const date = selectedDate.value
    updateRoomReservations(date)
})

// Week selection and departments watcher
watchEffect(() => {
    console.log('Updating Scheduled courses')
    const date = selectedDate.value

    if (!departmentStore.departments) {
        return
    }
    updateScheduledCourses(date, departmentStore.departments)
})

// Time settings watcher
watchEffect(() => {
    console.log('Updating time settings')
    onTimeSettingsChanged(timeSettings.value)
})

/**
 * Takes an object having departments id as key and an array.
 * Returns the filtered entries of selected departments.
 * @param object
 */
function filterBySelectedDepartments<T>(object: { [key: string]: Array<T> }) {
    const out: { [departmentId: string]: Array<T> } = Object.fromEntries(
        Object.entries(object).filter(
            ([key]) => selectedDepartments.value.findIndex((dept) => `${dept.id}` === key) >= 0
        )
    )
    return out
}

function onTimeSettingsChanged(timeSettings?: Array<TimeSettings>) {
    if (!timeSettings) {
        return
    }

    let minStartTime = timeSettings[0].day_start_time
    let maxFinishTime = timeSettings[0].day_finish_time
    let minLunchBreakStartTime = timeSettings[0].lunch_break_start_time
    let maxLunchBreakFinishTime = timeSettings[0].lunch_break_finish_time
    timeSettings.forEach((setting) => {
        minStartTime = Math.min(minStartTime, setting.day_start_time)
        maxFinishTime = Math.max(maxFinishTime, setting.day_finish_time)
        minLunchBreakStartTime = Math.min(minLunchBreakStartTime, setting.lunch_break_start_time)
        maxLunchBreakFinishTime = Math.max(maxLunchBreakFinishTime, setting.lunch_break_finish_time)
    })

    dayStartTime.value = createTime(minStartTime)
    dayFinishTime.value = createTime(maxFinishTime)
    lunchBreakStartTime.value = createTime(minLunchBreakStartTime)
    lunchBreakFinishTime.value = createTime(maxLunchBreakFinishTime)
}

function createRoomReservationSlot(reservation: RoomReservation): CalendarSlot {
    const startTimeRaw = reservation.start_time.split(':')
    const startTimeValue = parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
    const startTime = createTime(startTimeValue)
    const endTimeRaw = reservation.end_time.split(':')
    const endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
    const endTime: Time = createTime(endTimeValue)

    let backgroundColor = '#ffffff'
    if (reservation.reservation_type in roomReservationTypes.perId.value) {
        const type = roomReservationTypes.perId.value[reservation.reservation_type]
        backgroundColor = type.bg_color
    }

    const slotData: CalendarRoomReservationSlotData = {
        reservation: reservation,
        rooms: rooms.perIdFilterBySelectedDepartments.value,
        users: users.perId.value,
        reservationTypes: Object.values(roomReservationTypes.list.value),
        periodicityTypes: reservationPeriodicityTypes.value,
        periodicity: reservation.periodicity,
        weekdays: weekDays.list.value,
        day: reservation.date,
        startTime: startTime,
        endTime: endTime,
        dayStart: dayStartTime.value,
        dayEnd: dayFinishTime.value,
        title: reservation.title,
        id: `roomreservation-${reservation.id}`,
        displayStyle: { background: backgroundColor },
        onPeriodicityDelete: () => {
            if (!reservation.periodicity) {
                return Promise.resolve()
            }
            const periodicityId = reservation.periodicity.periodicity.id
            const reservationsRemovalPromise = reservationRemoveFutureSamePeriodicity(reservation)
            if (!reservationsRemovalPromise) {
                return Promise.reject(`Could not remove the reservations with periodicity id ${periodicityId}`)
            }
            return reservationsRemovalPromise.then((_) => deleteReservationPeriodicity(periodicityId))
        },
    }
    return {
        slotData: slotData,
        component: shallowRef(selectedRoom.value ? HourCalendarRoomReservationSlot : RoomCalendarRoomReservationSlot),
        actions: {
            delete: deleteRoomReservationSlot,
            save: updateRoomReservation,
        },
    }
}

function createScheduledCourseSlot(course: ScheduledCourse, courseType: CourseType, deptId: string): CalendarSlot {
    const startTime = createTime(course.start_time)
    const endTime = createTime(course.start_time + courseType.duration)

    let departmentName = ''
    if (departmentStore.departments) {
        const department = departmentStore.departments.find((dept) => `${dept.id}` === deptId)
        if (department) {
            departmentName = department.abbrev
        }
    }

    const slotData: CalendarScheduledCourseSlotData = {
        course: course,
        department: departmentName,
        rooms: rooms.perIdFilterBySelectedDepartments.value,
        day: course.day,
        startTime: startTime,
        endTime: endTime,
        title: course.course.module.abbrev + 'AAA',
        id: `scheduledcourse-${course.course.id}`,
        displayStyle: { background: scheduledCourseColor },
    }
    return {
        slotData: slotData,
        component: shallowRef(selectedRoom.value ? HourCalendarScheduledCourseSlot : RoomCalendarScheduledCourseSlot),
        actions: {
            // No course save
            save: undefined,
            // No course deletion
            delete: undefined,
        },
    }
}

function createFiltersValues(): Array<RoomAttributeEntry> {
    const out = []

    out.push(
        ...roomAttributes.booleanList.value.map((attribute) => {
            return {
                component: markRaw(DynamicSelectedElementBoolean),
                value: {
                    id: attribute.id,
                    name: attribute.name,
                    value: false,
                },
            }
        })
    )
    out.push(
        ...roomAttributes.numericList.value.map((attribute) => {
            const values = roomAttributeValues.numericList.value
                .filter((att) => att.attribute === attribute.id)
                .map((att) => att.value)
            const min = Math.min(...values)
            const max = Math.max(...values)
            return {
                component: markRaw(DynamicSelectedElementNumeric),
                value: {
                    id: attribute.id,
                    name: attribute.name,
                    min: min,
                    max: max,
                    initialMin: min,
                    initialMax: max,
                },
            }
        })
    )
    return out
}

function addTo<T>(collection: { [p: string]: Array<T> }, id: string | number, element: T): void {
    if (!collection[id]) {
        collection[id] = []
    }
    collection[id].push(element)
}

function updateRoomReservations(date: FlopWeek): Promise<void> {
    const week = date.week
    const year = date.year

    showLoading()
    return api.value.fetch.roomReservations({ week: week, year: year }).then((value) => {
        roomReservations.list.value = value
        temporaryReservation.value = undefined
        hideLoading()
    })
}

function updateScheduledCourses(date: FlopWeek, departments: Array<Department>) {
    const week = date.week
    const year = date.year

    showLoading()
    scheduledCourses.perDepartment.value = {}
    let count = departments.length

    if (count === 0) {
        hideLoading()
        return
    }

    const coursesList: { [p: string]: ScheduledCourse[] } = {}
    departments.forEach((dept) => {
        api.value.fetch.scheduledCourses({ week: week, year: year, department: dept.abbrev }).then((value) => {
            coursesList[dept.id] = value
            if (--count === 0) {
                scheduledCourses.perDepartment.value = coursesList
                hideLoading()
            }
        })
    })
}

function updateReservationPeriodicities() {
    return api.value.fetch.reservationPeriodicities().then((value) => {
        reservationPeriodicities.list.value = value
    })
}

function updateRoomReservation(newData: CalendarRoomReservationSlotData, oldData: CalendarRoomReservationSlotData) {
    const newReservation = newData.reservation
    const oldReservation = oldData.reservation

    if (oldReservation.id < 0) {
        // The reservation is a new one, just add it to the list
        roomReservations.list.value.push(newReservation)

        // Clear the temporary slot
        temporaryReservation.value = undefined

        if (newReservation.periodicity != oldReservation.periodicity) {
            // The reservation has a periodicity, new reservations might have been created.
            // Update the lists of reservations and periodicity
            updateRoomReservations(selectedDate.value)
            updateReservationPeriodicities()
        }
        return
    }

    // Find the reservation index from the list of reservations
    const index = roomReservations.list.value.findIndex((reserv) => reserv.id === oldReservation.id)

    if (index < 0) {
        // Reservation not found
        console.error(`Could not find reservation with id: ${oldReservation.id}`)
        return
    }

    if (newReservation.periodicity != oldReservation.periodicity) {
        // The reservation has a new periodicity, new reservations might have been created.
        // Update the lists of reservations and periodicities
        updateRoomReservations(selectedDate.value)
        updateReservationPeriodicities()
    }

    // Replace the reservation at index
    roomReservations.list.value[index] = newReservation
}

function handleReason(level: string, message: string) {
    console.error(`${level}: ${message}`)
}

function deleteRoomReservationSlot(toDelete: CalendarRoomReservationSlotData) {
    const reservation = toDelete.reservation

    // Target reservation is a temporary one, just remove the slot
    if (reservation.id < 0) {
        temporaryReservation.value = undefined
        return
    }

    if (reservation.periodicity && reservation.periodicity.periodicity.id >= 0) {
        // The reservation is linked to a periodicity,
        // we must ask if we remove other reservations related to this periodicity
        reservationToDelete.value = reservation
        isReservationDeletionDialogOpen.value = true
        return
    }

    reservationDeletionConfirmed(reservation)
}

function reservationRemoveAllSamePeriodicity(reservation: RoomReservation) {
    if (!reservation.periodicity || reservation.periodicity.periodicity.id < 0) {
        return
    }
    const periodicityId = reservation.periodicity.periodicity.id

    // Get the list of all the reservations to delete, which are those who share the periodicity ID
    api.value.fetch.roomReservations({ periodicityId: periodicityId }).then((deletionList) => {
        // Delete each reservation in the list
        deleteRoomReservations(deletionList)
            .then((_) => {
                // Remove the associated periodicity
                api.value.delete.reservationPeriodicity(periodicityId)
            })
            // Close the dialog when all the reservations have been deleted
            .finally(closeReservationDeletionDialog)
    })
}

function reservationRemoveCurrentAndFutureSamePeriodicity(reservation: RoomReservation) {
    if (!reservation.periodicity || reservation.periodicity.periodicity.id < 0) {
        return
    }

    const periodicityId = reservation.periodicity.periodicity.id
    const reservationDate = new Date(reservation.date)
    // Remove all the future reservations of the same periodicity
    reservationRemoveFutureSamePeriodicity(reservation)
        // Remove the current reservation
        ?.then((_) => {
            deleteRoomReservation(reservation)
        })
        // Reduce the periodicity end date to the day before the current reservation
        .then((_) => {
            // Get the day before the reservation
            const dayBefore = new Date(reservationDate)
            dayBefore.setDate(dayBefore.getDate() - 1)

            // Get the periodicity data
            const periodicity = reservationPeriodicities.perId.value[periodicityId].periodicity
            if (periodicity.periodicity_type === '') {
                // Should never arrive here as an existing periodicity always has a type. Written for the type checks.
                return
            }
            // Match the api path with the periodicity type
            let apiCall
            switch (periodicity.periodicity_type) {
                case 'BM':
                    apiCall = api.value.patch.reservationPeriodicityByMonth
                    break
                case 'EM':
                    apiCall = api.value.patch.reservationPeriodicityEachMonthSameDate
                    break
                case 'BW':
                    apiCall = api.value.patch.reservationPeriodicityByWeek
                    break
            }
            // Finally apply the patch
            return apiCall(periodicity.id, { end: dayBefore.toISOString().split('T')[0] })
        })
        ?.then((_) => {
            updateRoomReservations(selectedDate.value)
            updateReservationPeriodicities()
        })
        .finally(closeReservationDeletionDialog)
}

/**
 * Removes all the reservations having the same periodicity as the provided reservation and happening at a later date.
 * @param reservation The reservation to base the periodicity removal.
 */
function reservationRemoveFutureSamePeriodicity(reservation: RoomReservation) {
    if (!reservation.periodicity || reservation.periodicity.periodicity.id < 0) {
        return
    }

    const periodicityId = reservation.periodicity.periodicity.id
    const reservationDate = new Date(reservation.date)
    const reservationTime = reservationDate.getTime()

    // Get the list of all the reservations to delete, which are those who share the periodicity ID and are later than
    // the selected
    return api.value.fetch.roomReservations({ periodicityId: periodicityId }).then((deletionList) => {
        // Filter the older reservations
        deletionList = deletionList.filter((reserv) => new Date(reserv.date).getTime() > reservationTime)
        return deleteRoomReservations(deletionList)
    })
}

function deleteReservationPeriodicity(periodicityId: number): Promise<void> {
    return api.value.delete
        .reservationPeriodicity(periodicityId)
        .then((_) => {
            updateReservationPeriodicities()
        })
        .then((_) => updateRoomReservations(selectedDate.value))
}

function closeReservationDeletionDialog() {
    reservationToDelete.value = undefined
    isReservationDeletionDialogOpen.value = false
}

function deleteRoomReservation(reservation: RoomReservation): Promise<void> {
    return api.value.delete
        .roomReservation(reservation.id)
        .then(
            (_) => {
                // Filter the list of reservations
                roomReservations.list.value = roomReservations.list.value.filter((r) => r.id != reservation.id)
            },
            (reason) => parseReason(reason, handleReason)
        )
        .catch((reason) => parseReason(reason, handleReason))
}

async function deleteRoomReservations(deletionList: Array<RoomReservation>) {
    await Promise.all(
        deletionList.map(async (reserv) => {
            return await deleteRoomReservation(reserv)
        })
    )
}

function reservationDeletionConfirmed(reservation: RoomReservation) {
    deleteRoomReservation(reservation)
    closeReservationDeletionDialog()
}

function hideLoading(): void {
    if (--loadingCounter <= 0) {
        loaderIsVisible.value = false
    }
}

function showLoading(): void {
    ++loadingCounter
    loaderIsVisible.value = true
}

function handleRoomNameClick(roomId: number) {
    selectedRoom.value = roomStore.rooms.find((r) => r.id === roomId)
}

function handleDepartmentNameClick(deptId: number) {
    selectedDepartment.value = departmentStore.departments.find((dept) => dept.id === deptId)
}

let newReservationId = -1

function handleDrag(drag: CalendarDragEvent) {
    if (drag.startDate.getDate() != drag.endDate.getDate()) {
        console.error('Reserving a room for more than a day is not accepted.')
        return
    }
    const day = toStringAtLeastTwoDigits(drag.startDate.getDate())
    const month = toStringAtLeastTwoDigits(drag.startDate.getMonth() + 1)
    const year = drag.startDate.getFullYear()
    const date = `${year}-${month}-${day}`
    temporaryReservation.value = {
        date: date,
        description: '',
        email: false,
        end_time: drag.endTime.text,
        id: newReservationId--,
        periodicity: null,
        reservation_type: roomReservationTypes.list.value[0].id,
        responsible: currentUserId,
        room: selectedRoom.value?.id ?? -1,
        start_time: drag.startTime.text,
        title: '',
    }
}

/**
 * Called when the room calendar receives a new slot instruction.
 * Sets the temporary reservation slot value to a new reservation with day and room already defined.
 * @param date
 * @param roomId
 */
function handleNewSlot(date: Date, roomId: string) {
    const now = new Date()
    const reservDate = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`
    temporaryReservation.value = {
        date: reservDate,
        description: '',
        email: false,
        end_time: new Date(now.getTime() + newReservationDefaultDuration * 60000).toTimeString(),
        id: newReservationId--,
        periodicity: null,
        reservation_type: roomReservationTypes.list.value[0].id,
        responsible: currentUserId,
        room: parseInt(roomId, 10),
        start_time: now.toTimeString(),
        title: '',
    }
}

function createDateId(day: string | number, month: string | number): string {
    return `${toStringAtLeastTwoDigits(day)}/${toStringAtLeastTwoDigits(month)}`
}

/**
 * Takes a room id and
 * returns true if the room is available to the selected departments, false otherwise
 * @param roomId The room id
 */
function isRoomInSelectedDepartments(roomId: number): boolean {
    const room = rooms.listFilterBySelectedDepartments.value.find((r) => r.id === roomId)
    return !(!room || !room.basic_rooms.find((r: { id: number }) => r.id === roomId))
}

function isRoomSelected(roomId: number): boolean {
    if (selectedRoom.value) {
        // Return false if the course's sub rooms are not selected
        if (!roomStore.perId[roomId]?.basic_rooms.find((val) => val.id === selectedRoom.value.id)) {
            return false
        }
    }
    return true
}

function getScheduledCourseDepartment(course: ScheduledCourse): Department | undefined {
    const departmentEntry = Object.entries(scheduledCourses.perDepartment.value).find((entry) => {
        return entry[1].find((c) => c.id === course.id)
    })
    if (departmentEntry) {
        const deptId = departmentEntry[0]
        return departmentStore.departments.find((dept) => `${dept.id}` === deptId)
    }
    return undefined
}

onMounted(() => {
    const dbDataElement = document.getElementById('json_data')
    if (dbDataElement && dbDataElement.textContent) {
        const data = JSON.parse(dbDataElement.textContent)

        if ('dept' in data) {
            currentDepartment = data.dept
        }
        if ('user_id' in data) {
            currentUserId = data.user_id
        }
    }
    departmentStore.remote.fetch().then((value) => {
        // Select the current department by default
        if (value) {
            selectedDepartment.value = value.find((dept) => dept.abbrev === currentDepartment)

            courseTypes.perDepartment.value = {}
            const typesList: { [key: string]: Array<CourseType> } = {}
            let typesCounter = departmentStore.departments.length
            value.forEach((dept) => {
                api.value.fetch.courseTypes({ department: dept.abbrev }).then((value) => {
                    typesList[dept.id] = value
                    if (--typesCounter === 0) {
                        // Update the course types list ref only once every department is handled
                        courseTypes.perDepartment.value = typesList
                    }
                })
            })
        }
    })

    roomStore.remote.fetch()

    api.value.fetch.timeSettings().then((value) => {
        timeSettings.value = value
    })

    api.value.fetch.roomReservationTypes().then((value) => {
        if (value.length === 0) {
            value = ['Unknown']
        }
        roomReservationTypes.list.value = value
    })

    updateReservationPeriodicities()

    api.value.fetch.reservationPeriodicityTypes().then((value) => {
        reservationPeriodicityTypes.value = value
    })

    api.value.fetch.users().then((value) => {
        users.list.value = value
    })

    api.value.fetch.booleanRoomAttributes().then((value) => {
        roomAttributes.booleanList.value = value
    })

    api.value.fetch.numericRoomAttributes().then((value) => {
        roomAttributes.numericList.value = value
    })

    api.value.fetch.booleanRoomAttributeValues().then((value) => {
        roomAttributeValues.booleanList.value = value
    })

    api.value.fetch.numericRoomAttributeValues().then((value) => {
        roomAttributeValues.numericList.value = value
    })
})
</script>

<script lang="ts">
export default {
    name: 'RoomReservationView',
    components: {},
}
</script>

<style scoped>
.loader {
    position: fixed;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.6) url('@/assets/images/logo-head-gribou-rc-hand.svg') no-repeat 50% 50%;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    cursor: wait;
}
</style>
