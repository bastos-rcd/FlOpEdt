import { User } from '@/ts/type'

const API_ENDPOINT = '/fr/api/'

const urls = {
    getcurrentuser : 'user/getcurrentuser',
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

//const csrfToken = getCookie('csrftoken')

export interface FlopAPI {
    getCurrentUser() : Promise<User>
}

const api: FlopAPI = {
    async getCurrentUser(): Promise<User> {
        let user : User = new User()
        await fetch(API_ENDPOINT+urls.getcurrentuser, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json'}
        }).then(
            async (response) => {
                if(!response.ok) {
                    throw Error('Erreur HTTP : ' + response.status)
                }
                await response.json()
                        .then(data => {
                            //console.log('data = ', data)
                            user = data
                        })
                        .catch( _ => console.log("ERROR JSON"))
            }
        ).catch( _ => console.log("ERROR FETCH"))
        return user
    }
}
export {api}