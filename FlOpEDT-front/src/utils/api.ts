import {
  Department,
  User,
  UserAPI,
  ScheduledCourse,
  RoomAPI,
  GroupAPI,
  ModuleAPI,
  TrainingProgrammeAPI,
  AvailabilityBack,
  TimeSettingBack,
  StartTime,
} from '@/ts/type'

import { dateToString, buildUrl, durationDjangoToMinutes } from '@/helpers'
import { TimeSetting } from '@/stores/declarations'
import { parseTime, parseTimestamp } from '@quasar/quasar-ui-qcalendar'

const API_ENDPOINT = '/fr/api/'

const urls = {
  getcurrentuser: 'v1/people/getcurrentuser',
  getAllDepartments: 'v1/base/groups/department',
  getScheduledcourses: 'v1/base/courses/scheduled_courses',
  getRooms: 'v1/base/courses/rooms',
  weekdays: 'fetch/weekdays',
  getTimeSettings: 'base/timesettings',
  roomreservation: 'roomreservations/reservation',
  roomreservationtype: 'roomreservations/reservationtype',
  reservationperiodicity: 'roomreservations/reservationperiodicity',
  reservationperiodicitytype: 'roomreservations/reservationperiodicitytype',
  reservationperiodicitybyweek: 'roomreservations/reservationperiodicitybyweek',
  reservationperiodicityeachmonthsamedate: 'roomreservations/reservationperiodicityeachmonthsamedate',
  reservationperiodicitybymonth: 'roomreservations/reservationperiodicitybymonth',
  reservationperiodicitybymonthxchoice: 'roomreservations/reservationperiodicitybymonthxchoice',
  courses: 'courses/courses',
  scheduledcourses: 'v1/base/courses/scheduledcourses',
  coursetypes: 'courses/type',
  users: 'user/users',
  getTutors: 'v1/people/tutors',
  booleanroomattributes: 'rooms/booleanattributes',
  numericroomattributes: 'rooms/numericattributes',
  booleanroomattributevalues: 'rooms/booleanattributevalues',
  numericroomattributevalues: 'rooms/numericattributevalues',
  weeks: 'base/weeks',
  getGroups: 'v1/base/groups/structural_groups',
  getTransversalGroups: 'v1/base/groups/transversal_groups',
  getModules: 'v1/base/courses/module',
  getTrainProgs: 'v1/base/groups/training_programmes',
  getAvailability: 'v1/availability/user',
  getStartTimes: 'v1/constraint/base/course_start_time',
}

function getCookie(name: string) {
  if (!document.cookie) {
    return null
  }
  const xsrfCookies = document.cookie
    .split(';')
    .map((c) => c.trim())
    .filter((c) => c.startsWith(name + '='))

  if (xsrfCookies.length === 0) {
    return null
  }
  return decodeURIComponent(xsrfCookies[0].split('=')[1])
}

const csrfToken = getCookie('csrftoken')

console.log('csrfToken retrieved: ', csrfToken)

interface FlopAPI {
  getScheduledCourses(from?: Date, to?: Date, department_id?: number, tutor?: number): Promise<Array<ScheduledCourse>>
  getStructuralGroups(department?: string): Promise<GroupAPI[]>
  getTransversalGroups(department?: string): Promise<GroupAPI[]>
  getModules(): Promise<ModuleAPI[]>
  getCurrentUser(): Promise<User>
  getAllDepartments(): Promise<Array<Department>>
  getTutors(id?: number): Promise<Array<UserAPI>>
  getTrainProgs(department?: string): Promise<TrainingProgrammeAPI[]>
  getAllRooms(department?: Department): Promise<Array<RoomAPI>>
  getRoomById(id: number): Promise<RoomAPI | undefined>
  getAvailabilities(userId: number, from: Date, to: Date): Promise<Array<AvailabilityBack>>
  getTimeSettings(): Promise<TimeSetting[]>
  getStartTimes(deptId?: number): Promise<StartTime[]>
}

export const api: FlopAPI = {
  async getScheduledCourses(
    from?: Date,
    to?: Date,
    department_id?: number,
    tutor?: number
  ): Promise<Array<ScheduledCourse>> {
    const scheduledCourses: Array<ScheduledCourse> = []
    const context = new Map<string, string | number | undefined | null>([['dept_id', department_id]])
    if (from) {
      context.set('from_date', dateToString(from))
    }
    if (to) {
      context.set('to_date', dateToString(to))
    }
    if (tutor !== -1) {
      context.set('tutor_name', tutor)
    }
    const finalUrl = buildUrl(API_ENDPOINT + urls.getScheduledcourses + '/', context)
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then(
            (
              data: {
                id: number
                room_id: number
                start_time: string
                end_time: string
                course_id: number
                tutor_id: number
                module_id: number
                train_prog_id: number
                number: number
                course_type_id: number
                supp_tutor_ids: number[]
                group_ids: number[]
              }[]
            ) => {
              data.forEach(
                (d: {
                  id: number
                  room_id: number
                  start_time: string
                  end_time: string
                  course_id: number
                  tutor_id: number
                  module_id: number
                  train_prog_id: number
                  number: number
                  course_type_id: number
                  supp_tutor_ids: number[]
                  group_ids: number[]
                }) => {
                  const sc: ScheduledCourse = {
                    id: d.id,
                    roomId: d.room_id,
                    start_time: parseTimestamp(d.start_time),
                    end_time: parseTimestamp(d.end_time),
                    courseId: d.course_id,
                    tutor: d.tutor_id,
                    id_visio: -1,
                    moduleId: d.module_id,
                    trainProgId: d.train_prog_id,
                    groupIds: [],
                    suppTutorsIds: [],
                    no: d.number,
                    courseTypeId: d.course_type_id,
                  }
                  d.supp_tutor_ids.forEach((sti: number) => {
                    sc.suppTutorsIds.push(sti)
                  })
                  d.group_ids.forEach((gId: number) => {
                    sc.groupIds.push(gId)
                  })
                  scheduledCourses.push(sc)
                }
              )
            }
          )
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return scheduledCourses
  },
  async getStructuralGroups(department?: string): Promise<Array<GroupAPI>> {
    let groups: Array<GroupAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getGroups
    if (department) finalUrl += '?dept=' + department
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then((data: GroupAPI[]) => {
            groups = data
          })
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return groups
  },
  async getTransversalGroups(department?: string): Promise<GroupAPI[]> {
    let groups: Array<GroupAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getTransversalGroups
    if (department) finalUrl += '?dept=' + department
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then((data: GroupAPI[]) => {
            groups = data
          })
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return groups
  },
  async getTrainProgs(department?: string): Promise<TrainingProgrammeAPI[]> {
    let trainProgs: Array<TrainingProgrammeAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getTrainProgs
    if (department) finalUrl += '/?dept=' + department
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    }).then(async (response) => {
      if (!response.ok) {
        throw Error('Error : ' + response.status)
      }
      await response.json().then((data: TrainingProgrammeAPI[]) => {
        trainProgs = data
      })
    })
    return trainProgs
  },
  async getModules(): Promise<Array<ModuleAPI>> {
    let modules: Array<ModuleAPI> = []
    const finalUrl: string = API_ENDPOINT + urls.getModules
    // if (department_id) finalUrl += '/?dept_id=' + department_id
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then((data: ModuleAPI[]) => {
            modules = data
          })
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return modules
  },
  async getTutors(id?: number): Promise<Array<UserAPI>> {
    const tutors: Array<UserAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getTutors
    if (id) finalUrl += '/' + id
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then((data: UserAPI[] | UserAPI) => {
            if (id) tutors.push(data as UserAPI)
            else if (Array.isArray(data)) {
              data.forEach((d: UserAPI) => tutors.push(d))
            }
          })
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return tutors
  },
  async getCurrentUser(): Promise<User> {
    let user: User = new User()
    await fetch(API_ENDPOINT + urls.getcurrentuser, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw Error('Error : ' + response.status)
        }
        await response
          .json()
          .then((data: User) => {
            user = data
          })
          .catch((error: Error) => console.log('Error : ' + error.message))
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return user
  },
  async getAllDepartments(): Promise<Array<Department>> {
    let departments: Array<Department> = []
    await fetch(API_ENDPOINT + urls.getAllDepartments, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
        }
        await response
          .json()
          .then((data: Department[]) => {
            departments = data
          })
          .catch((error: Error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return departments
  },
  async getAllRooms(department?: Department): Promise<Array<RoomAPI>> {
    let rooms: Array<RoomAPI> = []
    let finalUrl = API_ENDPOINT + urls.getRooms
    if (department) finalUrl += '/?dept=' + department?.abbrev
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    })
      .then(async (response) => {
        if (!response.ok) {
          return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
        }
        await response
          .json()
          .then((data: RoomAPI[]) => {
            rooms = data
          })
          .catch((error: Error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return rooms
  },
  async getRoomById(id: number): Promise<RoomAPI | undefined> {
    let room: RoomAPI | undefined
    if (id) {
      await fetch(API_ENDPOINT + urls.getRooms + '/' + id, {
        method: 'GET',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
      })
        .then(async (response) => {
          if (!response.ok) {
            return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
          }
          await response
            .json()
            .then((data: RoomAPI) => {
              room = data
            })
            .catch((error: Error) => {
              return Promise.reject(error.message)
            })
        })
        .catch((error: Error) => {
          console.log(error.message)
        })
    }
    return room
  },
  async getAvailabilities(userId: number, from: Date, to: Date): Promise<Array<AvailabilityBack>> {
    const availabilities: AvailabilityBack[] = []
    await fetch(
      API_ENDPOINT +
        urls.getAvailability +
        '/?user_id=' +
        userId +
        '&from_date=' +
        dateToString(from) +
        '&to_date=' +
        dateToString(to),
      {
        method: 'GET',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
      }
    )
      .then(async (response) => {
        if (!response.ok) {
          return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
        }
        await response
          .json()
          .then(
            (
              data: {
                subject_type: string
                start_time: string
                duration: string
                userId: number
                value: number
              }[]
            ) => {
              data.forEach((avail) => {
                availabilities.push({
                  av_type: avail.subject_type,
                  start_time: parseTimestamp(avail.start_time),
                  duration: avail.duration,
                  dataId: userId,
                  value: avail.value,
                })
              })
            }
          )
          .catch((error: Error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error: Error) => {
        console.log(error.message)
      })
    return availabilities
  },
  async getTimeSettings(): Promise<TimeSetting[]> {
    const timeSettings: TimeSetting[] = []
    await fetch(API_ENDPOINT + urls.getTimeSettings, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    }).then(async (response) => {
      if (!response.ok) {
        return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
      }
      await response.json().then((data: TimeSettingBack[]) => {
        data.forEach((timeSettingBack: TimeSettingBack) => {
          timeSettings.push({
            id: timeSettingBack.id,
            dayStartTime: parseTime(timeSettingBack.day_start_time),
            dayEndTime: parseTime(timeSettingBack.day_end_time),
            morningEndTime: parseTime(timeSettingBack.morning_end_time),
            afternoonStartTime: parseTime(timeSettingBack.afternoon_start_time),
            days: timeSettingBack.days,
            departmentId: timeSettingBack.department,
          })
        })
      })
    })
    return timeSettings
  },
  async getStartTimes(deptId?: number): Promise<StartTime[]> {
    const startTimes: StartTime[] = []
    let finalUrl = API_ENDPOINT + urls.getStartTimes
    if (deptId) finalUrl += '/?department_id=' + deptId
    await fetch(finalUrl, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    }).then(async (response) => {
      if (!response.ok) {
        return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
      }
      await response.json().then(
        (
          data: {
            id: number
            department_id: number
            duration: string
            allowed_start_times: string[]
          }[]
        ) => {
          data.forEach((allowedStartTime) => {
            startTimes.push({
              id: allowedStartTime.id,
              departmentId: allowedStartTime.department_id,
              duration: durationDjangoToMinutes(allowedStartTime.duration),
              allowedStartTimes: allowedStartTime.allowed_start_times.map((ast: string) =>
                durationDjangoToMinutes(ast)
              ),
            })
          })
        }
      )
    })
    return startTimes
  },
}
