import { cloneDeep, intersection } from 'lodash'
import { CalendarColumn, CalendarEvent } from './declaration'
import {
  TimestampOrNull,
  copyTimestamp,
  nextDay,
  parseTime,
  prevDay,
  updateFormatted,
  updateMinutes,
  diffTimestamp,
} from '@quasar/quasar-ui-qcalendar'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { Course } from '@/stores/declarations'
import { useDepartmentStore } from '@/stores/department'

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

export function generateSpanId(
  eventId: number,
  spans: {
    istart: number
    weight: number
    columnIds: number[]
  }
): string {
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

function eventTopAttribute(
  event: CalendarEvent,
  intervalHeight: number,
  intervalStart: number,
  intervalMinutes: number
): number {
  const startEvent = parseTime(event.data.start)
  return Math.floor((startEvent - intervalStart * 15) / intervalMinutes) * (intervalHeight + 1)
}

function eventHeightAttribute(event: CalendarEvent, intervalHeight: number, intervalMinutes: number): number {
  return (event.data.duration! / intervalMinutes) * (intervalHeight + 1)
}

export function badgeStyles(
  event: CalendarEvent,
  span: { istart: number; weight: number; columnIds: number[] },
  preWeight: Record<number, number>,
  totalWeight: number,
  columns: CalendarColumn[],
  closestStartTime: string,
  currentTime: TimestampOrNull,
  isInEdit: boolean = false,
  intervalHeight: number,
  intervalStart: number,
  intervalMinutes: number
) {
  const preceedingWeight = preWeight[columns[span.istart].id]
  const s: Record<string, string> = {
    top: '',
    height: '',
  }
  s.top = eventTopAttribute(event, intervalHeight, intervalStart, intervalMinutes) + 'px'
  s.left = Math.round((preceedingWeight / totalWeight) * 100) + '%'
  s.width = Math.round((100 * span.weight) / totalWeight) + '%'
  s.height = eventHeightAttribute(event, intervalHeight, intervalMinutes) + 'px'
  if (event.data.dataType === 'dropzone') {
    s['background-color'] = 'transparent'
  } else {
    s['background-color'] = event.bgcolor
  }
  if (event.data.dataType === 'event') {
    s['border'] = '2px solid #000000'
    s['margin'] = '0'
    s['box-sizing'] = 'border-box'
  } else if (event.data.dataType === 'avail') {
    if (isInEdit) s['resize'] = 'vertical'
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

function isTutorInTwoCourses(course1: Course, course2: Course): boolean {
  return course1.tutorId === course2.tutorId
}

function areBothCoursesInSameRoom(course1: Course, course2: Course): boolean {
  return course1.room === course2.room
}

function areCoursesNotPossibleAtSameTime(event1: CalendarEvent, event2: CalendarEvent): boolean {
  const courseStore = useScheduledCourseStore()
  if (event1.data.dataType === 'event' && event2.data.dataType === 'event') {
    const course1 = courseStore.getCourse(event1.data.dataId)
    const course2 = courseStore.getCourse(event2.data.dataId)
    if (course1 && course2) {
      return areBothCoursesInSameRoom(course1, course2) || isTutorInTwoCourses(course1, course2)
    }
  }
  return false
}

function areEventsOverlapped(event1: CalendarEvent, event2: CalendarEvent): boolean {
  const sameColumns = columnsInCommon(event1, event2)
  let timeOverlap = false
  if (sameColumns) {
    timeOverlap = eventsTimeOverlap(event1, event2)
  }
  return sameColumns && timeOverlap
}

function eventsTimeOverlap(event1: CalendarEvent, event2: CalendarEvent): boolean {
  let timeOverlap = false
  if (event1.data.start.date === event2.data.start.date) {
    const diff = Math.ceil(diffTimestamp(event1.data.start, event2.data.start, false) / 1000 / 60)
    if (diff > 0) {
      if (event1.data.duration) timeOverlap = event1.data.duration > diff
    } else {
      if (event2.data.duration) timeOverlap = event2.data.duration > Math.abs(diff)
    }
  }
  return timeOverlap
}

export function createDropzonesForEvent(
  eventId: number,
  allEvents: CalendarEvent[],
  dayStartTime: number,
  dayEndTime: number,
  lastDayOfWeek: number = 6,
  lunchBreakStart?: number,
  lunchBreakEnd?: number
): CalendarEvent[] {
  const dropzones: CalendarEvent[] = []
  const event = allEvents.find((ev) => ev.id === eventId)
  if (event) {
    createDropzonesOnTimes(
      event,
      allEvents,
      dayStartTime,
      dayEndTime,
      lastDayOfWeek,
      lunchBreakStart,
      lunchBreakEnd
    ).forEach((dz) => {
      dropzones.push(dz)
    })
  }
  return dropzones
}

/*
 ** dayStartTime && dayEndTime = minutes since midnight
 ** allEvents doesn't contain dropzones
 **
 */
function createDropzonesOnTimes(
  event: CalendarEvent,
  allEvents: CalendarEvent[],
  dayStartTime: number,
  dayEndTime: number,
  lastDayOfWeek: number = 6,
  lunchBreakStart?: number,
  lunchBreakEnd?: number,
  step: number = STEP_DEFAULT
): CalendarEvent[] {
  const dropZones: CalendarEvent[] = []
  const departmentStore = useDepartmentStore()
  const startTimes = departmentStore.startTimes.find((st) => st.duration === event.data.duration)
  let startTime = copyTimestamp(event.data.start)
  while (startTime.weekday !== 1) {
    startTime = prevDay(startTime)
    updateFormatted(startTime)
  }
  if (!startTimes) {
    while (startTime.weekday !== lastDayOfWeek) {
      updateMinutes(startTime, dayStartTime)
      if (event.data.duration) {
        while (parseTime(startTime) + event.data.duration <= dayEndTime) {
          const startTimeMinutes = parseTime(startTime)
          let isDuringLunch = false
          if (lunchBreakStart && lunchBreakEnd)
            isDuringLunch = isBetween(lunchBreakStart, lunchBreakEnd, startTimeMinutes, event.data.duration)
          if (!isDuringLunch) {
            const newDropZone: CalendarEvent = cloneDeep(event)
            newDropZone.data.dataId = event.id
            newDropZone.id = -1
            newDropZone.data.dataType = 'dropzone'
            newDropZone.data.start = startTime
            if (isPossibleDropzone(newDropZone, allEvents, event)) dropZones.push(newDropZone)
          }
          startTime = copyTimestamp(startTime)
          updateMinutes(startTime, closestStep(parseTime(startTime) + event.data.duration + step, step))
        }
      }
      startTime = nextDay(startTime)
      updateFormatted(startTime)
    }
  } else {
    while (startTime.weekday !== lastDayOfWeek) {
      updateMinutes(startTime, startTimes.allowedStartTimes[0])
      if (event.data.duration) {
        let i = 0
        while (i < startTimes.allowedStartTimes.length) {
          let isDuringLunch = false
          if (lunchBreakStart && lunchBreakEnd)
            isDuringLunch = isBetween(
              lunchBreakStart,
              lunchBreakEnd,
              startTimes.allowedStartTimes[i],
              event.data.duration
            )
          if (!isDuringLunch) {
            const newDropZone: CalendarEvent = cloneDeep(event)
            newDropZone.data.dataId = event.id
            newDropZone.id = -1
            newDropZone.data.dataType = 'dropzone'
            newDropZone.data.start = startTime
            if (isPossibleDropzone(newDropZone, allEvents, event)) dropZones.push(newDropZone)
          }
          startTime = copyTimestamp(startTime)
          i++
          updateMinutes(startTime, startTimes.allowedStartTimes[i])
        }
      }
      startTime = nextDay(startTime)
      updateFormatted(startTime)
    }
  }
  return dropZones
}

function isBetween(lowEnd: number, highEnd: number, start: number, duration: number): boolean {
  return lowEnd !== highEnd && ((start >= lowEnd && start < highEnd) || (start <= lowEnd && start + duration > lowEnd))
}

function isPossibleDropzone(
  dropzone: CalendarEvent,
  allCalendarEvents: CalendarEvent[],
  event: CalendarEvent
): boolean {
  let isPossible = true
  let i = 0
  // Compare the dropzone to every other events
  while (i < allCalendarEvents.length && isPossible) {
    // Current Event overlooked
    const currentEvent = allCalendarEvents[i]
    // Is it just on the same column and time with the current Event
    if (areEventsOverlapped(dropzone, currentEvent)) {
      isPossible = false
      //Else is it only overlapping on the time and if so does it have the same tutor
    } else if (
      event.id !== currentEvent.id &&
      eventsTimeOverlap(dropzone, currentEvent) &&
      areCoursesNotPossibleAtSameTime(event, currentEvent)
    ) {
      isPossible = false
    }
    i++
  }
  return isPossible
}
