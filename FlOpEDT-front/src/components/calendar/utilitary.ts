import { cloneDeep, intersection } from 'lodash'
import { CalendarColumn, CalendarEvent, InputCalendarEvent } from './declaration'
import { TimestampOrNull, copyTimestamp, parseTime, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { diffTimestamp } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'

export const STEP_DEFAULT: number = 15

let idAvail = 900

export function nextId(): number {
  return idAvail++
}

export function badgeClasses(type: 'event' | 'dropzone' | 'header' | 'avail', bgcolor?: string) {
  switch (type) {
    case 'event':
      return {
        [`text-white bg-${bgcolor}`]: true,
        'rounded-border': true,
      }
    case 'dropzone':
      return 'my-dropzone border-dashed'
    case 'header':
      return {}
    case 'avail':
      return { 'rounded-border': true }
  }
}

export function isItOnStep(nbMinutes: number, step: number): boolean {
  return nbMinutes % step === 0
}

export function closestStep(nbMinutes: number, step: number = STEP_DEFAULT): number {
  if (!isItOnStep(nbMinutes, step)) {
    const mod = nbMinutes % step
    if (mod < step / 2) {
      if (nbMinutes - mod === 0) return step
      return nbMinutes - mod
    } else {
      return nbMinutes + (step - mod)
    }
  } else {
    return nbMinutes
  }
}

export function generateSpanId(eventId: number, spans: any): string {
  let colIds = ''
  spans.columnIds.forEach((cl: number) => {
    colIds += cl.toString()
  })
  return `${eventId}-${colIds}-${spans.istart}`
}

export function columnsInCommon(event1: CalendarEvent, event2: CalendarEvent): boolean {
  const cols1 = event1.spans.map((span) => span.columnIds).flat()
  const cols2 = event2.spans.map((span) => span.columnIds).flat()
  return intersection(cols1, cols2).length !== 0
}

export function updateEventsOverlap(events: CalendarEvent[]): CalendarEvent[] {
  const newEvents: CalendarEvent[] = events
  for (let i = 0; i < newEvents.length; i++) {
    if (newEvents[i].toggled) {
      for (let k = 0; k < newEvents.length; k++) {
        if (i !== k && (k > i || !newEvents[k].toggled)) {
          if (
            areEventsOverlapped(newEvents[i], newEvents[k]) &&
            newEvents[i].data.dataType === newEvents[k].data.dataType
          ) {
            newEvents[i].toggled = newEvents[k].toggled = false
          }
        }
      }
    }
  }
  return newEvents
}

export function areEventsOverlapped(event1: CalendarEvent, event2: CalendarEvent): boolean {
  const sameColumns = columnsInCommon(event1, event2)
  let timeOverlap = false
  if (sameColumns) {
    const diff = Math.ceil(diffTimestamp(event1.data.start, event2.data.start) / 1000 / 60)
    if (diff > 0) {
      if (event1.data.duration) timeOverlap = event1.data.duration > diff
    } else {
      if (event2.data.duration) timeOverlap = event2.data.duration > Math.abs(diff)
    }
  }
  return sameColumns && timeOverlap
}

/*
 ** dayStartTime && dayEndTime = minutes since midnight
 **
 */
export function createDropZonesOnTimes(
  event: InputCalendarEvent,
  dayStartTime: number,
  dayEndTime: number,
  newId: number
): InputCalendarEvent[] {
  const dropZones: InputCalendarEvent[] = []
  let startTime = copyTimestamp(event.data.start)
  updateMinutes(startTime, dayStartTime)
  if (event.data.duration) {
    while (parseTime(startTime) + event.data.duration <= dayEndTime) {
      const newDropZone: InputCalendarEvent = cloneDeep(event)
      newDropZone.data.dataId = event.id
      newDropZone.id = newId++
      newDropZone.data.dataType = 'dropzone'
      newDropZone.data.start = startTime
      dropZones.push(newDropZone)
      startTime = copyTimestamp(startTime)
      updateMinutes(startTime, parseTime(startTime) + event.data.duration + 5)
    }
  }
  return dropZones
}

export function badgeStyles(
  event: CalendarEvent,
  span: { istart: number; weight: number; columnIds: number[] },
  timeStartPos: any = undefined,
  preWeight: Record<number, number>,
  totalWeight: number,
  columns: CalendarColumn[],
  timeDurationHeight: Function,
  closestStartTime: string,
  currentTime: TimestampOrNull
) {
  const preceedingWeight = preWeight[columns[span.istart].id]

  const s: Record<string, string> = {
    top: '',
    height: '',
  }
  if (timeStartPos) {
    s.top = timeStartPos(event.data?.start) + 'px'
    s.left = Math.round((preceedingWeight / totalWeight) * 100) + '%'
    s.width = Math.round((100 * span.weight) / totalWeight) + '%'
    s.height = timeDurationHeight(event.data?.duration) + 'px'
  }
  if (event.data.dataType === 'dropzone') {
    s['background-color'] = 'transparent'
  } else {
    s['background-color'] = event.bgcolor
  }
  if (event.data.dataType === 'event') {
    s['border'] = '2px solid #000000'
  } else if (event.data.dataType === 'avail') {
    s['resize'] = 'vertical'
    s['overflow'] = 'auto'
    s['border'] = '1px solid #222222'
  } else if (
    event.data?.dataType === 'dropzone' &&
    event.data.start.time === closestStartTime &&
    event.data.start.date === currentTime?.date
  ) {
    s['border-color'] = 'green'
    s['border-width'] = '3px'
  }
  s['align-items'] = 'flex-start'
  if (!event.toggled && event.data.dataType === 'event') {
    s['background-color'] = 'rgba(80,80,80,0.5)'
  }
  return s
}
