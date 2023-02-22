import type { ShallowRef } from 'vue'

export interface FlopWeek {
    week: number
    year: number
}

export interface TimeSettings {
    id: number
    day_start_time: number
    day_finish_time: number
    lunch_break_start_time: number
    lunch_break_finish_time: number
    days: Array<string>
    default_preference_duration: number
    department: number
}

export class Time {
    value: number
    text: string

    constructor(value: number, text: string) {
        this.value = value
        this.text = text
    }
}

export interface WeekDay {
    date: string
    name: string
    num: number
    ref: string
}

export interface Department {
    id: number
    abbrev: string
}

export interface User {
    id: number
    password: string
    last_login: string
    is_superuser: boolean
    username: string
    first_name: string
    last_name: string
    email: string
    is_staff: boolean
    is_active: boolean
    date_joined: string
    is_student: boolean
    is_tutor: boolean
    rights: number
    groups: []
    user_permissions: []
    departments: Array<Department>
}

export interface Room {
    departments: Array<number>
    id: number
    name: string
    subroom_of: Array<Room>
    types: Array<number>
    is_basic: boolean
    basic_rooms: Array<{ id: number; name: string }>
}

export interface RoomReservation {
    date: string
    description: string
    email: boolean
    end_time: string
    id: number
    responsible: number
    room: number
    reservation_type: number
    start_time: string
    title: string
    periodicity: number
}

export interface RoomReservationType {
    id: number
    name: string
    bg_color: string
}

export class Course {
    id: number
    week: string
    year: string
    no: number
    type: { department: { name: string }; name: string }
    room_type: { name: string }
    tutor: string
    supp_tutor: string
    groups: Array<{ name: string }>
    module: { abbrev: string }
    modulesupp: { abbrev: string }
    pay_module: { abbrev: string }

    constructor() {
        this.id = 0
        this.week = ''
        this.year = ''
        this.no = 0
        this.type = { department: { name: '' }, name: '' }
        this.room_type = { name: '' }
        this.tutor = ''
        this.supp_tutor = ''
        this.groups = []
        this.module = { abbrev: '' }
        this.modulesupp = { abbrev: '' }
        this.pay_module = { abbrev: '' }
    }
}

export class ScheduledCourse {
    id: number
    room: number
    start_time: number
    day: string
    course: {
        id: number
        type: string
        room_type: string
        week: number
        year: number
        groups: [
            {
                id: number
                train_prog: string
                name: string
                is_structural: boolean
            }
        ]
        supp_tutor: []
        module: {
            name: string
            abbrev: string
            display: {
                color_bg: string
                color_txt: string
            }
        }
        pay_module: object
        is_graded: boolean
    }
    tutor: string
    id_visio: number

    constructor() {
        this.id = 0
        this.room = 0
        this.start_time = 0
        this.day = ''
        this.course = {
            id: 0,
            type: '',
            room_type: '',
            week: 0,
            year: 0,
            groups: [
                {
                    id: 0,
                    train_prog: '',
                    name: '',
                    is_structural: false,
                },
            ],
            supp_tutor: [],
            module: {
                name: '',
                abbrev: '',
                display: {
                    color_bg: '',
                    color_txt: '',
                },
            },
            pay_module: {},
            is_graded: false,
        }
        this.tutor = ''
        this.id_visio = 0
    }
}

export interface CourseType {
    name: string
    duration: number
}

export interface CalendarDragEvent {
    startDate: Date
    startTime: Time
    endDate: Date
    endTime: Time
}

export interface CalendarProps {
    days: {
        [index: number]: {
            name: string
            date: string
        }
    }
    year: string
}

export interface HourCalendarProps extends CalendarProps {
    slots: {
        // The slot date formatted as yyyy-MM-dd
        [index: string]: Array<CalendarSlot>
    }
    startTime: number
    endTime: number
}

export interface RoomCalendarProps extends CalendarProps {
    slots: {
        // The slot date formatted as yyyy-MM-dd
        [index: string]: {
            // The room id
            [index: string]: Array<CalendarSlot>
        }
    }
    rooms: Array<Room>
}

export interface CalendarSlot {
    slotData: CalendarSlotData
    component: ShallowRef
    actions: CalendarSlotActions
}

export interface CalendarSlotActions {
    delete?(toDelete: CalendarSlotData): void

    save?(newValue: CalendarSlotData, oldValue?: CalendarSlotData): void
}

export interface CalendarSlotData {
    day: string
    startTime: Time
    endTime: Time
    title: string
    id: string
    displayStyle: object
}

export interface CalendarRoomReservationSlotData extends CalendarSlotData {
    reservation: RoomReservation
    rooms: { [roomId: number]: Room }
    reservationTypes: Array<RoomReservationType>
    users: { [userId: number]: User }
}

export interface CalendarScheduledCourseSlotData extends CalendarSlotData {
    course: ScheduledCourse
    department: string
    rooms: { [roomId: number]: Room }
}

export interface CalendarSlotInterface {
    openContextMenu: () => boolean
    closeContextMenu: () => void
}

export interface FormInterface {
    close: () => void
    addAlert: (level: string, message: string) => void
    dismissAlerts: () => void
}

export interface FormAlert {
    level: string // info | warning | danger | success
    message: string
}

export interface RoomAttribute {
    id: number
    name: string
    description: string
}

export interface RoomAttributeValue {
    id: number
    room: number
    attribute: number
}

export interface BooleanRoomAttributeValue extends RoomAttributeValue {
    value: boolean
}

export interface NumericRoomAttributeValue extends RoomAttributeValue {
    value: number
}

export interface DynamicSelectElementValue {
    id: number
    name: string
}

export interface DynamicSelectElementBooleanValue extends DynamicSelectElementValue {
    value: boolean
}

export interface DynamicSelectElementNumericValue extends DynamicSelectElementValue {
    initialMin: number
    initialMax: number
    min: number
    max: number
}
