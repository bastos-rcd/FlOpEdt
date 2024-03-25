<template>
  <div class="calendar-div">
    <div class="header">
      <span>N° de version sélectionnée: {{ workcopy === -1 ? 'default' : workcopy }}</span>
      <button @click="onPrev">&lt; Prev</button>
      <button @click="onToday">Today</button>
      <button @click="onNext">Next &gt;</button>
    </div>
    <q-calendar-day
      ref="calendar"
      v-model="selectedDate"
      :locale="locale"
      :selected-dates="selectedDates"
      :view="typeCalendar"
      bordered
      hoverable
      animated
      transition-next="slide-left"
      transition-prev="slide-right"
      no-active-date
      :interval-start="props.startOfDay / props.intervalMinutes - 1"
      :interval-count="(props.endOfDay - props.startOfDay) / props.intervalMinutes + 2"
      :interval-minutes="props.intervalMinutes"
      :interval-height="20"
      time-clicks-clamped
      :weekdays="weekdays"
      :drag-enter-func="onDragEnter"
      :drag-over-func="onDragOver"
      :drag-leave-func="onDragLeave"
      @dragend="onDragStop"
    >
      <template #head-intervals="{ scope }">
        <span>{{ selectedDate.substring(5, 7) }}/{{ selectedDate.substring(0, 4) }}</span>
      </template>
      <template #head-day-event="{ scope: { timestamp } }">
        <div style="display: flex">
          <template v-for="column in props.columns" :key="column.id">
            <div
              :class="badgeClasses('header')"
              style="
                cursor: pointer;
                height: 12px;
                font-size: 10px;
                margin-bottom: 1px;
                margin-top: 1px;
                border-color: 1px solid black;
                color: black;
              "
              :style="{
                'flex-basis': Math.round((100 * column.weight) / totalWeight) + '%',
                'text-align': 'center',
              }"
            >
              {{ column.name }}
            </div>
          </template>
        </div>
      </template>

      <template #day-body="{ scope: { timestamp, timeStartPos } }">
        <!-- events to display -->
        <template v-for="event in eventsByDate.get(timestamp.date)" :key="event.id">
          <template
            v-if="
              event.data.duration !== undefined &&
              (event.data.dataType === 'event' ||
                event.data.dataType === 'avail' ||
                (isDragging && event.data.dataId === eventDragged?.id))
            "
          >
            <div :draggable="event.data.dataType !== 'avail'" @dragstart="onDragStart($event, event)">
              <div
                v-for="span in event.spans"
                :key="generateSpanId(event.id, span)"
                class="event-span"
                :class="badgeClasses(event.data.dataType, event.bgcolor)"
                :style="
                  badgeStyles(
                    event,
                    span,
                    timeStartPos,
                    preWeight,
                    totalWeight,
                    props.columns,
                    calendar!.timeDurationHeight,
                    closestStartTime,
                    currentTime
                  )
                "
                @mousedown="onMouseDown($event, event.id)"
                @mouseup="onMouseUp()"
              >
                <slot
                  name="event"
                  :event="event"
                  v-if="event.data.dataType !== 'avail' && event.data.dataType !== 'dropzone'"
                >
                  <edit-event :event-object-id="event.data.dataId">
                    <template v-slot:trigger>
                      <CourseCard :event-id="event.data.dataId" />
                    </template>
                  </edit-event>
                </slot>
                <slot name="event" :event="event" v-else>
                  <div
                    style="
                      width: 100%;
                      height: 100%;
                      flex-direction: column;
                      justify-content: center;
                      align-items: center;
                      display: flex;
                    "
                    class="avail"
                  >
                    <AvailibityMenu :event="event" @update:event="changeAvailValue">
                      <template v-slot:trigger>
                        <span class="avail">
                          {{ event.data.value }}
                        </span>
                      </template>
                    </AvailibityMenu>
                  </div>
                </slot>
              </div>
            </div>
          </template>
        </template>
      </template>
    </q-calendar-day>
  </div>
</template>

<script setup lang="ts">
import { today } from '@quasar/quasar-ui-qcalendar/src/index.js'
import '@quasar/quasar-ui-qcalendar/src/QCalendarVariables.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarTransitions.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarAgenda.sass'
import {
  QCalendarDay,
  copyTimestamp,
  diffTimestamp,
  parseTime,
  updateMinutes,
} from '@quasar/quasar-ui-qcalendar/src/QCalendarDay.js'

import { forEach, includes, cloneDeep, remove, sortBy, find, sumBy, filter } from 'lodash'

import { CalendarColumn, CalendarEvent, InputCalendarEvent } from './declaration'

import { Ref, computed, ref } from 'vue'
import {
  TimestampOrNull,
  Timestamp,
  parsed,
  QCalendar,
  parseTimestamp,
  prevDay,
  nextDay,
  getTime,
  updateFormatted,
  getStartOfWeek,
} from '@quasar/quasar-ui-qcalendar'
import { watch } from 'vue'
import { availabilityData } from './declaration'
import EditEvent from '../EditEvent.vue'
import { useI18n } from 'vue-i18n'
import { STEP_DEFAULT, badgeClasses, closestStep, generateSpanId, badgeStyles, updateEventsOverlap } from './utilitary'
import AvailibityMenu from '../AvailibityMenu.vue'
import CourseCard from '../CourseCard.vue'

const { locale } = useI18n({ useScope: 'global' })
/**
 * Calendar component handling the display of a week with
 * events data in it.
 */

/**
 * Data passed to the component to handle the display in
 * columns for each day
 * *  The dropzoneEvents have references of events ids and
 * *  the totalWeight is the total of each columns weight
 */
const props = defineProps<{
  events: InputCalendarEvent[]
  dropzones?: CalendarEvent[]
  columns: CalendarColumn[]
  endOfDay: number
  startOfDay: number
  step?: number
  workcopy: number
  intervalMinutes: number
}>()

const emits = defineEmits<{
  (e: 'dragstart', id: number, allEvents: CalendarEvent[]): void
  (e: 'update:events', value: InputCalendarEvent[]): void
  (e: 'update:week', value: Timestamp): void
  (e: 'weekdays', value: number[]): void
  (e: 'event:details', value: number): void
  (e: 'update:event', value: InputCalendarEvent): void
}>()

const preWeight = computed(() => {
  const map: Record<number, number> = {}
  let preceeding = 0
  forEach(props.columns, (col: CalendarColumn) => {
    map[col.id] = preceeding
    preceeding += col.weight
  })
  return map
})

const calendar: Ref<QCalendar | null> = ref(null)
/**
 * QCalendar DATA TO DISPLAY
 * * Format the data from the events to match the calendar display,
 * * Functions to compute the style to render for each event
 */
const selectedDate = ref<string>(
  updateFormatted(updateFormatted(getStartOfWeek(parseTimestamp(today())!, [1, 2, 3, 4, 5, 6, 0]))).date
)

watch(selectedDate, () => {
  console.log(updateFormatted(parsed(selectedDate.value) as Timestamp))
  emits('update:week', updateFormatted(parsed(selectedDate.value) as Timestamp))
})

/**
 * Time and date data defining which days will
 * be displayed in a week
 */
const weekdays = ref<number[]>([1, 2, 3, 4, 5])
const selectedDates = ref<string[]>([today()])
const typeCalendar = ref<string>('week')
const dayStart = ref<{ min: number; max: number }>()

watch(dayStart, () => {
  const newValue: number[] = []
  if (dayStart.value)
    for (let i = dayStart.value?.min; i <= dayStart.value?.max; i++) {
      if (i === 7) newValue.push(0)
      else newValue.push(i)
    }
  weekdays.value = newValue
  if (weekdays.value.length === 1) {
    typeCalendar.value = 'day'
  } else {
    typeCalendar.value = 'week'
  }
  const newSelectedDates = []
  let now_date = parseTimestamp(selectedDate.value)

  while (now_date!.weekday > 1) {
    now_date = prevDay(now_date as Timestamp)
    now_date!.date = `${now_date?.year}-${putAZero(now_date.month)}-${putAZero(now_date.day)}` as string
  }
  while (newSelectedDates.length < weekdays.value.length) {
    if (includes(weekdays.value, now_date?.weekday)) {
      newSelectedDates.push(now_date?.date)
    }
    now_date = nextDay(now_date as Timestamp)
    now_date!.date = `${now_date?.year}-${putAZero(now_date.month)}-${putAZero(now_date.day)}` as string
  }
  selectedDates.value = newSelectedDates as string[]
  selectedDate.value = selectedDates.value[0]
})

function putAZero(i: number): string {
  if (i <= 9) return `0${i}`
  return `${i}`
}

// Events send to the qcalendar ordered by their date
// Their columnIds are changed to merge the same events
// occuring on different columns
const eventsByDate = computed(() => {
  const map: Map<string, CalendarEvent[]> = new Map<string, CalendarEvent[]>()
  let allEvents: InputCalendarEvent[] = props.events
  // Copy of events
  const newEvents: CalendarEvent[] = []
  // Dict of column ids keys to their index
  const columnIndexes: Record<number, number> = {}
  forEach(props.columns, (c, i) => {
    columnIndexes[c.id] = i
  })
  allEvents.forEach((event) => {
    const newEvent = cloneDeep(event)
    let columnIds = newEvent.columnIds
    if (newEvent.data.dataType === 'dropzone') {
      const eventRelated = allEvents.find((ev) => ev.id === newEvent.data.dataId && ev.data.dataType === 'event')
      if (eventRelated) columnIds = eventRelated.columnIds
    }

    // availability column
    if (newEvent.data.dataType === 'avail') {
      newEvent.bgcolor = availabilityData.color[newEvent.data.value?.toString() || '0']
      newEvent.icon = availabilityData.icon[newEvent.data.value?.toString() || '0']
    }

    // filter out absent columns
    remove(columnIds, (colId) => !(colId in columnIndexes))

    // merge columns
    columnIds = sortBy(columnIds, (colId) => columnIndexes[colId])

    const spans: Array<{ istart: number; weight: number; columnIds: number[] }> = []
    if (columnIds.length > 0) {
      let currentSlice = {
        istart: columnIndexes[columnIds[0]],
        weight: 0,
        iend: columnIndexes[columnIds[0]],
        columnIds: [] as number[],
      }
      forEach(columnIds, (colId, i) => {
        const colProps = find(props.columns, (col) => col.id == colId) as CalendarColumn
        if (columnIndexes[colId] === currentSlice.iend) {
          currentSlice.weight += colProps.weight
          currentSlice.iend = columnIndexes[colId] + 1
          currentSlice.columnIds.push(colId)
        } else {
          spans.push({ istart: currentSlice.istart, weight: currentSlice.weight, columnIds: currentSlice.columnIds })
          currentSlice = {
            istart: columnIndexes[colId],
            weight: colProps.weight,
            iend: columnIndexes[colId] + 1,
            columnIds: [colId],
          }
        }
      })
      spans.push({ istart: currentSlice.istart, weight: currentSlice.weight, columnIds: currentSlice.columnIds })
    }

    // Created as InputCalendarEvent
    const cnewEvent = newEvent as any
    // Changing properties to convert to an CalendarEvent
    delete cnewEvent.columnIds
    cnewEvent.spans = spans

    newEvents.push(cnewEvent as CalendarEvent)
  })
  const newEventsUpdated: CalendarEvent[] = updateEventsOverlap(newEvents)
  if (props.dropzones)
    props.dropzones.forEach((dz) => {
      newEventsUpdated.push(dz)
    })
  // sort by date
  newEventsUpdated.forEach((event) => {
    if (!map.has(event.data.start.date)) {
      map.set(event.data.start.date, [])
    }
    map.get(event.data.start.date)!.push(event)
  })
  return map
})

const totalWeight = computed(() => {
  return sumBy(props.columns, (c: CalendarColumn) => c.weight)
})

/**
 *
 * DRAG AND DROP MANAGEMENT
 *
 */

/**
 * Reactive variables to track the drag process
 * @param isDragging tracks when drag starts and stops
 * @param currentTime tracks the date and time of the
 * * position of the cursor
 * @param eventDragged refers to the event data that
 * * is being dragged at the start of the drag process
 */
const isDragging = ref(false)
const currentTime = ref<TimestampOrNull>(null)
const eventDragged = ref<CalendarEvent>()
let minutesToStartEvent: number = 0
let minutesToPixelRate: number

/**
 * V-MODEL IMPLEMENTATION OF EVENTS
 */
const eventsModel = computed({
  get() {
    return props.events
  },
  set(value: InputCalendarEvent[]) {
    emits('update:events', value)
  },
})

/**
 * Only returns the dropZone with the same ID as the event dragged
 */
const dropZoneToDisplay = computed((): CalendarEvent[] | undefined => {
  return filter(
    props.dropzones,
    (e) =>
      e.data.dataType === 'dropzone' &&
      currentTime.value?.date === e.data.start.date &&
      eventDragged.value?.id === e.data.dataId
  )
})

/**
 * Computes the closest start time from the props.dropzoneEvents
 * @trigger currentTime The Timestamp object giving us the date and time where the mouse is
 */
const closestStartTime = computed(() => {
  let closest: string = ''
  if (!currentTime.value || !dropZoneToDisplay.value || dropZoneToDisplay.value.length < 1) return closest
  let i = 0
  let timeDiff: number = 0
  while (i < dropZoneToDisplay.value.length) {
    let currentDiff: number = 0
    if (i === 0) {
      timeDiff = Math.abs(diffTimestamp(dropZoneToDisplay.value[i].data.start, currentTime.value, false))
      closest = dropZoneToDisplay.value[i].data.start.time
    } else {
      currentDiff = Math.abs(diffTimestamp(dropZoneToDisplay.value[i].data.start, currentTime.value, false))
      if (timeDiff > currentDiff) {
        timeDiff = currentDiff
        closest = dropZoneToDisplay.value[i].data.start.time
      }
    }
    i = i + 1
  }
  return closest
})

/**
 * Update the dropZone data and set to true the closest one from the mouse
 * during the drag.
 * Uses the computed value calculating the time string of the closest
 * possibleStartTime.
 * @param dateTime The date referring to the day in which we are
 */
function dropZoneCloseUpdate(dateTime: Timestamp): void {
  if (!dropZoneToDisplay.value || dropZoneToDisplay.value.length < 1) return
  dropZoneToDisplay.value.forEach((cdze) => {
    if (cdze.data.start.time === closestStartTime.value && cdze.data.start.date == dateTime.date) {
      cdze.toggled = true
    } else {
      cdze.toggled = false
    }
  })
}

/**
 * Compute the current time of the mouse y position
 * @param dateTime the data concerning the day and the time when the parent element starts
 * @param layerY The position of the mouse on the Y-axis from the start of the parent element
 */
function currentTimeUpdate(dateTime: Timestamp, layerY: number): void {
  if (dateTime) {
    if (!currentTime.value || currentTime.value.date !== dateTime.date)
      currentTime.value = copyTimestamp(dateTime) as TimestampOrNull
    if (!minutesToPixelRate) minutesToPixelRate = 1000 / calendar.value!.timeDurationHeight(1000)
    updateMinutes(
      currentTime.value as Timestamp,
      Math.round(parseTime(dateTime.time) + layerY * minutesToPixelRate - minutesToStartEvent)
    )
  }
}

/**
 * Function called when the drag event is triggered, set isDragging and eventDragged refs
 * @param browserEvent The HTML triggered event
 * @param event The event we are currently dragging
 */
function onDragStart(browserEvent: DragEvent & { layerY: number }, event: CalendarEvent) {
  minutesToStartEvent = browserEvent.layerY * minutesToPixelRate
  currentTime.value = copyTimestamp(event.data.start) as TimestampOrNull
  isDragging.value = true
  eventDragged.value = cloneDeep(event)
  emits('dragstart', event.id, getAllEvents())
}

function getAllEvents(): CalendarEvent[] {
  const allEvents: CalendarEvent[] = []
  eventsByDate.value.forEach((events: CalendarEvent[], date: string) => {
    events.forEach((ev) => {
      if (ev.data.dataType === 'event') allEvents.push(ev)
    })
  })
  return allEvents
}

function onDragEnter(e: any, type: string, scope: { timestamp: Timestamp }): boolean {
  currentTimeUpdate(scope.timestamp, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return true
}

/**
 * Function called when the dragOver event is triggered, computes the current mouse position
 * time and update the closest dropZone
 * @param e the mouse event triggered with data of the DOM object in it
 * @param type the type of element of the calendar
 * @param scope context containing utilitary functions
 */
function onDragOver(e: any, type: string, scope: { timestamp: Timestamp }) {
  e.preventDefault()
  currentTimeUpdate(scope.timestamp, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return true
}

function onDragLeave(e: any, type: string, scope: { timestamp: Timestamp }) {
  currentTimeUpdate(scope.timestamp, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return false
}

function onDragStop() {
  updateEventDropped()
  isDragging.value = false
  return false
}

/**
 * Function called when the drag event stops
 * Update the v-model of the events with a
 * * copy updated of the event changed
 */
function updateEventDropped(): void {
  if (!currentTime.value) {
    console.log('ERREUR CURRENT TIME')
    return
  }
  if (!eventDragged.value || eventDragged.value.data.dataType !== 'event') {
    console.log("I don't know what happened: Maybe it was an availability")
    return
  }
  const newEvent: InputCalendarEvent = cloneDeep(
    eventsModel.value.find((e) => eventDragged.value?.id === e.id) as InputCalendarEvent
  )
  if (dropZoneToDisplay.value) {
    dropZoneToDisplay.value.forEach((cdze) => {
      if (cdze.toggled) {
        newEvent.data.start = copyTimestamp(cdze.data.start)
      }
    })
  } else {
    console.log('NO DROPZONE FOR THIS EVENT OU ERREUR DE DROPZONE')
  }
  emits('update:events', [newEvent])
}

/**
 * Functions relative to the navigation-bar
 */
// I still have issues with the doc
// I found this QCalendar here: https://github.com/quasarframework/quasar-ui-qcalendar/releases/tag/v2.2.1

function onToday(): void {
  calendar.value?.moveToToday()
}
function onPrev(): void {
  calendar.value?.prev()
}
function onNext(): void {
  calendar.value?.next()
}

/**
 * Functions for onclick management
 */
let timeoutId: any = null
let currentAvailId: number = -1
let newAvailDuration: number = 0
let oldAvailDuration: number = 0

function onMouseDown(mouseEvent: MouseEvent, eventId: number): void {
  if (!minutesToPixelRate) minutesToPixelRate = 1000 / calendar.value!.timeDurationHeight(1000)
  const target = mouseEvent.target
  if (target instanceof HTMLElement) {
    const targetChild = target.firstElementChild
    if (mouseEvent.button === 0) {
      if (target.classList.contains('avail')) {
        onAvailClick(mouseEvent, eventId)
      } else if (target.classList.contains('event') || targetChild?.classList.contains('event')) {
        const dataId = eventsModel.value.find((ev) => ev.id === eventId)?.data.dataId
        if (dataId) emits('event:details', dataId)
      } else if (target.classList.contains('event-span') && targetChild?.classList.contains('avail')) {
        currentAvailId = eventId
        availResizeObs.observe(target as Element)
      } else if (targetChild?.classList.contains('avail')) {
        onAvailClick(mouseEvent, eventId)
      }
    }
  }
}

function nextAvailInTime(
  avail: InputCalendarEvent,
  updatedEvents: InputCalendarEvent[]
): InputCalendarEvent | undefined {
  let nextAvail = updatedEvents.find((e) => {
    return (
      e.data.start.date === avail.data.start.date &&
      parseTime(e.data.start) === parseTime(avail.data.start) + avail.data.duration &&
      e.data.dataType === 'avail'
    )
  })
  if (!nextAvail) {
    nextAvail = eventsModel.value.find((e) => {
      return (
        e.data.start.date === avail.data.start.date &&
        parseTime(e.data.start) === parseTime(avail.data.start) + avail.data.duration &&
        e.data.dataType === 'avail'
      )
    })
  }
  return nextAvail
}

function allNextAvailWithSameValue(
  avail: InputCalendarEvent,
  updatedEvents: InputCalendarEvent[]
): InputCalendarEvent[] {
  const nextAvails: InputCalendarEvent[] = []
  let nextAvail: InputCalendarEvent | undefined = nextAvailInTime(avail, updatedEvents)
  while (nextAvail && nextAvail.data.value === avail.data.value) {
    nextAvails.push(nextAvail)
    nextAvail = nextAvailInTime(nextAvail, updatedEvents)
  }
  return nextAvails
}

function onMouseUp(): void {
  availResizeObs.disconnect()
  if (currentAvailId !== -1) {
    const newEvent: InputCalendarEvent = cloneDeep(
      eventsModel.value.find((e) => currentAvailId === e.id) as InputCalendarEvent
    )
    if (newEvent) {
      const newEventsToUpdate: InputCalendarEvent[] = updateResizedEvent(newEvent)
      if (
        oldAvailDuration === newAvailDuration &&
        parseTime(newEvent.data.start.time) + newAvailDuration === props.endOfDay
      ) {
        emits('update:events', newEventsToUpdate)
        currentAvailId = -1
        return
      }
      if (oldAvailDuration !== newAvailDuration) {
        const bigger: boolean = newAvailDuration - oldAvailDuration > 0
        if (bigger) {
          updateResizedUpEvents(eventsModel.value, newEvent).forEach((ev) => {
            newEventsToUpdate.push(ev)
          })
          // Checking if nextAvail has same value and then combining both if that's so
          const nextAvails: InputCalendarEvent[] = allNextAvailWithSameValue(newEvent, newEventsToUpdate)
          if (nextAvails) {
            nextAvails.forEach((nextAv) => {
              newEvent.data.duration! += nextAv.data.duration!
              nextAv.data.duration = -1
            })
          }
        } else {
          const updatedDownEvent = updateResizedDownEvents(eventsModel.value, newEvent)
          if (updatedDownEvent) {
            newEventsToUpdate.push(updatedDownEvent)
          }
        }
        emits('update:events', newEventsToUpdate)
      }
    }
    currentAvailId = -1
  }
}

function onAvailClick(mouseEvent: MouseEvent & { layerY: number }, eventId: number): void {
  if (mouseEvent.button === 0) {
    if (!timeoutId) {
      timeoutId = setTimeout(() => {
        changeAvailValue(eventId)
        clearTimeout(timeoutId)
        timeoutId = null
      }, 200)
    } else {
      // DoubleClick management
      clearTimeout(timeoutId)
      timeoutId = null
      const firstAvail = cloneDeep(eventsModel.value.find((e) => e.id === eventId))
      if (firstAvail) {
        if (firstAvail.data.duration! > (props.step || STEP_DEFAULT)) {
          const secondAvail = cloneDeep(firstAvail)
          const layerY: number = mouseEvent.layerY
          firstAvail.data.duration = closestStep(minutesToPixelRate * layerY, props.step)
          updateMinutes(
            secondAvail.data.start,
            parseTime(firstAvail!.data.start) + closestStep(minutesToPixelRate * layerY, props.step)
          )
          secondAvail.id = -1
          secondAvail.data.duration! -= firstAvail.data.duration
          emits('update:events', [firstAvail, secondAvail])
        }
      }
    }
  }
}

function changeAvailValue(eventId: number, value?: number): void {
  const newEvent: InputCalendarEvent | undefined = cloneDeep(
    eventsModel.value.find((ev: InputCalendarEvent) => ev.id == eventId)
  )
  if (newEvent !== undefined && newEvent.data.dataType === 'avail') {
    if (value || value === 0) {
      newEvent.data.value = value
    } else {
      if (newEvent.data.value! < 3) {
        newEvent.data.value = 3
      } else if (newEvent.data.value! >= 3 && newEvent.data.value! < 6) {
        newEvent.data.value = 6
      } else if (newEvent.data.value! >= 6 && newEvent.data.value! < 8) {
        newEvent.data.value = 8
      } else {
        newEvent.data.value = 0
      }
    }
    emits('update:events', [newEvent])
  }
}

/**
 * AVAIL REZISE MANAGEMENT
 */
const availResizeObs = new ResizeObserver((entries) => {
  if (calendar.value?.timeDurationHeight) {
    newAvailDuration = entries[0].contentRect.height * minutesToPixelRate
  }
})

/**
 * We update the resized event. We take care of cases when we tried to
 * resize it above end of day time && when we resize down the last event
 * of the day to create another one.
 */
function updateResizedEvent(newEvent: InputCalendarEvent): InputCalendarEvent[] {
  oldAvailDuration = newEvent.data.duration as number
  const newEventsToUpdate: InputCalendarEvent[] = []
  let newEnd = parseTime(newEvent.data.start) + newAvailDuration
  if (newEnd > props.endOfDay) newEnd = props.endOfDay
  else if (
    oldAvailDuration > newAvailDuration &&
    parseTime(newEvent.data.start) + oldAvailDuration === props.endOfDay
  ) {
    const newAvail: InputCalendarEvent = cloneDeep(newEvent)
    updateMinutes(newAvail.data.start, closestStep(newEnd, props.step))
    newAvail.id = -1
    newAvail.data.duration = props.endOfDay - closestStep(newEnd, props.step)
    if (newAvail.data.duration > 0) newEventsToUpdate.push(newAvail)
  }
  newEvent.data.duration = closestStep(newEnd, props.step) - parseTime(newEvent.data.start)
  newAvailDuration = newEvent.data.duration
  if (newAvailDuration !== 0) newEventsToUpdate.push(newEvent)
  return newEventsToUpdate
}

function updateResizedUpEvents(newEvents: InputCalendarEvent[], newEvent: InputCalendarEvent): InputCalendarEvent[] {
  const availsToUpdate: InputCalendarEvent[] = []
  newEvents.forEach((currentEvent: InputCalendarEvent) => {
    if (currentEvent.data.dataType === 'avail' && newEvent.id !== currentEvent.id) {
      if (newEvent.data.start.date === currentEvent.data.start.date) {
        const diffBetweenStarts = diffTimestamp(newEvent.data.start, currentEvent.data.start) / 60000
        if (diffBetweenStarts > 0 && diffBetweenStarts < newEvent.data.duration!) {
          availsToUpdate.push(cloneDeep(currentEvent))
        }
      }
    }
  })
  for (let k = 0; k < availsToUpdate.length; k++) {
    const diffBetweenStarts = diffTimestamp(newEvent.data.start, availsToUpdate[k].data.start) / 60000
    if (diffBetweenStarts + availsToUpdate[k].data.duration! <= newEvent.data.duration!) {
      availsToUpdate[k].data.duration = -1
    } else {
      let oldTimeAvail = parseTime(getTime(availsToUpdate[k].data.start))
      updateMinutes(
        availsToUpdate[k].data.start,
        Math.round(parseTime(newEvent.data.start.time) + newEvent.data.duration)
      )
      availsToUpdate[k].data.duration! -= parseTime(getTime(availsToUpdate[k].data.start)) - oldTimeAvail
    }
  }
  return availsToUpdate
}

function updateResizedDownEvents(
  newEvents: InputCalendarEvent[],
  newEvent: InputCalendarEvent
): InputCalendarEvent | undefined {
  const mins = Math.round(parseTime(newEvent.data.start) + newAvailDuration)
  let availToUpdate: InputCalendarEvent | undefined
  let i = 0
  while (!availToUpdate && i < newEvents.length) {
    if (
      newEvents[i].data.dataType === 'avail' &&
      newEvent.id !== newEvents[i].id &&
      newEvent.data.start.date === newEvents[i].data.start.date &&
      parseTime(newEvents[i].data.start) === parseTime(newEvent.data.start) + oldAvailDuration
    ) {
      availToUpdate = cloneDeep(newEvents[i])
    }
    i++
  }
  if (availToUpdate) {
    updateMinutes(availToUpdate.data.start, mins)
    availToUpdate.data.duration! += oldAvailDuration - newAvailDuration
    return availToUpdate
  }
}
</script>

<style lang="sass" scoped>
.calendar-div
  width: 100%
.event-span
  position: absolute
  font-size: 12px
  justify-content: center
  margin: 0 1px
  text-overflow: ellipsis
  overflow: hidden
  cursor: pointer
.title
  position: relative
  display: flex
  flex-direction: column
  justify-content: center
  align-items: center
  height: 100%
.border-dashed
  border: 1px dashed grey
.my-dropzone
  pointer-events: none
.header
  display: flex
  justify-content: flex-start
.header span
  min-width: 40%
.header button
  padding: 1px
  margin: 3px
</style>
