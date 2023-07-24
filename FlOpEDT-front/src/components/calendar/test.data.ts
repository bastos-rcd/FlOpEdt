import { Timestamp, addToDate, getStartOfWeek, parseDate, parseTime, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { CalendarColumn, InputCalendarEvent } from './declaration'
import { Ref, ref } from 'vue'

interface UseCase {
  columns: CalendarColumn[]
  events: Ref<InputCalendarEvent[]>
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
  events: ref<InputCalendarEvent[]>([
    {
      id: 1,
      title: 'TP INFO',
      toggled: true,

      bgcolor: 'red',
      icon: 'fas fa-handshake',

      columnIds: [2, 3],

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
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
      },
    },
    {
      id: 3,
      title: 'Conference TD1',
      toggled: true,
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      id: 4,
      title: 'Conference TD2',
      toggled: true,
      bgcolor: 'grey',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'event',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
    // Drop zones
    {
      id: 5,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '14:00'),
        duration: 150,
      },
    },
    {
      id: 6,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '11:00'),
        duration: 150,
      },
    },
    {
      id: 7,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:50'),
        duration: 150,
      },
    },
    {
      id: 8,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:00'),
        duration: 150,
      },
    },
    {
      id: 9,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:50'),
        duration: 150,
      },
    },
    {
      id: 10,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 150,
      },
    },
    {
      id: 11,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 150,
      },
    },
    {
      id: 12,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:50'),
        duration: 150,
      },
    },
    {
      id: 13,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:00'),
        duration: 150,
      },
    },
    {
      id: 14,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '08:50'),
        duration: 150,
      },
    },
    {
      id: 15,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 120,
      },
    },
    {
      id: 16,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '13:30'),
        duration: 120,
      },
    },
    {
      id: 17,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '11:00'),
        duration: 120,
      },
    },
    {
      id: 18,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '13:30'),
        duration: 120,
      },
    },
    {
      id: 19,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '11:00'),
        duration: 120,
      },
    },
    {
      id: 20,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '13:30'),
        duration: 120,
      },
    },
    {
      id: 57,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '11:00'),
        duration: 120,
      },
    },
    {
      id: 58,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '13:30'),
        duration: 120,
      },
    },
    {
      id: 59,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '11:00'),
        duration: 120,
      },
    },
    {
      id: 60,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '13:30'),
        duration: 120,
      },
    },
    {
      id: 21,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '08:00'),
        duration: 120,
      },
    },
    {
      id: 22,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '10:30'),
        duration: 120,
      },
    },
    {
      id: 23,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 120,
      },
    },
    {
      id: 24,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '16:30'),
        duration: 120,
      },
    },
    {
      id: 25,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      id: 26,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '10:50'),
        duration: 120,
      },
    },
    {
      id: 27,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '13:10'),
        duration: 120,
      },
    },
    {
      id: 28,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '19:10'),
        duration: 120,
      },
    },
    {
      id: 29,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '16:30'),
        duration: 120,
      },
    },
    {
      id: 30,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 120,
      },
    },
    {
      id: 31,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '10:50'),
        duration: 120,
      },
    },
    {
      id: 32,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '13:10'),
        duration: 120,
      },
    },
    {
      id: 33,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '19:10'),
        duration: 120,
      },
    },
    {
      id: 34,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '16:30'),
        duration: 120,
      },
    },
    {
      id: 35,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '08:00'),
        duration: 120,
      },
    },
    {
      id: 36,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '10:50'),
        duration: 120,
      },
    },
    {
      id: 37,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '13:10'),
        duration: 120,
      },
    },
    {
      id: 38,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '19:10'),
        duration: 120,
      },
    },
    {
      id: 39,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '16:30'),
        duration: 120,
      },
    },
    {
      id: 40,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '08:00'),
        duration: 120,
      },
    },
    {
      id: 41,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '10:50'),
        duration: 120,
      },
    },
    {
      id: 42,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '13:10'),
        duration: 120,
      },
    },
    {
      id: 43,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '19:10'),
        duration: 120,
      },
    },
    {
      id: 44,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '16:30'),
        duration: 120,
      },
    },
    {
      id: 45,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '16:30'),
        duration: 90,
      },
    },
    {
      id: 46,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 90,
      },
    },
    {
      id: 47,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '10:50'),
        duration: 90,
      },
    },
    {
      id: 48,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '19:10'),
        duration: 90,
      },
    },
    {
      id: 49,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '16:30'),
        duration: 90,
      },
    },
    {
      id: 50,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 90,
      },
    },
    {
      id: 51,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '10:50'),
        duration: 90,
      },
    },
    {
      id: 52,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '19:10'),
        duration: 90,
      },
    },
    {
      id: 53,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '16:30'),
        duration: 90,
      },
    },
    {
      id: 54,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '08:00'),
        duration: 90,
      },
    },
    {
      id: 55,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '10:50'),
        duration: 90,
      },
    },
    {
      id: 56,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '19:10'),
        duration: 90,
      },
    },
  ]),
}
