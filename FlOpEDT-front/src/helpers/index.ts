import { Department } from '@/ts/type'
import { Room } from '@/stores/declarations'
import { useRoomStore } from '@/stores/timetable/room'
import { api } from '@/utils/api'

export function convertDecimalTimeToHuman(time: number): string {
  const hours = Math.trunc(time)
  const minutes = Math.round((time - hours) * 60)
  return `${hours}:${toStringAtLeastTwoDigits(minutes)}`
}

/**
 * Takes a number and convert it to a string with a '0' prefix if there is only one digit.
 * If the number is in a string then a '0' prefix is prepended if needed.
 * @param {number} element The element to convert
 * @returns {string} The two-digits string
 */
export function toStringAtLeastTwoDigits(element: number | string) {
  if (typeof element === 'string') {
    element = parseInt(element, 10)
    if (isNaN(element)) {
      throw new Error(`Given value (${element}) cannot not be parsed as number`)
    }
  }
  return `${element < 10 ? `0${element}` : element}`
}

export function parseReason(reason: unknown, onAlert?: (level: string, message: string) => void) {
  // Reason can be either a response body or a thrown error
  if (reason instanceof Object && !(reason instanceof Error)) {
    // Reason is a response body, display each message separately
    const reasonObj = reason as { [key: string]: string }
    Object.keys(reasonObj).forEach((key) => {
      onAlert?.('danger', `${key}: ${reasonObj[key]}`)
    })
  } else {
    onAlert?.('danger', `${reason}.`)
  }
}

/**
 * Takes an array and a predicate to extract a key serving as the group-by option.
 * Returns an object having each key property matching a list of given type.
 * @param list The array
 * @param keyPredicate The function to extract a key from each element
 */
export function listGroupBy<T>(list: Array<T>, keyPredicate: (value: T) => string): { [p: string]: Array<T> } {
  const out: { [day: string]: Array<T> } = {}
  list.forEach((value) => {
    const key = keyPredicate(value)
    if (!(key in out)) {
      out[key] = []
    }
    out[key].push(value)
  })
  return out
}

/**
 * Accepts an array of objects having an id and returns an array containing only those ids.
 * @param list
 */
export function mapListId(list: Array<{ id: number }>): Array<number> {
  return list.map((element) => element.id)
}

/**
 * Takes an object having departments id as key and an array.
 * Returns the filtered entries of selected departments.
 * @param object
 */
export function filterBySelectedDepartments<T>(
  object: { [key: string]: Array<T> },
  selectedDepartments: Array<Department>
) {
  const out: { [departmentId: string]: Array<T> } = Object.fromEntries(
    Object.entries(object).filter(([key]) => selectedDepartments.findIndex((dept) => `${dept.id}` === key) >= 0)
  )
  return out
}

/**
 * Takes a room id and
 * returns true if the room is available to the selected departments, false otherwise
 * @param roomId The room id
 */
export function isRoomInSelectedDepartments(roomId: number, departments: Array<Department>): boolean {
  const roomStore = useRoomStore()
  let inDept = false
  const room: Room = roomStore.getRoomById(roomId) as unknown as Room
  if (room)
    room.departmentIds.forEach((roomDeptId: number) => {
      departments.forEach((dept) => {
        if (dept.id === roomDeptId) {
          inDept = true
        }
      })
    })
  return room !== undefined && inDept
}

export function handleReason(level: string, message: string) {
  console.error(`${level}: ${message}`)
}

/**
 * Take a collection of key->Array objects and add a new element to a specific key
 * @param collection The dict object hosting the data
 * @param id The key of the array which will contain the new data
 * @param element The new data element
 */
export function addTo<T>(collection: { [p: string]: Array<T> }, id: string | number, element: T): void {
  if (!collection[id]) {
    collection[id] = []
  }
  collection[id].push(element)
}

/**
 * Takes the day and the month to return a string representing the date
 * @param day number of the day in the month : 1 - 31
 * @param month Number of the month in the year starting at 0 : 0 - 11
 * @returns The formatted string as "dd/MM"
 */
export function createDateId(day: string | number, month: string | number): string {
  return `${toStringAtLeastTwoDigits(day)}/${toStringAtLeastTwoDigits(month)}`
}

/**
 * Explain
 * @param periodicityId
 * @returns Nothing ?
 */
export function deleteReservationPeriodicity(periodicityId: number): Promise<unknown> {
  return api.delete.reservationPeriodicity(periodicityId)
}


/**
 * Helpers for WeekPicker.vue
 * @param date The date we wanna know the week number of
 * @returns the week number in the current year
 */
export function getNumberOfTheWeek(date: Date) {
  // We get the first day of the year
  const yearStart = new Date(Date.UTC(date.getFullYear(), 0, 1))
  // We get the thursday of our week
  const currentThursday = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  currentThursday.setUTCDate(currentThursday.getUTCDate() + 4 - (currentThursday.getUTCDay() || 7))
  return Math.ceil(((currentThursday.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}

export function minutesFromDate(d: Date): number {
  const midnight = new Date(d)
  midnight.setMinutes(0)
  midnight.setHours(0)
  const diff = new Date(d.getTime() - midnight.getTime())
  return diff.getHours() * 60 + diff.getMinutes()
}
