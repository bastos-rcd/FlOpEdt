import {
  Department,
  User,
  UserAPI,
  Course,
  CourseType,
  RoomAttribute,
  ScheduledCourse,
  RoomAPI,
  GroupAPI,
  ModuleAPI,
  TrainingProgrammeAPI,
  AvailabilityBack,
  TimeSettingBack,
} from '@/ts/type'

import { dateToString, buildUrl } from '@/helpers'
import { TimeSetting } from '@/stores/declarations'
import { parseTime } from '@quasar/quasar-ui-qcalendar'

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
  getModules: 'v1/base/courses/modules',
  getTrainProgs: 'v1/base/groups/training_programmes',
  getAvailability: 'v1/availability/user',
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

async function fetchData(url: string, params: { [k: string]: any }) {
  const providedParams = params
  console.log('providedParams: ', providedParams)
  params = Object.assign(
    {
      method: 'GET',
      credentials: 'same-origin',
    },
    params
  )

  params.headers = Object.assign(
    {
      'Content-Type': 'application/json',
    },
    params.headers
  )

  let args = ''

  if (providedParams) {
    args = Object.keys(providedParams)
      .map((p) => p + '=' + providedParams[p])
      .join('&')
  }
  const finalUrl = `${API_ENDPOINT}${url}/?${args}`
  console.log(`Fetching ${finalUrl}...`)

  const response = await fetch(finalUrl, params)
  const json = (await response.json()) || {}
  if (!response.ok) {
    const errorMessage = json.error || `${response.status}`
    throw new Error(errorMessage)
  }
  return json
}

/**
 * Proxy function to fetch from the api.
 * @param {string} url The url to access the data
 * @param {object} params1 Manually given parameters
 * @param {object} params2 Object-format given parameters
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params1?: object, params2?: object) => fetchData(url, { ...params1, ...params2 })

/**
 * Accepts an object and returns a new object with undefined values removed.
 * The object keys can be renamed using the renameList parameter.
 * @param obj The object to filter
 * @param renameList The rename list as an array of pair of strings as [oldName, newName]
 */
function filterObject(obj: { [key: string]: any }, renameList?: Array<[oldName: string, newName: string]>) {
  let filtered = Object.entries(obj).filter((entry) => entry[1])
  if (renameList) {
    filtered = filtered.map((entry: [string, any]) => {
      const toRename = renameList.find((renamePair) => renamePair[0] === entry[0])
      const keyName = toRename ? toRename[1] : entry[0]
      return [keyName, entry[1]]
    })
  }
  return Object.fromEntries(filtered)
}

const fetcher2 = (url: string, params?: object, renameList?: Array<[string, string]>) =>
  fetchData(url, params ? filterObject(params, renameList) : {})

export interface FlopAPI {
  getScheduledCourses(from?: Date, to?: Date, department_id?: number, tutor?: number): Promise<Array<ScheduledCourse>>
  getStructuralGroups(department?: string): Promise<GroupAPI[]>
  getTransversalGroups(department?: string): Promise<GroupAPI[]>
  getModules(): Promise<ModuleAPI[]>
  getCurrentUser(): Promise<User>
  getAllDepartments(): Promise<Array<Department>>
  getTutors(id?: Number): Promise<Array<UserAPI>>
  getTrainProgs(department?: string): Promise<TrainingProgrammeAPI[]>
  getAllRooms(department?: Department): Promise<Array<RoomAPI>>
  getRoomById(id: number): Promise<RoomAPI | undefined>
  getAvailabilities(userId: number, from: Date, to: Date): Promise<Array<AvailabilityBack>>
  getTimeSettings(): Promise<any[]>
  fetch: {
    booleanRoomAttributes(): Promise<Array<RoomAttribute>>
    courses(params: { week?: number; year?: number; department?: string }): Promise<Array<Course>>
    courseTypes(params: { department: string }): Promise<Array<CourseType>>
    numericRoomAttributes(): Promise<Array<RoomAttribute>>
    scheduledCourses(params: { week?: number; year?: number; department?: string }): Promise<Array<ScheduledCourse>>
    users(): Promise<Array<User>>
  }
  delete: {
    reservationPeriodicity(id: number): Promise<unknown>
    roomReservation(id: number): Promise<unknown>
  }
}

const api: FlopAPI = {
  async getScheduledCourses(
    from?: Date,
    to?: Date,
    department_id?: number,
    tutor?: number
  ): Promise<Array<ScheduledCourse>> {
    let scheduledCourses: Array<ScheduledCourse> = []
    let context = new Map<string, any>([['dept_id', department_id]])
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
          .then((data) => {
            data.forEach((d: any) => {
              const sc: ScheduledCourse = {
                id: d.id,
                roomId: d.room_id,
                start_time: new Date(d.start_time),
                end_time: new Date(d.end_time),
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
            })
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
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
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
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
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return groups
  },
  async getTrainProgs(department?: string): Promise<TrainingProgrammeAPI[]> {
    let trainProgs: Array<TrainingProgrammeAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getTrainProgs
    if (department) finalUrl += '/?dept=' + department
    await fetch(API_ENDPOINT + urls.getTrainProgs, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
    }).then(async (response) => {
      if (!response.ok) {
        throw Error('Error : ' + response.status)
      }
      await response.json().then((data) => {
        trainProgs = data
      })
    })
    return trainProgs
  },
  async getModules(): Promise<Array<ModuleAPI>> {
    let modules: Array<ModuleAPI> = []
    let finalUrl: string = API_ENDPOINT + urls.getModules
    //if (department) finalUrl += '/?dept=' + department.abbrev
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
          .then((data: any) => {
            modules = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return modules
  },
  async getTutors(id?: number): Promise<Array<UserAPI>> {
    let tutors: Array<UserAPI> = []
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
          .then((data) => {
            if (id) tutors.push(data)
            else {
              data.forEach((d: UserAPI) => tutors.push(d))
            }
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
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
          .then((data) => {
            user = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
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
          .then((data) => {
            departments = data
          })
          .catch((error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error) => {
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
          .catch((error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error) => {
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
            .then((data) => {
              room = data
            })
            .catch((error) => {
              return Promise.reject(error.message)
            })
        })
        .catch((error) => {
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
          .then((data) => {
            data.forEach((avail: any) => {
              availabilities.push({
                av_type: avail.subject_type,
                start_time: avail.start_time,
                duration: avail.duration,
                dataId: userId,
                value: avail.value,
              })
            })
          })
          .catch((error) => {
            return Promise.reject(error.message)
          })
      })
      .catch((error) => {
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
  fetch: {
    booleanRoomAttributes() {
      return fetcher(urls.booleanroomattributes)
    },
    courses(params: { week?: number; year?: number; department?: string }) {
      return fetcher2(urls.courses, params, [['department', 'dept']])
    },
    courseTypes(params: { department: string }) {
      return fetcher2(urls.coursetypes, params, [['department', 'dept']])
    },
    numericRoomAttributes() {
      return fetcher(urls.numericroomattributes)
    },
    scheduledCourses(params: { week?: number; year?: number; department?: string }) {
      return fetcher(urls.scheduledcourses, params)
    },
    users() {
      return fetcher(urls.users)
    },
  },
  delete: {
    reservationPeriodicity(id: number): Promise<unknown> {
      return deleteData(urls.reservationperiodicity, id)
    },
    roomReservation(id: number): Promise<unknown> {
      return deleteData(urls.roomreservation, id)
    },
  },
}

/****************************************/
/*            David's Code             */
/****************************************/

async function sendData<T>(method: string, url: string, optional: { data?: unknown; id?: number }): Promise<T | never> {
  if (!['PUT', 'POST', 'DELETE', 'PATCH'].includes(method)) {
    return Promise.reject('Method must be either PUT, POST, PATCH, or DELETE')
  }

  // Setup headers
  const requestHeaders: HeadersInit = new Headers()
  requestHeaders.set('Content-Type', 'application/json')
  console.log('optional : ', optional)
  console.log('method : ', method)
  console.log('url :', url)
  if (csrfToken) {
    requestHeaders.set('X-CSRFToken', csrfToken)
  }
  // Setup request
  const requestInit: RequestInit = {
    method: method,
    credentials: 'same-origin',
    headers: requestHeaders,
  }
  if (optional.data) {
    requestInit.body = JSON.stringify(optional.data)
  }

  // Create url
  let endUrl = '/'
  if (optional.id) {
    endUrl = `/${optional.id}/`
  }
  const finalUrl = `${API_ENDPOINT}${url}${endUrl}`
  console.log(`Updating ${finalUrl}...`)

  // Wait for the response
  return await fetch(finalUrl, requestInit)
    .then(async (response) => {
      const data = await response.json()
      if (!response.ok) {
        const error = data || `Error ${response.status}: ${response.statusText}`
        return Promise.reject(error)
      }
      return data
    })
    .catch((reason) => {
      return Promise.reject(reason)
    })
}

async function patchData<T>(url: string, id: number, data: unknown): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    id: id,
    data: data,
  }
  return await sendData('PATCH', url, optional)
}

export async function useFetch<T>(url: string, filters: Partial<T>) {
  const requestInit = createRequestHeader('GET')

  let args = ''

  if (filters) {
    type ObjectKey = keyof typeof filters

    args = Object.keys(filters)
      .map((p) => p + '=' + filters[p as ObjectKey])
      .join('&')
  }
  const finalUrl = `${API_ENDPOINT}${url}/?${args}`
  console.log(`Fetching ${finalUrl}...`)

  return doFetch(finalUrl, requestInit)
}

export function usePut<T>(url: string, id: number, data: T): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    id: id,
    data: data,
  }
  return sendData('PUT', url, optional)
}

export function usePost<T>(url: string, data: T): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    data: data,
  }
  return sendData('POST', url, optional)
}

export function usePatch<T>(url: string, id: number, data: Partial<T>): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    id: id,
    data: data,
  }
  return sendData('PATCH', url, optional)
}

async function doFetch(url: string, requestInit: RequestInit) {
  return await fetch(url, requestInit)
    .then(async (response) => {
      const data = await response.json()
      if (!response.ok) {
        const error = data || `Error ${response.status}: ${response.statusText}`
        return Promise.reject(error)
      }
      return data
    })
    .catch((reason) => {
      return Promise.reject(reason)
    })
}

function createRequestHeader(method: string): RequestInit {
  // Setup headers
  const requestHeaders: HeadersInit = new Headers()
  requestHeaders.set('Content-Type', 'application/json')

  // Setup request
  return {
    method: method,
    credentials: 'same-origin',
    headers: requestHeaders,
  }
}

async function putData<T>(url: string, id: number, data: unknown): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    id: id,
    data: data,
  }
  return await sendData('PUT', url, optional)
}

async function postData<T>(url: string, data: unknown): Promise<T | never> {
  const optional: { [key: string]: unknown } = {
    data: data,
  }
  return await sendData('POST', url, optional)
}

function deleteData(url: string, id: number) {
  const optional: { [key: string]: unknown } = {
    id: id,
  }
  return sendData('DELETE', url, optional)
}
export { api }
