import type {
    BooleanRoomAttributeValue,
    Course,
    CourseType,
    NumericRoomAttributeValue,
    ReservationPeriodicity,
    ReservationPeriodicityByMonth,
    ReservationPeriodicityByMonthXChoice,
    ReservationPeriodicityByWeek,
    ReservationPeriodicityEachMonthSameDate,
    ReservationPeriodicityType,
    RoomAttribute,
    RoomReservation,
    RoomReservationType,
    ScheduledCourse,
    TimeSettings,
    User,
    WeekDay,
} from '@/assets/js/types'
import type { Department } from '@/stores/department'
import type { Room } from '@/stores/room'

let API_ENDPOINT = ''

const dbDataElement = document.getElementById('json_data')
if (dbDataElement && dbDataElement.textContent) {
    const data = JSON.parse(dbDataElement.textContent)
    if ('api' in data) {
        API_ENDPOINT = data.api
    }
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

async function fetchData(url: string, params: { [k: string]: any }) {
    const providedParams = params

    params = Object.assign(
        {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
        },
        params
    )

    params.headers = Object.assign(
        {
            'X-CSRFToken': csrfToken,
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

async function sendData<T>(method: string, url: string, optional: { data?: unknown; id?: number }): Promise<T | never> {
    if (!['PUT', 'POST', 'DELETE', 'PATCH'].includes(method)) {
        return Promise.reject('Method must be either PUT, POST, PATCH, or DELETE')
    }

    // Setup headers
    const requestHeaders: HeadersInit = new Headers()
    requestHeaders.set('Content-Type', 'application/json')

    if (csrfToken) {
        requestHeaders.set('X-CSRFToken', csrfToken)
    }

    // Setup request
    const requestInit: RequestInit = {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: requestHeaders,
        redirect: 'follow',
        referrerPolicy: 'same-origin',
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

async function patchData<T>(url: string, id: number, data: unknown): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        id: id,
        data: data,
    }
    return await sendData('PATCH', url, optional)
}

function deleteData(url: string, id: number) {
    const optional: { [key: string]: unknown } = {
        id: id,
    }
    return sendData('DELETE', url, optional)
}

const urls = {
    departments: 'fetch/alldepts',
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
    scheduledcourses: 'fetch/scheduledcourses',
    coursetypes: 'courses/type',
    users: 'user/users',
    booleanroomattributes: 'rooms/booleanattributes',
    numericroomattributes: 'rooms/numericattributes',
    booleanroomattributevalues: 'rooms/booleanattributevalues',
    numericroomattributevalues: 'rooms/numericattributevalues',
}

/**
 * Proxy function to fetch from the api. Provided parameters' name can be mapped to another to fit the api names.
 * @param {string} url The url to access the data
 * @param params The parameters
 * @param renameList The rename
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params?: object, renameList?: Array<[string, string]>) =>
    fetchData(url, params ? filterObject(params, renameList) : {})

function buildUrl(base: string, uri: string) {
    return `${base}/${uri}`
}

export interface FlopAPI {
    fetch: {
        booleanRoomAttributes(): Promise<Array<RoomAttribute>>
        booleanRoomAttributeValues(): Promise<Array<BooleanRoomAttributeValue>>
        courses(params: { week?: number; year?: number; department?: string }): Promise<Array<Course>>
        courseTypes(params: { department: string }): Promise<Array<CourseType>>
        departments(): Promise<Array<Department>>
        numericRoomAttributes(): Promise<Array<RoomAttribute>>
        numericRoomAttributeValues(): Promise<Array<NumericRoomAttributeValue>>
        reservationPeriodicities(): Promise<Array<ReservationPeriodicity>>
        reservationPeriodicity(id: number): Promise<ReservationPeriodicity>
        reservationPeriodicityByMonthXChoices(): Promise<Array<ReservationPeriodicityByMonthXChoice>>
        reservationPeriodicityTypes(): Promise<Array<ReservationPeriodicityType>>
        room(id: number): Promise<Room>
        rooms(params: { department: string }): Promise<Array<Room>>
        roomReservations(params: {
            week?: number
            year?: number
            roomId?: number
            periodicityId?: number
        }): Promise<Array<RoomReservation>>
        roomReservationTypes(): Promise<Array<RoomReservationType>>
        scheduledCourses(params: { week?: number; year?: number; department?: string }): Promise<Array<ScheduledCourse>>
        timeSettings(): Promise<Array<TimeSettings>>
        users(): Promise<Array<User>>
        weekdays(params: { week: number; year: number }): Promise<Array<WeekDay>>
    }
    put: {
        roomReservation(value: RoomReservation): Promise<RoomReservation>
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth): Promise<ReservationPeriodicityByMonth>
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek): Promise<ReservationPeriodicityByWeek>
        reservationPeriodicityEachMonthSameDate(
            value: ReservationPeriodicityEachMonthSameDate
        ): Promise<ReservationPeriodicityEachMonthSameDate>
    }
    post: {
        roomReservation(value: RoomReservation): Promise<RoomReservation>
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth): Promise<ReservationPeriodicityByMonth>
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek): Promise<ReservationPeriodicityByWeek>
        reservationPeriodicityEachMonthSameDate(
            value: ReservationPeriodicityEachMonthSameDate
        ): Promise<ReservationPeriodicityEachMonthSameDate>
    }
    patch: {
        reservationPeriodicityByMonth(
            id: number,
            params: { start?: string; end?: string }
        ): Promise<ReservationPeriodicityByMonth>
        reservationPeriodicityByWeek(
            id: number,
            params: { start?: string; end?: string }
        ): Promise<ReservationPeriodicityByWeek>
        reservationPeriodicityEachMonthSameDate(
            id: number,
            params: {
                start?: string
                end?: string
            }
        ): Promise<ReservationPeriodicityEachMonthSameDate>
    }
    delete: {
        reservationPeriodicity(id: number): Promise<unknown>
        roomReservation(id: number): Promise<unknown>
    }
}

const api: FlopAPI = {
    fetch: {
        booleanRoomAttributes() {
            return fetcher(urls.booleanroomattributes)
        },
        booleanRoomAttributeValues() {
            return fetcher(urls.booleanroomattributevalues)
        },
        courses(params: { week?: number; year?: number; department?: string }) {
            return fetcher(urls.courses, params, [['department', 'dept']])
        },
        courseTypes(params: { department: string }) {
            return fetcher(urls.coursetypes, params, [['department', 'dept']])
        },
        departments() {
            return fetcher(urls.departments)
        },
        numericRoomAttributes() {
            return fetcher(urls.numericroomattributes)
        },
        numericRoomAttributeValues() {
            return fetcher(urls.numericroomattributevalues)
        },
        reservationPeriodicities() {
            return fetcher(urls.reservationperiodicity)
        },
        reservationPeriodicity(periodicityId: number): Promise<ReservationPeriodicity> {
            return fetcher(urls.reservationperiodicity, { id: periodicityId })
        },
        reservationPeriodicityByMonthXChoices() {
            return fetcher(urls.reservationperiodicitybymonthxchoice)
        },
        reservationPeriodicityTypes() {
            return fetcher(urls.reservationperiodicitytype)
        },
        room(id: number, additionalParams?: object) {
            return fetcher(buildUrl(urls.rooms, id.toString()), additionalParams)
        },
        rooms(params: { department?: string }) {
            return fetcher(urls.rooms, params, [['department', 'dept']])
        },
        roomReservations(params: { week?: number; year?: number; roomId?: number; periodicityId?: number }) {
            return fetcher(urls.roomreservation, params, [
                ['roomId', 'room'],
                ['periodicityId', 'periodicity'],
            ])
        },
        roomReservationTypes() {
            return fetcher(urls.roomreservationtype)
        },
        scheduledCourses(params: { week?: number; year?: number; department?: string }) {
            return fetcher(urls.scheduledcourses, params, [['department', 'dept']])
        },
        timeSettings() {
            return fetcher(urls.timesettings)
        },
        users() {
            return fetcher(urls.users)
        },
        weekdays(params: { week: number; year: number }) {
            return fetcher(urls.weekdays, params)
        },
    },
    put: {
        roomReservation(value: RoomReservation) {
            return putData<RoomReservation>(urls.roomreservation, value.id, value)
        },
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth) {
            return putData<ReservationPeriodicityByMonth>(urls.reservationperiodicitybymonth, value.id, value)
        },
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek) {
            return putData<ReservationPeriodicityByWeek>(urls.reservationperiodicitybyweek, value.id, value)
        },
        reservationPeriodicityEachMonthSameDate(value: ReservationPeriodicityEachMonthSameDate) {
            return putData<ReservationPeriodicityEachMonthSameDate>(
                urls.reservationperiodicityeachmonthsamedate,
                value.id,
                value
            )
        },
    },
    post: {
        roomReservation(value: RoomReservation) {
            return postData(urls.roomreservation, value)
        },
        reservationPeriodicityByMonth(value: ReservationPeriodicityByMonth) {
            return postData<ReservationPeriodicityByMonth>(urls.reservationperiodicitybymonth, value)
        },
        reservationPeriodicityByWeek(value: ReservationPeriodicityByWeek) {
            return postData<ReservationPeriodicityByWeek>(urls.reservationperiodicitybyweek, value)
        },
        reservationPeriodicityEachMonthSameDate(value: ReservationPeriodicityEachMonthSameDate) {
            return postData<ReservationPeriodicityEachMonthSameDate>(
                urls.reservationperiodicityeachmonthsamedate,
                value
            )
        },
    },
    patch: {
        reservationPeriodicityByMonth(id: number, params: { start?: string; end?: string }) {
            return patchData(urls.reservationperiodicitybymonth, id, params)
        },
        reservationPeriodicityByWeek(id: number, params: { start?: string; end?: string }) {
            return patchData(urls.reservationperiodicitybyweek, id, params)
        },
        reservationPeriodicityEachMonthSameDate(id: number, params: { start?: string; end?: string }) {
            return patchData(urls.reservationperiodicityeachmonthsamedate, id, params)
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
export { api }

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
