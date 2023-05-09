<template>
  <div style="display: flex; max-width: 100%; width: 100%; height: 100%">
    <q-calendar-day
      ref="calendar"
      v-model="selectedDate"
      view="week"
      bordered
      hoverable
      transition-next="slide-left"
      transition-prev="slide-right"
      no-active-date
      :interval-start="6"
      :interval-count="18"
      :interval-height="28"
      :weekdays="[1, 2, 3, 4, 5]"
      :drag-enter-func="onDragEnter"
      :drag-over-func="onDragOver"
      :drag-leave-func="onDragLeave"
      @dragend="onDragStop"
    >
      <template #head-day-event="{ scope: { timestamp } }">
        <div style="display: flex">
          <template v-for="column in props.columns" :key="column.name">
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
                'flex-basis': Math.round((100 * column.weight) / props.totalWeight) + '%',
                'align-items': 'center',
              }"
            >
              {{ column.name }}
            </div>
          </template>
        </div>
      </template>

      <template #day-body="{ scope: { timestamp, timeStartPos, timeDurationHeight } }">
        <!-- events to display -->
        <template v-for="event in eventsByDate[timestamp.date]" :key="event.id">
          <template v-if="event.data.duration !== undefined">
            <div draggable="true" @dragstart="onDragStart($event, event)">
              <div
                v-for="columnId in event.columnIds"
                :key="event.id + '_' + columnId"
                class="my-event"
                :class="badgeClasses('event', event.bgcolor)"
                :style="badgeStyles(event, columnId, timeStartPos, timeDurationHeight)"
              >
                <slot name="event" :event="event">
                  <span class="title q-calendar__ellipsis">
                    {{ event.title }}
                  </span>
                </slot>
              </div>
            </div>
          </template>
        </template>

        <!-- drop zone events to display -->
        <template
          v-if="
            dropZoneToDisplay &&
            isDragging &&
            dropZoneToDisplay.eventId !== -1 &&
            dropZoneToDisplay.possibleStarts[timestamp.date]
          "
          v-for="ts in dropZoneToDisplay.possibleStarts[timestamp.date]"
          :key="dropzoneEvents.eventId + '_' + timestamp.date + '_' + ts"
        >
          <div
            v-for="columnId in dropZoneToDisplay.columnIds"
            :key="dropZoneToDisplay.eventId + '_' + timestamp.date + '_' + ts.timeStart + '_' + columnId"
            class="my-dropzone my-event"
            :class="badgeClasses('dropzoneevent')"
            :style="
              badgeStyles(
                {
                  data: { start: ts.timeStart, duration: dropZoneToDisplay.duration, dataId: 0, dataType: 'dropzone' },
                },
                columnId,
                timeStartPos,
                timeDurationHeight
              )
            "
          ></div>
        </template>
      </template>
    </q-calendar-day>
  </div>
</template>

<script setup lang="ts">
import { QCalendarDay, addToDate, parseTimestamp, today } from '@quasar/quasar-ui-qcalendar/src/index.js'
import '@quasar/quasar-ui-qcalendar/src/QCalendarVariables.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarTransitions.sass'
import '@quasar/quasar-ui-qcalendar/src/QCalendarAgenda.sass'

import _ from 'lodash'

import { CalendarColumn, CalendarEvent, CalendarDropzoneEvent } from './declaration'

import { computed, ref } from 'vue'
import {
  Timestamp,
  TimestampOrNull,
  copyTimestamp,
  diffTimestamp,
  parseTime,
  updateMinutes,
} from '@quasar/quasar-ui-qcalendar'

/**
 * Data passed to the component to handle the display in
 * columns for each day
 * *  The dropzoneEvents have references of events ids and
 * *  the totaleWeight is the total of each columns weight
 */
const props = defineProps<{
  events: CalendarEvent[]
  columns: CalendarColumn[]
  totalWeight: number
  dropzoneEvents?: CalendarDropzoneEvent[]
}>()

const emits = defineEmits<{
  (e: 'dragstart', id: number): void
  (e: 'update:events', value: CalendarEvent[]): void
}>()

/**
 * QCalendar DATA TO DISPLAY
 * * Format the data from the events to match the calendar display,
 * * Functions to compute the style to render for each event
 */
const selectedDate = today()

const eventsByDate = computed(() => {
  const map: Record<string, any[]> = {}

  props.events.forEach((event) => {
    if (!map[event.data.start.date]) {
      map[event.data.start.date] = []
    }
    map[event.data.start.date].push(event)
    if (event.data.days) {
      let timestamp = parseTimestamp(event.data.start.date)
      let days = event.data.days
      do {
        timestamp = addToDate(timestamp, { day: 1 })
        if (!map[timestamp.date]) {
          map[timestamp.date] = []
        }
        map[timestamp.date].push(event)
      } while (--days > 0)
    }
  })
  return map
})

function badgeClasses(type: 'event' | 'dropzoneevent' | 'header', bgcolor?: string) {
  switch (type) {
    case 'event':
      return {
        [`text-white bg-${bgcolor}`]: true,
        'rounded-border': true,
      }
    case 'dropzoneevent':
      return 'border-dashed'
    case 'header':
      return {}
  }
}
function badgeStyles(
  event: Partial<CalendarEvent>,
  columnId: number,
  timeStartPos: any = undefined,
  timeDurationHeight: any = undefined
) {
  const currentGroup = props.columns.find((c) => c.id === columnId)

  if (!currentGroup) return undefined

  const s: Record<string, string> = {
    top: '',
    height: '',
    'background-color': event.bgcolor || 'transparent',
  }
  if (timeStartPos && timeDurationHeight) {
    s.top = timeStartPos(event.data?.start) + 'px'
    s.left = Math.round((currentGroup?.x / props.totalWeight) * 100) + '%'
    s.width = Math.round((100 * currentGroup.weight) / props.totalWeight) + '%'
    s.height = timeDurationHeight(event.data?.duration) + 'px'
  }
  if (
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
 * * is being dragged
 */
const isDragging = ref(false)
const currentTime = ref<TimestampOrNull>(null)
const eventDragged = ref<CalendarEvent>()

/**
 * V-MODEL IMPLEMENTATION OF EVENTS
 */
const eventsModel = computed({
  get() {
    return props.events
  },
  set(value: CalendarEvent[]) {
    emits('update:events', value)
  },
})

const dropZoneToDisplay = computed((): CalendarDropzoneEvent => {
  if (isDragging.value) {
    return _.find(props.dropzoneEvents, (dp: CalendarDropzoneEvent) => {
      return dp.eventId === eventDragged.value?.data.dataId
    })
  }
  return { eventId: -1, duration: 0, columnIds: [], possibleStarts: {} } as CalendarDropzoneEvent
})

/**
 * Computes the closest start time from the props.dropzoneEvents
 * @trigger currentTime The Timestamp object giving us the date and time where the mouse is
 */
const closestStartTime = computed(() => {
  let closest: string = ''
  if (!currentTime.value || !props.dropzoneEvents || dropZoneToDisplay.value.eventId === -1) return closest
  let i = 0
  let timeDiff: number = 0
  while (i < dropZoneToDisplay.value.possibleStarts[currentTime.value.date]?.length) {
    let currentDiff: number = 0
    if (i === 0) {
      timeDiff = Math.abs(
        diffTimestamp(
          dropZoneToDisplay.value.possibleStarts[currentTime.value.date][i].timeStart,
          currentTime.value,
          false
        )
      )
      closest = dropZoneToDisplay.value.possibleStarts[currentTime.value.date][i].timeStart.time
    } else {
      currentDiff = Math.abs(
        diffTimestamp(
          dropZoneToDisplay.value.possibleStarts[currentTime.value.date][i].timeStart,
          currentTime.value,
          false
        )
      )
      if (timeDiff > currentDiff) {
        timeDiff = currentDiff
        closest = dropZoneToDisplay.value.possibleStarts[currentTime.value.date][i].timeStart.time
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
  if (!dropZoneToDisplay.value || dropZoneToDisplay.value.eventId === -1) return
  dropZoneToDisplay.value.possibleStarts[dateTime.date]?.forEach((ts: { isClose: boolean; timeStart: Timestamp }) => {
    if (ts.timeStart.time === closestStartTime.value) {
      ts.isClose = true
    } else {
      ts.isClose = false
    }
  })
}

/**
 * Compute the current time of the mouse y position
 * @param dateTime the data concerning the day and the time when the parent element starts
 * @param timeDurationHeight function calculating the number of minutes from the position
 * @param layerY The position of the mouse on the Y-axis from the start of the parent element
 */
function currentTimeUpdate(dateTime: Timestamp, timeDurationHeight: Function, layerY: number): void {
  if (dateTime) {
    if (!currentTime.value || currentTime.value.date !== dateTime.date) currentTime.value = copyTimestamp(dateTime)
    updateMinutes(currentTime.value, Math.round(parseTime(dateTime.time) + timeDurationHeight(layerY)))
  }
}

/**
 * Function called when the drag event is triggered, set isDragging and eventDragged refs
 * @param browserEvent The HTML triggered event
 * @param event The event we are currently dragging
 */
function onDragStart(browserEvent: DragEvent, event: CalendarEvent) {
  isDragging.value = true
  eventDragged.value = event
  emits('dragstart', event.data.dataId)
  if (!browserEvent.dataTransfer) return
  browserEvent.dataTransfer.dropEffect = 'copy'
  browserEvent.dataTransfer.effectAllowed = 'move'
  browserEvent.dataTransfer.setData('ID', event.data.dataId.toString())
}

function onDragEnter(e: any, type: string, scope: { timeDurationHeight: any; timestamp: Timestamp }): boolean {
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return true
}

/**
 * Function called when the dragOver event is triggered, computes the current mouse position
 * time and update the closest dropZone
 * @param e the event triggered with data of the DOM object in it
 * @param type the type of element of the calendar
 * @param scope context containing utilitary functions
 */
function onDragOver(e: any, type: string, scope: { timeDurationHeight: any; timestamp: Timestamp }) {
  e.preventDefault()
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return true
}

function onDragLeave(e: any, type: string, scope: { timeDurationHeight: any; timestamp: Timestamp }) {
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
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
  let newEvent: CalendarEvent = _.cloneDeep(eventDragged.value)
  if (!dropZoneToDisplay.value) {
    console.log('NO DROPZONE FOR THIS EVENT')
    return
  }
  if (dropZoneToDisplay.value.eventId !== newEvent.data.dataId) {
    console.log('ERREUR DE DROPZONE')
    return
  }
  if (!currentTime.value) {
    console.log('ERREUR CURRENT TIME')
    return
  }
  dropZoneToDisplay.value.possibleStarts[currentTime.value.date]?.forEach(
    (ps: { isClose: boolean; timeStart: Timestamp }) => {
      if (ps.isClose) {
        newEvent.data.start = copyTimestamp(ps.timeStart)
      }
    }
  )
  let newEvents: CalendarEvent[] = _.cloneDeep(props.events)
  _.remove(newEvents, (e: CalendarEvent) => {
    return e.data.dataId === newEvent.data.dataId
  })
  newEvents.push(newEvent)
  eventsModel.value = newEvents
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
.text-white
  color: white
.bg-blue
  background: blue
.bg-green
  background: green
.bg-orange
  background: orange
.bg-red
  background: red
.bg-teal
  background: teal
.bg-grey
  background: grey
.bg-purple
  background: purple
.full-width
   left: 0
   width: calc(100% - 2px)
.left-side
   left: 0
   width: calc(50% - 3px)
.right-side
  left: 50%
  width: calc(50% - 3px)
.rounded-border
  border-radius: 2px
  padding-x: 2px
  text-align: center

.border-dashed
  border: 1px dashed grey
.my-dropzone
  pointer-events: none
</style>
