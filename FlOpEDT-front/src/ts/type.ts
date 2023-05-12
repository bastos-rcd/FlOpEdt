import { MappableToIdArray } from '@/stores/store'
import type { ComputedRef, Ref, ShallowRef } from 'vue'

export interface BooleanRoomAttributeValue extends RoomAttributeValue {
  value: boolean
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

export interface CalendarRoomReservationSlotData extends CalendarSlotData {
  reservation: RoomReservation
  rooms: { [roomId: number]: Room }
  reservationTypes: Array<RoomReservationType>
  users: { [userId: number]: User }
  periodicityTypes: Array<ReservationPeriodicityType>
  weekdays: Array<WeekDay>
  periodicity: ReservationPeriodicity | null
  onPeriodicityDelete: (reservation: RoomReservation) => Promise<void>
  dayStart: Time
  dayEnd: Time
}

export interface CalendarScheduledCourseSlotData extends CalendarSlotData {
  course: ScheduledCourse
  department: string
  rooms: { [roomId: number]: Room }
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
  startTime: Time
  endTime: Time
  title: string
  id: string
  displayStyle: object
}

export interface CalendarSlotInterface {
  openContextMenu: () => boolean
  closeContextMenu: () => void
}

export class Course {
  id: number
  type: {
    department: Department
    name: string
    duration: number
  }
  room_type: { name: string }
  week: string
  year: string
  groups: [
    {
      id: number
      train_prog: string
      name: string
      is_structural: boolean
    }
  ]
  no: number
  tutor: string
  supp_tutor: string
  module: {
    name: string
    abbrev: string
    display: {
      color_bg: string
      color_txt: string
    }
  }
  modulesupp: { abbrev: string }
  pay_module: { abbrev: string }
  is_graded: boolean

  constructor() {
    this.id = 0
    this.week = ''
    this.year = ''
    this.no = 0
    this.type = {
      department: new Department(),
      name: '',
      duration: 0,
    }
    this.room_type = { name: '' }
    this.tutor = ''
    this.supp_tutor = ''
    this.groups = [
      {
        id: -1,
        train_prog: '',
        name: '',
        is_structural: false,
      },
    ]
    this.module = {
      name: '',
      abbrev: '',
      display: {
        color_bg: '',
        color_txt: '',
      },
    }
    this.modulesupp = { abbrev: '' }
    this.pay_module = { abbrev: '' }
    this.is_graded = false
  }
}

export interface CourseType {
  name: string
  duration: number
}

export interface Department {
  id: number
  name: string
  abbrev: string
}

export class Department implements Department {
  id = -1
  abbrev = 'NF'
  name = 'not found'

  constructor(id: number = -1, abbrev: string = 'NF', name = 'not found') {
    this.id = id
    this.abbrev = abbrev
    this.name = name
  }
}

export interface DialogInterface {
  close: () => void
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

export interface DynamicSelectElementValue {
  id: number
  name: string
}

export interface FlopWeek {
  week: number
  year: number
}

export interface FormAlert {
  level: string // info | warning | danger | success
  message: string
}

export interface FormInterface {
  close: () => void
  addAlert: (level: string, message: string) => void
  dismissAlerts: () => void
}

export interface HourCalendarProps extends CalendarProps {
  slots: {
    // The slot date formatted as yyyy-MM-dd
    [index: string]: Array<CalendarSlot>
  }
  startTime: number
  endTime: number
}

export interface NumericRoomAttributeValue extends RoomAttributeValue {
  value: number
}

export interface ReservationPeriodicity {
  periodicity: ReservationPeriodicityData
}

export interface ReservationPeriodicityByMonth extends ReservationPeriodicityData {
  bm_x_choice: number
  bm_day_choice: string
}

export type ReservationPeriodicityByMonthXChoice = [number, string]

export interface ReservationPeriodicityByWeek extends ReservationPeriodicityData {
  bw_weekdays: Array<string>
  bw_weeks_interval: number
}

export interface ReservationPeriodicityData {
  id: number
  start: string
  end: string
  periodicity_type: ReservationPeriodicityTypeName | ''
}

export type ReservationPeriodicityEachMonthSameDate = ReservationPeriodicityData

export type ReservationPeriodicityType = [ReservationPeriodicityTypeName, string]

export type ReservationPeriodicityTypeName = 'BM' | 'BW' | 'EM'

export interface RoomAPI {
  departments: Array<number>
  id: number
  name: string
  subroom_of: Array<number>
  is_basic: boolean
  basic_rooms: Array<{ id: number; name: string }>
}

export interface Room {
  departments: Array<Department>
  id: number
  name: string
  subroom_of: MappableToIdArray<Room>
  is_basic: boolean
  basic_rooms: Array<{ id: number; name: string }>
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
  periodicity: ReservationPeriodicity | null
  create_repetitions?: boolean
}

export interface RoomReservationType {
  id: number
  name: string
  bg_color: string
}

export class ScheduledCourse {
  id: number
  room?: { id: number; name: string; is_basic: boolean }
  start_time: Date
  end_time: Date
  course: Course
  tutor: string
  id_visio: number

  constructor(
    id = 0,
    room = { id: 0, name: '', is_basic: true },
    start_time = '',
    end_time = '',
    course = new Course(),
    tutor = '',
    id_visio = 0
  ) {
    this.id = id
    this.room = room
    this.start_time = new Date(start_time)
    this.end_time = new Date(end_time)
    this.course = course
    this.tutor = tutor
    this.id_visio = id_visio
  }
}

export interface ScheduledCourses {
  perDepartment: Ref<{ [departmentId: string]: Array<ScheduledCourse> }>
  perDepartmentFilterByDepartmentsAndRooms: ComputedRef<{ [departmentId: string]: Array<ScheduledCourse> }>
  perDay: ComputedRef<{ [day: string]: Array<ScheduledCourse> }>
  perDayPerRoomFilterBySelectedDepartments: ComputedRef<{
    [day: string]: { [roomId: string]: Array<ScheduledCourse> }
  }>
  perDayPerRoom: ComputedRef<{
    [day: string]: { [roomId: string]: Array<ScheduledCourse> }
  }>
}

export class Time {
  value: number
  text: string

  constructor(value: number, text: string) {
    this.value = value
    this.text = text
  }
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

export interface User {
  username: string
  first_name: string
  last_name: string
  email: string
  id: number
}

export class User implements User {
  username = ''
  first_name = ''
  last_name = 'AnonymousUser'
  email = ''
  id = -1
}

export interface UserD {
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

export interface WeekDay {
  date: string
  name: string
  num: number
  ref: string
}

export interface Group {
  pouet: string
}
export interface Module {
  tut: string
}
