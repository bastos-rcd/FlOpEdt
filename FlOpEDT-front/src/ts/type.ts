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

export interface FlopWeek {
  week: number
  year: number
}

export interface Preference {
  id: number
  type: string
  startTimeMinutes: number
  duration: number
  week: number
  day: string
  value: number
  year: number
  //dataId: number
  userName: string
}

export interface RoomAPI {
  id: number
  name: string
  is_basic: string
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
  room?: { id: number; name: string; is_basic: boolean }
  start_time: Date
  end_time: Date
  course: Course
  tutor: number
  id_visio: number

  constructor(
    id = 0,
    room = { id: 0, name: '', is_basic: true },
    start_time = '',
    end_time = '',
    course = new Course(),
    tutor = -1,
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

export interface TrainingProgrammeAPI {
  id: number
  abbrev: string
  name: string
}

export interface UserAPI {
  name: string
  id: number
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
  train_prog: string
}
export interface ModuleAPI {
  id: number
  abbrev: string
  name: string
}
