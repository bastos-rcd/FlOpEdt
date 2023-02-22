<template>
    <div>
        <div class="loader" v-if="loaderIsVisible"></div>
        <div class="container-fluid">
            <div class="row">
                <!-- Week picker and filters -->
                <div class="col-6 col-md-5 col-lg-4 col-xl-3">
                    <WeekPicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></WeekPicker>
                    <div class="row">
                        <!-- Filters -->
                        <div class="col">
                            <!-- Room filter -->
                            <div class="mb-3">
                                <label for="select-room" class="form-label">Room:</label>
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
                            <!-- Department filter -->
                            <div class="mb-3">
                                <label for="select-department" class="form-label">Department:</label>
                                <select
                                    id="select-department"
                                    v-model="selectedDepartment"
                                    class="form-select w-auto ms-1"
                                    aria-label="Select department"
                                >
                                    <option :value="undefined">All departments</option>
                                    <option v-for="dept in departments.list.value" :key="dept.id" :value="dept">
                                        {{ dept.abbrev }}
                                    </option>
                                </select>
                            </div>
                            <!-- Room attribute filters -->
                            <div v-if="!selectedRoom">
                                <div class="mb-3">
                                    <DynamicSelect
                                        v-bind="{
                                            id: 'select-attribute-bool',
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
                    <HourCalendar v-if="selectedRoom" @drag="handleDrag" :values="hourCalendarValues"></HourCalendar>
                    <RoomCalendar v-else @new-slot="handleNewSlot" :values="roomCalendarValues"></RoomCalendar>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { convertDecimalTimeToHuman, listGroupBy, parseReason, toStringAtLeastTwoDigits } from '@/assets/js/helpers'
import { apiKey, apiToken, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type {
    BooleanRoomAttributeValue,
    CalendarDragEvent,
    CalendarProps,
    CalendarRoomReservationSlotData,
    CalendarScheduledCourseSlotData,
    CalendarSlot,
    CourseType,
    Department,
    DynamicSelectElementBooleanValue,
    DynamicSelectElementNumericValue,
    DynamicSelectElementValue,
    FlopWeek,
    HourCalendarProps,
    NumericRoomAttributeValue,
    Room,
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
import HourCalendar from '@/components/calendar/HourCalendar.vue'
import WeekPicker from '@/components/WeekPicker.vue'
import { getDepartment } from '@/main'
import type { ComputedRef, Ref } from 'vue'
import { computed, markRaw, onMounted, ref, shallowRef, watchEffect } from 'vue'
import RoomCalendar from '@/components/calendar/RoomCalendar.vue'
import HourCalendarRoomReservationSlot from '@/components/calendar/HourCalendarRoomReservationSlot.vue'
import RoomCalendarRoomReservationSlot from '@/components/calendar/RoomCalendarRoomReservationSlot.vue'
import HourCalendarScheduledCourseSlot from '@/components/calendar/HourCalendarScheduledCourseSlot.vue'
import RoomCalendarScheduledCourseSlot from '@/components/calendar/RoomCalendarScheduledCourseSlot.vue'
import DynamicSelect from '@/components/dynamicSelect/DynamicSelect.vue'
import DynamicSelectedElementNumeric from '@/components/dynamicSelect/DynamicSelectedElementNumeric.vue'
import DynamicSelectedElementBoolean from '@/components/dynamicSelect/DynamicSelectedElementBoolean.vue'

const api = ref<FlopAPI>(requireInjection(apiKey))
const authToken = requireInjection(apiToken)
const currentWeek = ref(requireInjection(currentWeekKey))
const currentDepartment = getDepartment()
let loadingCounter = 0

interface RoomAttributeEntry {
    component: any
    value: DynamicSelectElementValue
}

interface Rooms {
    list: ComputedRef<Array<Room>>
    perDepartment: Ref<{ [departmentId: string]: Array<Room> }>
    perDepartmentFilterBySelectedDepartments: ComputedRef<{ [departmentId: string]: Array<Room> }>
    listFilterBySelectedDepartments: ComputedRef<Array<Room>>
    perIdFilterBySelectedDepartments: ComputedRef<{ [roomId: string]: Room }>
    perId: ComputedRef<{ [roomId: string]: Room }>
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
    perDayFilterByDepartmentsAndRooms: ComputedRef<{ [day: string]: Array<RoomReservation> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{
        [day: string]: { [roomId: string]: Array<RoomReservation> }
    }>
}

interface RoomReservationTypes {
    list: Ref<Array<RoomReservationType>>
    perId: ComputedRef<{ [typeId: string]: RoomReservationType }>
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

// API data
const departments = {
    list: ref<Array<Department>>([]),
}

const weekDays = {
    list: ref<Array<WeekDay>>([]),
}

const rooms: Rooms = {
    list: computed(() => {
        const out: Array<Room> = []
        Object.values(rooms.perDepartment.value).forEach((rooms) => {
            out.push(...rooms.filter((room) => !out.includes(room)))
        })
        return out
    }),
    perDepartment: ref({}),
    perDepartmentFilterBySelectedDepartments: computed(() => {
        return filterBySelectedDepartments(rooms.perDepartment.value)
    }),
    listFilterBySelectedDepartments: computed(() => {
        const out: Array<Room> = []
        Object.values(rooms.perDepartmentFilterBySelectedDepartments.value).forEach((rooms) => {
            out.push(...rooms.filter((room) => !out.find((r) => r.id === room.id)))
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
    perId: computed(() => {
        return Object.fromEntries(rooms.list.value.map((r) => [r.id, r]))
    }),
    listFilterBySelectedDepartmentsAndFilters: computed(() => {
        const filters: Array<
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
        return Object.values(rooms.perIdFilterBySelectedDepartments.value).filter((room) => {
            const roomId = room.id
            let matchFilters = true

            filters.forEach((filterEntry) => {
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
                entry[1].filter((course) => isRoomSelected(course.room) && isRoomInSelectedDepartments(course.room)),
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
            out[day] = listGroupBy(courses, (course) => `${course.room}`)
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
    perDayFilterByDepartmentsAndRooms: computed(() => {
        const out: { [day: string]: Array<RoomReservation> } = Object.fromEntries(
            Object.entries(roomReservations.perDay.value).map((entry) => {
                return [
                    entry[0], // Keep the day as id
                    entry[1].filter((reservation) => {
                        // Apply the filter
                        return isRoomInSelectedDepartments(reservation.room) && isRoomSelected(reservation.room)
                    }),
                ]
            })
        )
        return out
    }),
    perDayPerRoomFilterBySelectedDepartments: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<RoomReservation> } } = {}
        Object.entries(roomReservations.perDayFilterByDepartmentsAndRooms.value).forEach(
            (entry: [string, RoomReservation[]]) => {
                const day = entry[0]
                out[day] = {}
                entry[1].forEach((reservation) => {
                    addTo(out[day], `${reservation.room}`, reservation)
                })
            }
        )
        return out
    }),
}

const roomReservationTypes: RoomReservationTypes = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(roomReservationTypes.list.value.map((t) => [t.id, t]))
    }),
}

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

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
    week: currentWeek.value.week,
    year: currentWeek.value.year,
})

const loaderIsVisible = ref(false)

const selectedRoom = ref<Room>()
const selectedDepartment = ref<Department>()
const selectedDepartments = computed(() => {
    let selected: Array<Department> = []

    if (!selectedDepartment.value) {
        // All departments
        if (!departments.list.value) {
            // No department fetched, cannot continue
            return []
        }
        selected = departments.list.value
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

/**
 * Computes the slots to display all the room reservations, grouped by day.
 */

interface RoomReservationSlots {
    filterBySelectedDepartments: ComputedRef<{ [day: string]: Array<CalendarSlot> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{ [day: string]: { [roomId: string]: Array<CalendarSlot> } }>
}

const roomReservationSlots: RoomReservationSlots = {
    filterBySelectedDepartments: computed(() => {
        const out: { [day: string]: Array<CalendarSlot> } = Object.fromEntries(
            Object.entries(roomReservations.perDayFilterByDepartmentsAndRooms.value).map((entry) => [
                // Keep the day as key
                entry[0],
                // Create a slot for each of the reservations
                entry[1].map(createRoomReservationSlot),
            ])
        )
        return out
    }),
    perDayPerRoomFilterBySelectedDepartments: computed(() => {
        const out: { [day: string]: { [roomId: string]: Array<CalendarSlot> } } = {}
        Object.entries(roomReservations.perDayPerRoomFilterBySelectedDepartments.value).forEach((entry) => {
            const day = entry[0]
            const reservations = entry[1]
            if (!(day in out)) {
                out[day] = {}
            }
            Object.values(reservations)
                .flat(1)
                .forEach((reservation) => {
                    const slot = createRoomReservationSlot(reservation)
                    addTo(out[day], `${reservation.room}`, slot)
                })
        })
        return out
    }),
}

/**
 * Computes the slots to display all the scheduled courses, grouped by day.
 */
interface ScheduledCourseSlots {
    perDepartmentFilterBySelectedDepartments: ComputedRef<{ [departmentId: string]: Array<CalendarSlot> }>
    perDayPerRoomFilterBySelectedDepartments: ComputedRef<{ [day: string]: { [roomId: string]: Array<CalendarSlot> } }>
}

const scheduledCoursesSlots: ScheduledCourseSlots = {
    perDepartmentFilterBySelectedDepartments: computed(() => {
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
                        if (!isRoomInSelectedDepartments(course.room)) {
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
        roomReservationSlots.filterBySelectedDepartments.value,
        scheduledCoursesSlots.perDepartmentFilterBySelectedDepartments.value,
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
            startTime: dayStartTime.value.value - (60 + (dayStartTime.value.value % 60)),
            endTime: dayFinishTime.value.value + (60 - (dayFinishTime.value.value % 60)),
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
    fetchWeekDays(selectedDate.value.week, selectedDate.value.year).then((value) => {
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

    if (!departments.list.value) {
        return
    }
    updateScheduledCourses(date, departments.list.value)
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

function createTime(time: number): Time {
    const text = convertDecimalTimeToHuman(time / 60)
    return new Time(time, text)
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
        day: reservation.date,
        startTime: startTime,
        endTime: endTime,
        title: reservation.title,
        id: `roomreservation-${reservation.id}`,
        displayStyle: { background: backgroundColor },
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
    if (departments.list.value) {
        const department = departments.list.value.find((dept) => `${dept.id}` === deptId)
        if (department) {
            departmentName = department.abbrev
        }
    }
    const type = Object.values(roomReservationTypes.list.value).find((type) => type.name === 'Course')
    let backgroundColor = '#ffffff'
    if (type) {
        backgroundColor = type.bg_color
    }
    const slotData: CalendarScheduledCourseSlotData = {
        course: course,
        department: departmentName,
        rooms: rooms.perIdFilterBySelectedDepartments.value,
        day: course.day,
        startTime: startTime,
        endTime: endTime,
        title: course.course.module.abbrev,
        id: `scheduledcourse-${course.course.id}`,
        displayStyle: { background: backgroundColor },
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
            return {
                component: markRaw(DynamicSelectedElementNumeric),
                value: {
                    id: attribute.id,
                    name: attribute.name,
                    min: 0,
                    max: 50,
                    initialMin: 0,
                    initialMax: 50,
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

function updateRoomReservations(date: FlopWeek) {
    const week = date.week
    const year = date.year

    showLoading()
    fetchRoomReservations(week, year, {}).then((value) => {
        roomReservations.list.value = value
        hideLoading()
    })
    temporaryReservation.value = undefined
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
        fetchScheduledCourses(week, year, dept.abbrev).then((value) => {
            coursesList[dept.id] = value
            if (--count === 0) {
                scheduledCourses.perDepartment.value = coursesList
                hideLoading()
            }
        })
    })
}

function updateRoomReservation(newData: CalendarRoomReservationSlotData, oldData: CalendarRoomReservationSlotData) {
    const newReservation = newData.reservation
    const oldReservation = oldData.reservation

    if (oldReservation.id < 0) {
        // The reservation is a new one, just add it to the list
        roomReservations.list.value.push(newData.reservation)
        // Clear the temporary slot
        temporaryReservation.value = undefined
        return
    }

    // Find the reservation index from the list of reservations
    const index = roomReservations.list.value.findIndex((reserv) => reserv.id === oldReservation.id)

    if (index < 0) {
        // Reservation not found
        console.error(`Could not find reservation with id: ${oldReservation.id}`)
        return
    }
    // Replace the reservation at index
    roomReservations.list.value[index] = newReservation
}

function handleReason(level: string, message: string) {
    console.error(`${level}: ${message}`)
}

function deleteRoomReservationSlot(toDelete: CalendarRoomReservationSlotData) {
    const reservation = toDelete.reservation

    if (reservation.id < 0) {
        temporaryReservation.value = undefined
        return
    }

    // Target reservation is in the database, so we need to remove it first
    api.value.delete
        .roomReservation(reservation.id, authToken)
        .then(
            (_) => {
                // Filter the list of reservations
                roomReservations.list.value = roomReservations.list.value.filter((r) => r.id != reservation.id)
            },
            (reason) => parseReason(reason, handleReason)
        )
        .catch((reason) => parseReason(reason, handleReason))
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
        email: true,
        end_time: drag.endTime.text,
        id: newReservationId--,
        periodicity: -1,
        reservation_type: -1,
        responsible: 553,
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
        email: true,
        end_time: new Date(now.getTime() + newReservationDefaultDuration * 60000).toTimeString(),
        id: newReservationId--,
        periodicity: -1,
        reservation_type: -1,
        responsible: 553,
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
    return !(!room || !room.basic_rooms.find((r) => r.id === roomId))
}

function isRoomSelected(roomId: number): boolean {
    if (selectedRoom.value) {
        // Return false if the course's sub rooms are not selected
        if (!rooms.perId.value[roomId]?.basic_rooms.find((val) => val.id === selectedRoom.value.id)) {
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
        return departments.list.value.find((dept) => `${dept.id}` === deptId)
    }
    return undefined
}

onMounted(() => {
    fetchDepartments().then((value) => {
        departments.list.value = value

        // Select the current department by default
        if (departments.list.value) {
            selectedDepartment.value = departments.list.value.find((dept) => dept.abbrev === currentDepartment)

            rooms.perDepartment.value = {}
            courseTypes.perDepartment.value = {}
            const roomsList: { [key: string]: Array<Room> } = {}
            const typesList: { [key: string]: Array<CourseType> } = {}
            const departmentsCount = departments.list.value.length
            let roomsCounter = departmentsCount
            let typesCounter = departmentsCount
            departments.list.value.forEach((dept) => {
                // Fetch the rooms of each selected department
                fetchRooms(dept.abbrev).then((value) => {
                    roomsList[dept.id] = value
                    if (--roomsCounter === 0) {
                        // Update the rooms list ref only once every department is handled
                        rooms.perDepartment.value = roomsList
                    }
                })

                fetchCourseTypes(dept.abbrev).then((value) => {
                    typesList[dept.id] = value
                    if (--typesCounter === 0) {
                        // Update the course types list ref only once every department is handled
                        courseTypes.perDepartment.value = typesList
                    }
                })
            })
        }
    })

    fetchTimeSettings().then((value) => {
        timeSettings.value = value
    })

    fetchRoomReservationTypes().then((value) => {
        roomReservationTypes.list.value = value
    })

    fetchUsers().then((value) => {
        users.list.value = value
    })

    fetchBooleanRoomAttributes().then((value) => {
        roomAttributes.booleanList.value = value
    })

    fetchNumericRoomAttributes().then((value) => {
        roomAttributes.numericList.value = value
    })

    fetchBooleanRoomAttributeValues().then((value) => {
        roomAttributeValues.booleanList.value = value
    })

    fetchNumericRoomAttributeValues().then((value) => {
        roomAttributeValues.numericList.value = value
    })
})

// Fetch functions
async function fetchDepartments() {
    return await api.value.fetch.all.departments()
}

async function fetchWeekDays(week: number, year: number) {
    return await api.value.fetch.target.weekdays(week, year)
}

async function fetchRooms(department: string) {
    return await api.value.fetch.all.rooms(department)
}

async function fetchTimeSettings() {
    return await api.value.fetch.all.timeSettings()
}

async function fetchRoomReservations(week: number, year: number, params: { roomId?: number }) {
    return await api.value.fetch.target.roomReservations(week, year, params)
}

async function fetchRoomReservationTypes() {
    return await api.value.fetch.all.roomReservationTypes()
}

async function fetchScheduledCourses(week: number, year: number, department: string) {
    return await api.value.fetch.target.scheduledCourses(week, year, department)
}

async function fetchCourseTypes(department: string) {
    return await api.value.fetch.all.courseTypes(department)
}

async function fetchUsers() {
    return await api.value.fetch.all.users()
}

async function fetchBooleanRoomAttributes() {
    return await api.value.fetch.all.booleanRoomAttributes()
}

async function fetchNumericRoomAttributes() {
    return await api.value.fetch.all.numericRoomAttributes()
}

async function fetchBooleanRoomAttributeValues() {
    return await api.value.fetch.all.booleanRoomAttributeValues()
}

async function fetchNumericRoomAttributeValues() {
    return await api.value.fetch.all.numericRoomAttributeValues()
}
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
