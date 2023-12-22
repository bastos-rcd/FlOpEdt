import { Timestamp } from '@quasar/quasar-ui-qcalendar'
import {
  matBattery0Bar,
  matBattery1Bar,
  matBattery2Bar,
  matBattery3Bar,
  matBattery4Bar,
  matBattery5Bar,
  matBattery6Bar,
  matBatteryFull,
  matBatteryChargingFull,
} from '@quasar/extras/material-icons'

/**
 * Calendar event, for display purpose
 */
export interface CalendarEventNoCol {
  id: number
  title: string

  toggled: boolean

  bgcolor: string
  icon?: string

  data: EventData
}

export interface InputCalendarEvent extends CalendarEventNoCol {
  columnIds: number[]
}

export interface CalendarEvent extends CalendarEventNoCol {
  spans: Array<{ istart: number; weight: number; columnIds: number[] }>
}

export interface EventData {
  dataId: number
  dataType: 'event' | 'dropzone' | 'header' | 'avail'
  start: Timestamp
  duration?: number
  value?: number
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

interface AvailabilityData {
  color: Record<string, string>
  icon: Record<string, string>
}

export const availabilityData: AvailabilityData = {
  color: {
    '0': '#fc0328',
    '1': '#fc3403',
    '2': '#fc6703',
    '3': '#faa305',
    '4': '#faf405',
    '5': '#a4fa05',
    '6': '#53fd02',
    '7': '#04fb13',
    '8': '#00ff5e',
  },
  icon: {
    '0': matBattery0Bar,
    '1': matBattery1Bar,
    '2': matBattery2Bar,
    '3': matBattery3Bar,
    '4': matBattery4Bar,
    '5': matBattery5Bar,
    '6': matBattery6Bar,
    '7': matBatteryFull,
    '8': matBatteryChargingFull,
  },
}
