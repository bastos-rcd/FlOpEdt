import {
  Department,
  User,
  Course,
  CourseType,
  RoomAttribute,
  ScheduledCourse,
  TimeSettings,
  Group,
  Module,
} from '@/ts/type'
import type { Room } from '@/stores/declarations'

const API_ENDPOINT = '/fr/api/'

const urls = {
  getcurrentuser: 'user/getcurrentuser',
  getAllDepartments: 'fetch/alldepts',
  rooms: 'rooms/room',
  weekdays: 'fetch/weekdays',
  timesettings: 'base/timesettings',
  roomreservation: 'roomreservations/reservation',
  roomreservationtype: 'roomreservations/reservationtype',
  reservationperiodicity: 'roomreservations/reservationperiodicity',
  reservationperiodicitytype: 'roomreservations/reservationperiodicitytype',
  reservationperiodicitybyweek: 'roomreservations/reservationperiodicitybyweek',
  reservationperiodicityeachmonthsamedate: 'roomreservations/reservationperiodicityeachmonthsamedate',
  reservationperiodicitybymonth: 'roomreservations/reservationperiodicitybymonth',
  reservationperiodicitybymonthxchoice: 'roomreservations/reservationperiodicitybymonthxchoice',
  courses: 'courses/courses',
  scheduledcourses: 'fetch/new_api_scheduledcourses',
  coursetypes: 'courses/type',
  users: 'user/users',
  getTutors: 'user/tutor',
  booleanroomattributes: 'rooms/booleanattributes',
  numericroomattributes: 'rooms/numericattributes',
  booleanroomattributevalues: 'rooms/booleanattributevalues',
  numericroomattributevalues: 'rooms/numericattributevalues',
  weeks: 'base/weeks',
  getGroups: 'groups/structural',
  getModules: 'courses/module',
}

function getCookie(name: string) {
  return null
}

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

function buildUrl(base: string, uri: string) {
  return `${base}/${uri}`
}
export interface FlopAPI {
  getGroups(department?: Department): Promise<Group[]>
  getModules(department?: Department): Promise<Module[]>
  getCurrentUser(): Promise<User>
  getAllDepartments(): Promise<Array<Department>>
  getTutors(department?: Department): Promise<Array<User>>
  getTutorById(id: number): Promise<User>
  fetch: {
    booleanRoomAttributes(): Promise<Array<RoomAttribute>>
    courses(params: { week?: number; year?: number; department?: string }): Promise<Array<Course>>
    courseTypes(params: { department: string }): Promise<Array<CourseType>>
    numericRoomAttributes(): Promise<Array<RoomAttribute>>
    room(id: number): Promise<Room>
    rooms(params: { department: string }): Promise<Array<Room>>
    scheduledCourses(params: { week?: number; year?: number; department?: string }): Promise<Array<ScheduledCourse>>
    timeSettings(): Promise<Array<TimeSettings>>
    users(): Promise<Array<User>>
  }
  delete: {
    reservationPeriodicity(id: number): Promise<unknown>
    roomReservation(id: number): Promise<unknown>
  }
}

const api: FlopAPI = {
  async getGroups(department?: Department): Promise<Array<Group>> {
    let groups: Array<Group> = []
    let finalUrl: string = API_ENDPOINT + urls.getGroups
    if (department) finalUrl += '/?dept=' + department.abbrev
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
            groups = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return groups
  },
  async getModules(department?: Department): Promise<Array<Module>> {
    let modules: Array<Module> = []
    let finalUrl: string = API_ENDPOINT + urls.getModules
    if (department) finalUrl += '/?dept=' + department.abbrev
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
            modules = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return modules
  },
  async getTutors(department?: Department): Promise<Array<User>> {
    let tutors: Array<User> = []
    let finalUrl: string = API_ENDPOINT + urls.getTutors
    if (department) finalUrl += '/?dept=' + department.abbrev
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
            tutors = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return tutors
  },
  async getTutorById(id: number): Promise<User> {
    let tutor: User = new User()
    let finalUrl: string = API_ENDPOINT + urls.getTutors + '/?id=' + id
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
            tutor = data
          })
          .catch((error) => console.log('Error : ' + error.message))
      })
      .catch((error) => {
        console.log(error.message)
      })
    return tutor
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
    room(id: number, additionalParams?: object) {
      return fetcher(buildUrl(urls.rooms, id.toString()), additionalParams)
    },
    rooms(params: { department?: string }) {
      return fetcher(urls.rooms, params, [['department', 'dept']])
    },
    scheduledCourses(params: { week?: number; year?: number; department?: string }) {
      return fetcher(urls.scheduledcourses, params)
    },
    timeSettings() {
      return fetcher(urls.timesettings)
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
  // Paul: I comment out this, I don't know what it is supposed to do
  // if (csrfToken) {
  //   requestHeaders.set('X-CSRFToken', csrfToken)
  // }
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
