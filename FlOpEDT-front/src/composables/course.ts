import { parsed, updateWorkWeek } from '@quasar/quasar-ui-qcalendar'
import { Timestamp } from '@quasar/quasar-ui-qcalendar/dist/types/types'

export function getCoursesData() {
  return [
    {
      id: 65692,
      no: 1,
      room: 210,
      start: updateWorkWeek(parsed('2023-04-25 14:15:00') as Timestamp),
      end: updateWorkWeek(parsed('2023-04-25T16:15:00') as Timestamp),
      tutorId: -1,
      suppTutorIds: [],
      module: -1,
      groupIds: [299],
      courseTypeId: -1,
      roomTypeIde: -1,
      graded: false,
      workCopy: -1,
    },
  ]
}
