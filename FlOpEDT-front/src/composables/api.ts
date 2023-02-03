import { User } from '@/ts/type'
import { Department } from '../ts/type'

const API_ENDPOINT = '/fr/api/'

const urls = {
    getcurrentuser : 'user/getcurrentuser',
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
    scheduledcourses: 'fetch/scheduledcourses',
    coursetypes: 'courses/type',
    users: 'user/users',
    booleanroomattributes: 'rooms/booleanattributes',
    numericroomattributes: 'rooms/numericattributes',
    booleanroomattributevalues: 'rooms/booleanattributevalues',
    numericroomattributevalues: 'rooms/numericattributevalues',
    weeks: 'base/weeks'
}

function getCookie(name: string) {
    if (!document.cookie) {
        return null
    }
    //console.log(`This is the cookieeee : ${document.cookie}`)
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

export interface FlopAPI {
    getCurrentUser() : Promise<User>
    getAllDepartments() : Promise<Array<Department>>
}

const api: FlopAPI = {
    async getCurrentUser(): Promise<User> {
        let user : User = new User()
        await fetch(API_ENDPOINT+urls.getcurrentuser, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' }
        }).then(
            async (response) => {
                if(!response.ok) {
                    throw Error('Error : ' + response.status)
                }
                await response.json()
                        .then(data => {
                            user = data
                        })
                        .catch( error => console.log('Error : ' + error.message))
            }
        ).catch( error => {
            console.log(error.message)
        })
        return user
    },
    async getAllDepartments() : Promise<Array<Department>> {
        let departments : Array<Department> = []
        await fetch(API_ENDPOINT+urls.getAllDepartments, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' }
        }).then(
            async (response) => {
                if(!response.ok) {
                    return Promise.reject('Erreur : ' + response.status + ': ' + response.statusText)
                }
                await response.json()
                        .then(data => {
                            departments = data
                        })
                        .catch( error => { return Promise.reject(error.message) })
            }
        ).catch( error => {
            console.log(error.message)
        })
        return departments
    }
}
export {api}