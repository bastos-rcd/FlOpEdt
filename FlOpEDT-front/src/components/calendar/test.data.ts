import { Timestamp, addToDate, getStartOfWeek, parseDate, parseTime, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { CalendarColumn, CalendarEvent } from './declaration'
import { Ref, ref } from 'vue'

interface UseCase {
  columns: CalendarColumn[]
  events: Ref<CalendarEvent[]>
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
  events: ref<CalendarEvent[]>([
    {
      id: 1,
      title: 'TP INFO',
      toggled: true,

      bgcolor: 'red',
      icon: 'fas fa-handshake',

      span: [{ istart: 2, columnIds: [2, 3], weight: 2 }],

      data: {
        dataId: 3,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      id: 2,
      title: 'Lunch',
      toggled: true,
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      span: [{ istart: 0, columnIds: [0, 1, 2, 3], weight: 6 }],
      data: {
        dataId: 4,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
      },
    },
  ]),
}
