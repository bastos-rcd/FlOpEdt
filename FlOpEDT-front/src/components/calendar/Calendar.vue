<template>
  <div class="row justify-center">
    <div class="q-pa-md q-gutter-sm row">
      <q-btn no-caps class="button" style="margin: 2px" @click="onToday"> Today </q-btn>
      <q-btn no-caps class="button" style="margin: 2px" @click="onPrev"> &lt; Prev </q-btn>
      <q-btn no-caps class="button" style="margin: 2px" @click="onNext"> Next &gt; </q-btn>
    </div>
    <div class="q-pa-md q-gutter-sm row">
      <q-btn-dropdown class="glossy" color="blue" style="margin: 2px">
        <q-list>
          <q-item clickable v-close-popup @click=";[weekdays, typeCalendar] = [[1, 2, 3, 4, 5, 6, 0], 'week']">
            <q-item-section>
              <q-item-label>Full Week</q-item-label>
            </q-item-section>
          </q-item>

          <q-item clickable v-close-popup @click=";[weekdays, typeCalendar] = [[1, 2, 3, 4, 5], 'week']">
            <q-item-section>
              <q-item-label>Monday to Friday</q-item-label>
            </q-item-section>
          </q-item>

          <q-item v-close-popup>
            <q-item-section>
              <q-item-label>Select a day</q-item-label>
              <q-btn-group push>
                <q-btn push label="Monday" @click=";[weekdays, typeCalendar] = [[1], 'day']" />
                <q-btn push label="Tuesday" @click=";[weekdays, typeCalendar] = [[2], 'day']" />
                <q-btn push label="Wednesday" @click=";[weekdays, typeCalendar] = [[3], 'day']" />
                <q-btn push label="Thursday" @click=";[weekdays, typeCalendar] = [[4], 'day']" />
                <q-btn push label="Friday" @click=";[weekdays, typeCalendar] = [[5], 'day']" />
                <q-btn push label="Saturday" @click=";[weekdays, typeCalendar] = [[6], 'day']" />
                <q-btn push label="Sunday" @click=";[weekdays, typeCalendar] = [[0], 'day']" />
              </q-btn-group>
            </q-item-section>
          </q-item>
          <q-item v-close-popup>
            <q-item-section>
              <q-item-label>Select a day</q-item-label>
              <q-range :marker-labels="arrayWeekdaysLabel" :min="1" :max="7" label-always v-model="dayStart" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </div>
  </div>
  <div style="display: flex; max-width: 100%; width: 100%; height: 100%">
    <q-calendar-day
      ref="calendar"
      v-model="selectedDate"
      :selected-dates="selectedDates"
      :view="typeCalendar"
      bordered
      hoverable
      animated
      transition-next="slide-left"
      transition-prev="slide-right"
      no-active-date
      :interval-start="26"
      :interval-count="52"
      :interval-minutes="15"
      :interval-height="28"
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
        <template v-for="event in eventsByDate[timestamp.date]" :key="event.id">
          <template
            v-if="
              event.data.duration !== undefined &&
              (event.data.dataType === 'event' ||
                event.data.dataType === 'avail' ||
                (isDragging && event.data.dataId === eventDragged?.data.dataId))
            "
          >
            <div :draggable="event.data.dataType !== 'avail'" @dragstart="onDragStart($event, event)">
              <div
                v-for="spans in event.spans"
                :key="event.id"
                class="my-event"
                :class="badgeClasses(event.data.dataType, event.bgcolor)"
                :style="badgeStyles(event, spans, timeStartPos)"
                @mousedown="onMouseDown($event, event.id)"
                @mouseup="onMouseUp()"
                @mouseover="onAvailMouseOver($event, event.id)"
              >
                <slot name="event" :event="event">
                  <span v-if="event.data.dataType !== 'avail'" class="title q-calendar__ellipsis">
                    {{ event.title }}
                  </span>
                  <div
                    v-else
                    style="width: 100%; height: 100%; flex-direction: column; align-items: center; display: flex"
                    class="avail"
                  >
                    <div style="flex: 2; display: flex; align-items: center" class="avail">
                      <q-popup-edit v-model="newAvailValue" v-slot="scope" anchor="bottom left" context-menu>
                        <q-btn-group style="display: flex; flex-direction: column">
                          <q-btn
                            v-for="(icon, index) in availabilityData.icon"
                            :style="availMenuStyle(index)"
                            :icon="icon"
                            size="sm"
                            @click="changeAvail(event.id, parseInt(index))"
                          />
                        </q-btn-group>
                      </q-popup-edit>
                      <q-icon color="black" :name="event.icon" size="xs" />
                    </div>
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

import _ from 'lodash'

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
  relativeDays,
} from '@quasar/quasar-ui-qcalendar'
import { watch } from 'vue'
import { availabilityData } from './declaration'
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
  dropzones?: InputCalendarEvent[]
  columns: CalendarColumn[]
  endOfDayMinutes: number
  step?: number
  availEdition?: boolean
}>()

const STEP_DEFAULT: number = 15

const emits = defineEmits<{
  (e: 'dragstart', id: number): void
  (e: 'update:events', value: InputCalendarEvent[]): void
  (e: 'update:week', value: Timestamp): void
  (e: 'weekdays', value: number[]): void
}>()

const preWeight = computed(() => {
  const map: Record<number, number> = {}
  let preceeding = 0
  _.forEach(props.columns, (col: CalendarColumn) => {
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
  updateFormatted(relativeDays(parseTimestamp(today())!, prevDay, parseTimestamp(today())!.weekday - 1 || 6)).date
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
const arrayWeekdaysLabel = [
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' },
  { value: 7, label: 'Sunday' },
]
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
    if (_.includes(weekdays.value, now_date?.weekday)) {
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
  const map: Record<string, CalendarEvent[]> = {}
  let allEvents: InputCalendarEvent[] = props.events
  // Copy of events
  const newEvents: CalendarEvent[] = []
  // Dict of column ids keys to their index
  const columnIndexes: Record<number, number> = {}
  _.forEach(props.columns, (c, i) => {
    columnIndexes[c.id] = i
  })
  if (props.dropzones) allEvents = _.concat(allEvents, props.dropzones)
  allEvents.forEach((event) => {
    const newEvent = _.cloneDeep(event)
    let columnIds = newEvent.columnIds

    // availability column
    if (newEvent.data.dataType === 'avail') {
      newEvent.bgcolor = availabilityData.color[newEvent.data.value?.toString() || '0']
      newEvent.icon = availabilityData.icon[newEvent.data.value?.toString() || '0']
    }

    // filter out absent columns
    _.remove(columnIds, (colId) => !(colId in columnIndexes))

    // merge columns
    columnIds = _.sortBy(columnIds, (colId) => columnIndexes[colId])

    const spans: Array<{ istart: number; weight: number; columnIds: number[] }> = []
    if (columnIds.length > 0) {
      let currentSlice = {
        istart: columnIndexes[columnIds[0]],
        weight: 0,
        iend: columnIndexes[columnIds[0]],
        columnIds: [] as number[],
      }
      _.forEach(columnIds, (colId, i) => {
        const colProps = _.find(props.columns, (col) => col.id == colId) as CalendarColumn
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
  // sort by date
  const newEventsUpdated: CalendarEvent[] = updateEventsOverlap(newEvents)
  newEventsUpdated.forEach((event) => {
    if (!map[event.data.start.date]) {
      map[event.data.start.date] = []
    }
    map[event.data.start.date].push(event)
  })
  return map
})

function columnsInCommon(event1: CalendarEvent, event2: CalendarEvent): boolean {
  const cols1 = event1.spans.map((span) => span.columnIds).flat()
  const cols2 = event2.spans.map((span) => span.columnIds).flat()
  return _.intersection(cols1, cols2).length !== 0
}

function updateEventsOverlap(events: CalendarEvent[]): CalendarEvent[] {
  const newEvents: CalendarEvent[] = events
  for (let i = 0; i < newEvents.length; i++) {
    if (newEvents[i].toggled) {
      for (let k = 0; k < newEvents.length; k++) {
        if (i !== k && (k > i || !newEvents[k].toggled)) {
          const sameColumns = columnsInCommon(newEvents[i], newEvents[k])
          if (newEvents[i].data.dataType === newEvents[k].data.dataType && sameColumns) {
            const diff = Math.ceil(diffTimestamp(newEvents[i].data.start, newEvents[k].data.start) / 1000 / 60)
            if (diff > 0) {
              if (newEvents[i].data.duration! > diff) {
                newEvents[i].toggled = newEvents[k].toggled = false
              }
            } else {
              if (newEvents[k].data.duration! > Math.abs(diff)) {
                newEvents[i].toggled = newEvents[k].toggled = false
              }
            }
          }
        }
      }
    }
  }
  return newEvents
}

const totalWeight = computed(() => {
  return _.sumBy(props.columns, (c: CalendarColumn) => c.weight)
})

function badgeClasses(type: 'event' | 'dropzone' | 'header' | 'avail', bgcolor?: string, toggled?: boolean) {
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
function badgeStyles(
  event: CalendarEvent,
  span: { istart: number; weight: number; columnIds: number[] },
  timeStartPos: any = undefined
) {
  // const currentColumn = columnsToDisplay.value.find((c) => displayData.columnId == c.id)
  // if (!currentColumn) return undefined
  const preceedingWeight = preWeight.value[props.columns[span.istart].id]

  const s: Record<string, string> = {
    top: '',
    height: '',
  }
  if (!event.toggled) {
    s['opacity'] = '0.5'
  }
  if (timeStartPos) {
    s.top = timeStartPos(event.data?.start) + 'px'
    s.left = Math.round((preceedingWeight / totalWeight.value) * 100) + '%'
    s.width = Math.round((100 * span.weight) / totalWeight.value) + '%'
    s.height = calendar.value!.timeDurationHeight(event.data?.duration) + 'px'
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
    event.data.start.time === closestStartTime.value &&
    event.data.start.date === currentTime.value?.date
  ) {
    s['border-color'] = 'green'
    s['border-width'] = '3px'
  }
  s['align-items'] = 'flex-start'
  return s
}

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
const dropZoneToDisplay = computed((): InputCalendarEvent[] | undefined => {
  return _.filter(
    props.dropzones,
    (e) =>
      e.data.dataType === 'dropzone' &&
      currentTime.value?.date === e.data.start.date &&
      eventDragged.value?.data.dataId === e.data.dataId
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
function onDragStart(browserEvent: DragEvent, event: CalendarEvent) {
  //@ts-expect-error
  minutesToStartEvent = browserEvent.layerY! * minutesToPixelRate
  currentTime.value = copyTimestamp(event.data.start) as TimestampOrNull
  isDragging.value = true
  eventDragged.value = _.cloneDeep(event)
  emits('dragstart', event.data.dataId)
  if (!browserEvent.dataTransfer) return
  browserEvent.dataTransfer.dropEffect = 'copy'
  browserEvent.dataTransfer.effectAllowed = 'move'
  browserEvent.dataTransfer.setData('ID', event.data.dataId.toString())
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
  const newEvent: InputCalendarEvent = _.cloneDeep(
    props.events.find((e) => eventDragged.value?.id === e.id) as InputCalendarEvent
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
  const newEvents: InputCalendarEvent[] = _.cloneDeep(props.events)
  _.remove(newEvents, (e: InputCalendarEvent) => {
    return e.id === newEvent.id
  })
  newEvents.push(newEvent)
  eventsModel.value = newEvents
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

let newAvailValue: number = 0
let timeoutId: any = null
let currentAvailId: number = -1
let newAvailDuration: number = 0
let oldAvailDuration: number = 0
const selectedItems: InputCalendarEvent[] = []
let selectionAvail: Ref<boolean> = ref(false)

const availResizeObs = new ResizeObserver((entries) => {
  if (calendar.value?.timeDurationHeight) {
    newAvailDuration = entries[0].contentRect.height * minutesToPixelRate
  }
})

/**
 * AVAIL REZISE MANAGEMENT
 */

function updateResizedEvent(newEvent: InputCalendarEvent): InputCalendarEvent[] {
  oldAvailDuration = newEvent.data.duration as number
  const newEvents: InputCalendarEvent[] = _.cloneDeep(props.events)
  let newEnd = parseTime(newEvent.data.start) + newAvailDuration
  if (newEnd > props.endOfDayMinutes * 60) newEnd = props.endOfDayMinutes * 60
  else if (
    oldAvailDuration > newAvailDuration &&
    parseTime(newEvent.data.start) + oldAvailDuration === props.endOfDayMinutes * 60
  ) {
    const newAvail: InputCalendarEvent = _.cloneDeep(newEvent)
    updateMinutes(newAvail.data.start, closestStep(newEnd, props.step))
    newAvail.id = nextId()
    newAvail.data.duration = props.endOfDayMinutes * 60 - closestStep(newEnd, props.step)
    newEvents.push(newAvail)
  }
  newEvent.data.duration = closestStep(newEnd, props.step) - parseTime(newEvent.data.start)
  newAvailDuration = newEvent.data.duration
  _.remove(newEvents, (e: InputCalendarEvent) => {
    return e.id === newEvent.id
  })
  if (newAvailDuration !== 0) newEvents.push(newEvent)
  return newEvents
}

function updateResizedUpEvents(newEvents: InputCalendarEvent[], newEvent: InputCalendarEvent): void {
  const idAvailsToUpdate: number[] = []
  let oldDurationTotal: number = 0
  newEvents.forEach((currentEvent: InputCalendarEvent) => {
    if (currentEvent.data.dataType === 'avail' && newEvent.id !== currentEvent.id) {
      if (newEvent.data.start.date === currentEvent.data.start.date) {
        const diffBetweenStarts = diffTimestamp(newEvent.data.start, currentEvent.data.start) / 60000
        if (diffBetweenStarts > 0 && diffBetweenStarts < newEvent.data.duration!) {
          idAvailsToUpdate.push(currentEvent.id)
        }
      }
    }
  })
  for (let k = 0; k < idAvailsToUpdate.length; k++) {
    const availToUpdate = _.cloneDeep(newEvents.find((e: InputCalendarEvent) => e.id === idAvailsToUpdate[k]))
    if (availToUpdate) {
      const diffBetweenStarts = diffTimestamp(newEvent.data.start, availToUpdate!.data.start) / 60000
      oldDurationTotal += availToUpdate.data.duration!
      if (diffBetweenStarts + availToUpdate.data.duration! <= newEvent.data.duration!) {
        _.remove(newEvents, (e: InputCalendarEvent) => {
          return e.id === idAvailsToUpdate[k]
        })
      } else {
        let oldTimeAvail = parseTime(getTime(availToUpdate.data.start))
        updateMinutes(
          availToUpdate?.data.start,
          Math.round(parseTime(newEvent.data.start.time) + newEvent.data.duration)
        )
        availToUpdate.data.duration! -= parseTime(getTime(availToUpdate.data.start)) - oldTimeAvail
        _.remove(newEvents, (e: InputCalendarEvent) => {
          return e.id === availToUpdate!.id
        })
        newEvents.push(availToUpdate!)
      }
    }
  }
}

function updateResizedDownEvents(newEvents: InputCalendarEvent[], newEvent: InputCalendarEvent) {
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
      availToUpdate = _.cloneDeep(newEvents[i])
    }
    i++
  }
  if (availToUpdate) {
    updateMinutes(availToUpdate.data.start, mins)
    availToUpdate.data.duration! += oldAvailDuration - newAvailDuration
    _.remove(newEvents, (e) => e.id === availToUpdate!.id)
    newEvents.push(availToUpdate)
  }
}

function isItOnStep(nbMinutes: number, step: number = STEP_DEFAULT): boolean {
  return nbMinutes % step === 0
}

function closestStep(nbMinutes: number, step: number = STEP_DEFAULT): number {
  if (!isItOnStep(nbMinutes)) {
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

function onMouseDown(mouseEvent: MouseEvent, eventId: number): void {
  if (!minutesToPixelRate) minutesToPixelRate = 1000 / calendar.value!.timeDurationHeight(1000)
  //@ts-expect-error
  if (_.includes(mouseEvent.target.className, 'avail') || _.includes(_.words(mouseEvent.target.className), 'SVG'))
    onAvailClick(mouseEvent, eventId)
  //@ts-expect-error
  else if (!_.includes(mouseEvent.target.className, 'title')) {
    if (mouseEvent.target) {
      availResizeObs.observe(mouseEvent.target as Element)
      currentAvailId = eventId
    }
  }
}

function onAvailClick(mouseEvent: MouseEvent, eventId: number): void {
  if (mouseEvent.button === 0) {
    if (!timeoutId) {
      timeoutId = setTimeout(() => {
        if (!props.availEdition) changeAvail(eventId)
        else {
          const availSelected = props.events.find((e) => e.id === eventId)
          selectionAvail.value = true
          selectedItems.push(availSelected!)
          availSelected!.toggled = false
        }
        clearTimeout(timeoutId)
        timeoutId = null
      }, 200)
    } else {
      // DoubleClick management
      clearTimeout(timeoutId)
      timeoutId = null
      const firstAvail = _.cloneDeep(props.events.find((e) => e.id === eventId))
      if (firstAvail) {
        if (firstAvail.data.duration! > (props.step || STEP_DEFAULT)) {
          const secondAvail = _.cloneDeep(firstAvail)
          const allEvents = _.cloneDeep(props.events)
          //@ts-expect-error
          const layerY = mouseEvent.layerY
          firstAvail!.data.duration = closestStep(minutesToPixelRate * layerY, props.step)
          updateMinutes(
            secondAvail.data.start,
            parseTime(firstAvail!.data.start) + closestStep(minutesToPixelRate * layerY, props.step)
          )
          secondAvail.id = nextId()
          secondAvail.data.duration! -= firstAvail.data.duration
          _.remove(allEvents, (e: InputCalendarEvent) => e.id === firstAvail!.id)
          allEvents.push(firstAvail, secondAvail)
          eventsModel.value = allEvents
        }
      }
    }
  }
}

function onAvailMouseOver(event: Event, eventId: number): void {
  //@ts-expect-error
  if (selectionAvail.value && _.includes(event.target.className, 'avail')) console.log('Hey ', eventId)
}

function onMouseUp(): void {
  selectionAvail.value = false
  if (currentAvailId !== -1) {
    availResizeObs.disconnect()
    const newEvent: InputCalendarEvent = _.cloneDeep(
      props.events.find((e) => currentAvailId === e.id) as InputCalendarEvent
    )
    if (newEvent) {
      const newEvents: InputCalendarEvent[] = updateResizedEvent(newEvent)
      if (
        oldAvailDuration === newAvailDuration &&
        parseTime(newEvent.data.start.time) + newAvailDuration === props.endOfDayMinutes * 60
      ) {
        eventsModel.value = newEvents
        currentAvailId = -1
        return
      }
      const bigger: boolean = newAvailDuration - oldAvailDuration > 0
      if (bigger) {
        updateResizedUpEvents(newEvents, newEvent)
        const nextAvail: InputCalendarEvent | undefined = newEvents.find((e) => {
          return (
            e.data.start.date === newEvent.data.start.date &&
            parseTime(e.data.start) === parseTime(newEvent.data.start) + newEvent.data.duration &&
            e.data.dataType === 'avail'
          )
        })
        if (nextAvail && nextAvail.data.value === newEvent.data.value) {
          newEvent.data.duration! += nextAvail.data.duration!
          _.remove(newEvents, (e) => e.id === nextAvail.id)
        }
      } else {
        updateResizedDownEvents(newEvents, newEvent)
      }
      eventsModel.value = newEvents
    }
    currentAvailId = -1
  }
}

let idAvail = 900

function nextId(): number {
  return idAvail++
}

function changeAvail(eventId: number, value?: number): void {
  const newEvent: InputCalendarEvent | undefined = _.cloneDeep(
    eventsModel.value.find((ev: InputCalendarEvent) => ev.id == eventId)
  )
  if (newEvent !== undefined && newEvent.data.dataType === 'avail') {
    const newEvents: InputCalendarEvent[] = _.cloneDeep(eventsModel.value)
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
    _.remove(newEvents, (e: InputCalendarEvent) => {
      return e.id === newEvent!.id
    })
    newEvents.push(newEvent)
    eventsModel.value = newEvents
  }
}

function availMenuStyle(index: string): any {
  return { 'background-color': availabilityData.color[index] }
}
</script>

<style lang="sass" scoped>
.my-event
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
  justify-content: center
  align-items: center
  height: 100%
.border-dashed
  border: 1px dashed grey
.my-dropzone
  pointer-events: none
</style>
