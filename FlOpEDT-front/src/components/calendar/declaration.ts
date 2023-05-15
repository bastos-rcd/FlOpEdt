import { Timestamp } from '@quasar/quasar-ui-qcalendar'

/**
 * Calendar event, for display purpose
 */
export interface CalendarEvent {
  title: string
  details: string

  bgcolor: string
  icon?: string

  columnIds: number[]

  data: EventData
}

export interface EventData {
  dataId: number
  dataType: string
  start: Timestamp
  duration?: number
  days?: number
}

/**
 * Calendar column, to divide each day in several columns
 */
export interface CalendarColumn {
  id: number
  name: string
  weight: number
  /**
   * Position of the column in the abscissa
   */
  // x: number
  // active: boolean
}

export interface CalendarResourceScope {
  resource: { id: number }
  timeStartPosX(time: Timestamp): number
  timeDurationWidth(duration: number): number
}

// This is expected to change, but for now, let's start with that
export interface CalendarResourceEvent {
  left: number
  width: number
  title: string
}


export interface CalendarDropzoneEvent {
  eventId: number
  duration: number
  columnIds: number[]
  possibleStarts: Record<string, { isClose: boolean; timeStart: Timestamp }[]>
}