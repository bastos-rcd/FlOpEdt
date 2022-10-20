import type {
    BooleanRoomAttributeValue,
    Course,
    CourseType,
    Department,
    NumericRoomAttributeValue,
    Room,
    RoomAttribute,
    RoomReservation,
    RoomReservationType,
    ScheduledCourse,
    TimeSettings,
    User,
    WeekDay,
} from '@/assets/js/types'

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

async function fetchData(url: string, params: { [k: string]: never }) {
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
    const finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}/?${args}`
    console.log(`Fetching ${finalUrl}...`)

    const response = await fetch(finalUrl, params)
    const json = (await response.json()) || {}
    if (!response.ok) {
        const errorMessage = json.error || `${response.status}`
        throw new Error(errorMessage)
    }
    return json
}

async function sendData<T>(
    method: string,
    url: string,
    optional: { data?: unknown; id?: number; authToken?: string }
): Promise<T | never> {
    if (!['PUT', 'POST', 'DELETE'].includes(method)) {
        return Promise.reject('Method must be either PUT, POST, or DELETE')
    }

    // Setup headers
    const requestHeaders: HeadersInit = new Headers()
    requestHeaders.set('Content-Type', 'application/json')
    if (csrfToken) {
        requestHeaders.set('X-CSRFToken', csrfToken)
    }
    if (optional.authToken) {
        requestHeaders.set('Authorization', `Token ${optional.authToken}`)
    }

    // Setup request
    const requestInit: RequestInit = {
        method: method,
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: requestHeaders,
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    }
    if (optional.data) {
        requestInit.body = JSON.stringify(optional.data)
    }

    // Create url
    let endUrl = '/'
    if (optional.id) {
        endUrl = `/${optional.id}/`
    }
    const finalUrl = `${import.meta.env.VITE_API_ENDPOINT}${url}${endUrl}`
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

async function putData<T>(url: string, id: number, data: unknown, authToken?: string): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        id: id,
        data: data,
    }
    if (authToken) {
        optional.authToken = authToken
    }
    return await sendData('PUT', url, optional)
}

async function postData<T>(url: string, data: unknown, authToken?: string): Promise<T | never> {
    const optional: { [key: string]: unknown } = {
        data: data,
    }
    if (authToken) {
        optional.authToken = authToken
    }
    return await sendData('POST', url, optional)
}

function deleteData(url: string, id: number, authToken?: string) {
    const optional: { [key: string]: unknown } = {
        id: id,
    }
    if (authToken) {
        optional.authToken = authToken
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
    courses: 'courses/courses',
    scheduledcourses: 'fetch/scheduledcourses',
    coursetypes: 'courses/type',
    users: 'user/users',
    authToken: 'api-token-auth',
    booleanroomattributes: 'rooms/booleanattributes',
    numericroomattributes: 'rooms/numericattributes',
    booleanroomattributevalues: 'rooms/booleanattributevalues',
    numericroomattributevalues: 'rooms/numericattributevalues',
}

/**
 * Proxy function to fetch from the api.
 * @param {string} url The url to access the data
 * @param {object} params1 Manually given parameters
 * @param {object} params2 Object-format given parameters
 * @returns {Promise<any>}
 */
const fetcher = (url: string, params1?: object, params2?: object) => fetchData(url, { ...params1, ...params2 })

function buildUrl(base: string, uri: string) {
    return `${base}/${uri}`
}

export interface FlopAPI {
    fetch: {
        all: {
            departments(): Promise<Array<Department>>
            rooms(department: string): Promise<Array<Room>>
            timeSettings(): Promise<Array<TimeSettings>>
            courseTypes(department: string): Promise<Array<CourseType>>
            roomReservationTypes(): Promise<Array<RoomReservationType>>
            users(): Promise<Array<User>>
            booleanRoomAttributes(): Promise<Array<RoomAttribute>>
            numericRoomAttributes(): Promise<Array<RoomAttribute>>
            booleanRoomAttributeValues(): Promise<Array<BooleanRoomAttributeValue>>
            numericRoomAttributeValues(): Promise<Array<NumericRoomAttributeValue>>
        }
        target: {
            room(id: number, additionalParams?: object): Promise<Room>
            weekdays(week: number, year: number, additionalParams?: object): Promise<Array<WeekDay>>
            roomReservations(
                week: number,
                year: number,
                params: { roomId?: number },
                additionalParams?: object
            ): Promise<Array<RoomReservation>>
            courses(
                week: number,
                year: number,
                params: { department?: string },
                additionalParams?: object
            ): Promise<Array<Course>>
            scheduledCourses(
                week: number,
                year: number,
                department: string,
                additionalParams?: object
            ): Promise<Array<ScheduledCourse>>
            token(username: string, password: string): Promise<{ token: string }>
        }
    }
    put: {
        roomReservation(value: RoomReservation, authToken?: string): Promise<RoomReservation>
    }
    post: {
        roomReservation(value: RoomReservation, authToken?: string): Promise<RoomReservation>
    }
    delete: {
        roomReservation(id: number, authToken?: string): Promise<unknown>
    }
}

const api: FlopAPI = {
    fetch: {
        all: {
            departments() {
                return fetcher(urls.departments)
            },
            rooms(department: string) {
                return fetcher(urls.rooms, { dept: department })
            },
            timeSettings() {
                return fetcher(urls.timesettings)
            },
            courseTypes(department: string) {
                return fetcher(urls.coursetypes, { dept: department })
            },
            roomReservationTypes() {
                return fetcher(urls.roomreservationtype)
            },
            users() {
                return fetcher(urls.users)
            },
            booleanRoomAttributes() {
                return fetcher(urls.booleanroomattributes)
            },
            numericRoomAttributes() {
                return fetcher(urls.numericroomattributes)
            },
            booleanRoomAttributeValues() {
                return fetcher(urls.booleanroomattributevalues)
            },
            numericRoomAttributeValues() {
                return fetcher(urls.numericroomattributevalues)
            },
        },
        target: {
            room(id: number, additionalParams?: object) {
                return fetcher(buildUrl(urls.rooms, id.toString()), additionalParams)
            },
            weekdays(week: number, year: number, additionalParams?: object) {
                return fetcher(
                    urls.weekdays,
                    {
                        week: week,
                        year: year,
                    },
                    additionalParams
                )
            },
            roomReservations(week: number, year: number, params: { roomId?: number }, additionalParams?: object) {
                return fetcher(
                    urls.roomreservation,
                    {
                        ...{
                            week: week,
                            year: year,
                        },
                        ...{
                            ...(params.roomId && { room: params.roomId }),
                            ...(!params.roomId && {}),
                        },
                    },
                    additionalParams
                )
            },
            courses(week: number, year: number, params: { department?: string }, additionalParams?: object) {
                return fetcher(
                    urls.courses,
                    {
                        ...{
                            week: week,
                            year: year,
                        },
                        ...{
                            ...(params.department && {
                                dept: params.department,
                            }),
                            ...(!params.department && {}),
                        },
                    },
                    additionalParams
                )
            },
            scheduledCourses(week: number, year: number, department: string, additionalParams?: object) {
                return fetcher(
                    urls.scheduledcourses,
                    {
                        week: week,
                        year: year,
                        dept: department,
                    },
                    additionalParams
                )
            },
            token(username: string, password: string) {
                return postData<{ token: string }>(urls.authToken, {
                    username: username,
                    password: password,
                })
            },
        },
    },
    put: {
        roomReservation(value: RoomReservation, authToken?: string) {
            return putData<RoomReservation>(urls.roomreservation, value.id, value, authToken)
        },
    },
    post: {
        roomReservation(value: RoomReservation, authToken?: string) {
            return postData(urls.roomreservation, value, authToken)
        },
    },
    delete: {
        roomReservation(id: number, authToken?: string): Promise<unknown> {
            return deleteData(urls.roomreservation, id, authToken)
        },
    },
}
export { api }
