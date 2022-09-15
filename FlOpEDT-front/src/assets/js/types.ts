export interface FlopWeek {
  week: number,
  year: number,
}

export interface TimeSettings {
  'id': number,
  'day_start_time': number,
  'day_finish_time': number,
  'lunch_break_start_time': number,
  'lunch_break_finish_time': number,
  'days': Array<string>,
  'default_preference_duration': number,
  'department': number
}

export class Time {
  value: number
  text: string

  constructor (value: number, text: string) {
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
  id: number,
  abbrev: string,
}

export class Room {
  departments: Array<number>
  id: number
  name: string
  subroom_of: Array<Room>
  types: Array<number>

  constructor () {
    this.departments = []
    this.id = 0
    this.name = ''
    this.subroom_of = []
    this.types = []
  }
}

export interface RoomReservation {
  date: string
  description: string
  email: boolean
  end_time: string
  id: number
  responsible: string
  room: number
  type: number
  start_time: string
  title: string
  with_key: boolean
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
  type: { department: { name: string }, name: string }
  room_type: { name: string }
  tutor: string
  supp_tutor: string
  groups: Array<{ name: string }>
  module: { abbrev: string }
  modulesupp: { abbrev: string }
  pay_module: { abbrev: string }

  constructor () {
    this.id = 0
    this.week = ''
    this.year = ''
    this.no = 0
    this.type = {department: {name: ''}, name: ''}
    this.room_type = {name: ''}
    this.tutor = ''
    this.supp_tutor = ''
    this.groups = []
    this.module = {abbrev: ''}
    this.modulesupp = {abbrev: ''}
    this.pay_module = {abbrev: ''}
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

  constructor () {
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

export interface CalendarSlot {
  data: CalendarSlotData
  component: any
}

export interface CalendarSlotData {
  startTime: Time
  endTime: Time
  title: string
  id: string
  displayStyle: object
}

export interface CalendarRoomReservationSlotData extends CalendarSlotData {
  reservation: RoomReservation
}

export interface CalendarScheduledCourseSlotData extends CalendarSlotData {
  course: ScheduledCourse
  department: string
}

export interface CalendarSlotInterface {
  openContextMenu: () => boolean,
  closeContextMenu: () => void,
}