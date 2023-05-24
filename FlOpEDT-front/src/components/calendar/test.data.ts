import { Timestamp, addToDate, getStartOfWeek, parseDate, parseTime, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { CalendarColumn, CalendarDropzoneEvent, CalendarEvent } from './declaration'
import { Ref, ref } from 'vue'

interface UseCase {
  columns: CalendarColumn[]
  totalWeight: number
  events: Ref<CalendarEvent[]>
  dropzoneEvents: CalendarDropzoneEvent[]
}

const CURRENT_DAY = new Date()
function shiftInCurrentWeek(relativeDay: number, time?: string): Timestamp {
  const tm = addToDate(weekStart, { day: relativeDay })
  if (tm && time) {
    updateMinutes(tm, parseTime(time))
  }
  return tm as Timestamp
}
const weekStart = getStartOfWeek(parseDate(CURRENT_DAY) as Timestamp, [1, 2, 3, 4, 5])

export const useCase: UseCase = {
  columns: [
    {
      id: 0,
      name: 'TD1',
      weight: 2,
    },
    {
      id: 1,
      name: 'TD2',
      weight: 2,
    },
    {
      id: 2,
      name: 'TP31',
      weight: 1,
    },
    {
      id: 3,
      name: 'TP32',
      weight: 1,
    },
  ],
  totalWeight: 6,
  events: ref([
    {
      title: 'TP INFO',
      details: "Let' work on our Python project",
      bgcolor: 'red',
      icon: 'fas fa-handshake',
      displayData: [
        { weight: 1, columnId: 2 },
        { weight: 1, columnId: 3 },
      ],
      data: {
        dataId: 3,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      title: 'Lunch',
      details: 'Company is paying!',
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      displayData: [
        { weight: 1, columnId: 0 },
        { weight: 1, columnId: 1 },
        { weight: 1, columnId: 2 },
        { weight: 1, columnId: 3 },
      ],
      data: {
        dataId: 4,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
      },
    },
    {
      title: 'Conference TD1',
      details: 'Always a nice chat with mom',
      bgcolor: 'grey',
      icon: 'fas fa-car',
      displayData: [{ weight: 1, columnId: 0 }],
      data: {
        dataId: 5,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      title: 'Conference TD2',
      details: 'Teaching Javascript 101',
      bgcolor: 'grey',
      icon: 'fas fa-chalkboard-teacher',
      displayData: [{ weight: 1, columnId: 1 }],
      data: {
        dataId: 6,
        dataType: 'mok',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
  ]),
  dropzoneEvents: [
    {
      eventId: 5,
      duration: 90,
      columnIds: [0, 1],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '09:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '15:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '14:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '14:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '14:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '14:30') },
        ],
      },
    },
    {
      eventId: 4,
      duration: 120,
      columnIds: [0, 1, 2, 3],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '13:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '13:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '13:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '13:30') },
        ],
      },
    },
    {
      eventId: 3,
      duration: 120,
      columnIds: [2, 3],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '10:30') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '14:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '16:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '16:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '16:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '16:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '16:30') },
        ],
      },
    },
    {
      eventId: 6,
      duration: 150,
      columnIds: [1],
      possibleStarts: {
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '16:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '16:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '16:30') },
        ],
      },
    },
  ],
}
