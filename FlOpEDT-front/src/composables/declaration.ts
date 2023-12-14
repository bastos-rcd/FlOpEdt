import { Timestamp } from '@quasar/quasar-ui-qcalendar'

export interface UpdatesHistory {
  type: 'course' | 'availability'
  objectId: number
}

export interface UpdateCourse extends UpdatesHistory {
  from: CourseData
  to: CourseData
}

export interface UpdateAvailability extends UpdatesHistory {
  from: AvailabilityData
  to: AvailabilityData
}

export interface CourseData {
  tutorId: number
  start: Timestamp
  end: Timestamp
  roomId: number
  suppTutorIds: number[]
  graded: boolean
  roomTypeId: number
  groupIds: number[]
}

export interface AvailabilityData {
  start: Timestamp
  end: Timestamp
  value: number
  duration: number
}
