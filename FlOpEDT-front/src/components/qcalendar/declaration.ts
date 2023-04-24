/**
 * Calendar event, for display purpose
 */
export interface CalendarEvent {
  id: number
  title: string
  details: string
  date: string

  bgcolor: string
  icon?: string
  time?: string
  duration?: number
  days?: number

  columnIds?: number[]

  data?: any
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
  x: number
}

export interface CalendarDropzoneEvent {
  eventId: number
  duration: number
  columnIds: number[]
  possibleStarts: Record<string, string[]>
}