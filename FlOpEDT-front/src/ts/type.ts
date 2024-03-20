import { TimestampOrNull, parseTimestamp } from '@quasar/quasar-ui-qcalendar'

export interface AvailabilityBack {
  av_type: string
  start_time: TimestampOrNull
  duration: string
  value: number
  dataId: number
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

  constructor(id: number = -1, abbrev: string = '', name = '') {
    this.id = id
    this.abbrev = abbrev
    this.name = name
  }
}

export interface FlopWeek {
  week: number
  year: number
}

export interface RoomAPI {
  id: number
  name: string
  over_room_ids: number[]
  department_ids: number[]
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

export class ScheduledCourse {
  id: number
  roomId: number
  start_time: TimestampOrNull
  end_time: TimestampOrNull
  courseId: number
  tutor: number
  id_visio: number
  moduleId: number
  trainProgId: number
  groupIds: number[]
  suppTutorsIds: number[]
  courseTypeId: number
  no: number

  constructor(
    id = -1,
    room = -1,
    start_time = '',
    end_time = '',
    courseId = -1,
    tutor = -1,
    id_visio = -1,
    moduleId = -1,
    trainProgId = -1,
    groupIds = [],
    suppTutorsIds = [],
    courseTypeId = -1,
    no = -1
  ) {
    this.id = id
    this.roomId = room
    this.start_time = parseTimestamp(start_time)
    this.end_time = parseTimestamp(end_time)
    this.courseId = courseId
    this.tutor = tutor
    this.id_visio = id_visio
    this.moduleId = moduleId
    this.trainProgId = trainProgId
    this.groupIds = groupIds
    this.suppTutorsIds = suppTutorsIds
    this.courseTypeId = courseTypeId
    this.no = no
  }
}

export interface StartTime {
  id: number
  departmentId: number
  duration: number
  allowedStartTimes: number[]
}

export interface TimeSettingBack {
  id: number
  day_start_time: string
  day_end_time: string
  morning_end_time: string
  afternoon_start_time: string
  days: Array<string>
  scheduling_period_mode: string
  department: number
}

export interface TrainingProgrammeAPI {
  id: number
  abbrev: string
  name: string
  department_id: number
}

export interface UserAPI {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  rights: number
  departments: Array<{ department_id: number; is_admin: string }>
}

export interface User {
  username: string
  firstname: string
  lastname: string
  email: string
  id: number
}

export class User implements User {
  username = ''
  firstname = ''
  lastname = 'AnonymousUser'
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

export interface GroupAPI {
  id: number
  name: string
  train_prog_id: number
  type_id: number
  parent_groups?: number[]
  conflicting_groups?: number[]
  parallel_groups?: number[]
}
export interface ModuleAPI {
  id: number
  abbrev: string
  name: string
  head_id: number
  url: string
  train_prog_id: number
  training_period_id: number
}
