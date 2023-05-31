<template>
  <div class="row justify-center">
    <div class="q-pa-md q-gutter-sm row">
      <q-btn no-caps class="button" style="margin: 2px" @click="onToday"> Today </q-btn>
      <q-btn no-caps class="button" style="margin: 2px" @click="onPrev"> &lt; Prev </q-btn>
      <q-btn no-caps class="button" style="margin: 2px" @click="onNext"> Next &gt; </q-btn>
    </div>
    <div class="q-pa-md q-gutter-sm row">
      <q-btn no-caps class="button" style="margin: 2px" @click="showAvailabilities = !showAvailabilities">
        Show Availabilities
      </q-btn>
    </div>
  </div>
  <div style="display: flex; max-width: 100%; width: 100%; height: 100%">
    <!-- <div style="display: flex">
      <template v-for="column in props.columns" :key="column.name">
        <div
              :class="badgeClasses('header')"
              style="cursor: pointer;height: 12px;font-size: 10px;margin-bottom: 1px;margin-top: 1px;border-color: 1px solid black;color: black;"
              :style="{
                'flex-basis': Math.round((100 * column.weight) / totalWeight) + '%',
                'align-items': 'center',
              }"
              @click="toggleActive(column.id)"
            >
              {{ column.name }}
        </div>
      </template>
    </div> -->
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
          <template v-for="column in columnsToDisplay" :key="column.name">
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

      <template #day-body="{ scope: { timestamp, timeStartPos, timeDurationHeight } }">
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
            <div
              draggable="true"
              @dragstart="onDragStart($event, event)"
              @dragover="onDragOver($event, event.data.dataType, { timeDurationHeight, timestamp: event.data.start })"
            >
              <div
                v-for="data in event.displayData"
                :key="event.id"
                class="my-event"
                :class="badgeClasses(event.data.dataType, event.bgcolor)"
                :style="badgeStyles(event, data, timeStartPos, timeDurationHeight)"
              >
                <slot v-if="columnsToDisplay.find((c) => c.id === data.columnId)" name="event" :event="event">
                  <span v-if="event.data.dataType !== 'avail'" class="title q-calendar__ellipsis">
                    {{ event.title }}
                  </span>
                  <div
                    v-else
                    style="width: 100%; height: 100%; align-items: center; display: flex; justify-content: center"
                  >
                    <q-icon color="black" :name="event.icon" size="xs" />
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
import '@quasar/extras/material-icons'

import _ from 'lodash'

import { CalendarColumn, CalendarEvent } from './declaration'

import { Ref, computed, ref } from 'vue'
import { TimestampOrNull, Timestamp, parsed, updateWorkWeek, QCalendar } from '@quasar/quasar-ui-qcalendar'
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
  events: CalendarEvent[]
  columns: CalendarColumn[]
}>()

const emits = defineEmits<{
  (e: 'dragstart', id: number): void
  (e: 'update:events', value: CalendarEvent[]): void
  (e: 'update:week', value: Timestamp): void
}>()

const preWeight = computed(() => {
  const map: Record<number, number> = {}
  let preceeding = 0
  _.forEach(columnsToDisplay.value, (col: CalendarColumn) => {
    map[col.id] = preceeding
    preceeding += col.weight
  })
  return map
})

/**
 * QCalendar DATA TO DISPLAY
 * * Format the data from the events to match the calendar display,
 * * Functions to compute the style to render for each event
 */
const selectedDate = ref<string>(today())
const showAvailabilities = ref<boolean>(false)

watch(selectedDate, () => {
  console.log(updateWorkWeek(parsed(selectedDate.value) as Timestamp))
  emits('update:week', updateWorkWeek(parsed(selectedDate.value) as Timestamp))
})

// Events send to the qcalendar ordered by their date
// Their columnIds are changed to merge the same events
// occuring on different columns
const eventsByDate = computed(() => {
  const map: Record<string, CalendarEvent[]> = {}
  // Copy of events
  let newEvents: CalendarEvent[] = []
  let i = 0
  // Dict of column ids keys to their index
  let columnIndexes: Record<number, number> = {}
  columnsToDisplay.value.forEach((c) => {
    columnIndexes[c.id] = i
    i++
  })
  props.events.forEach((event) => {
    let newEvent = _.cloneDeep(event)
    if (newEvent.data.dataType === 'avail') {
      newEvent.displayData[0].columnId = (_.maxBy(props.columns, 'id')?.id as number) + 1
      newEvent.bgcolor = availabilityData.color[newEvent.data.value?.toString() || '0']
      newEvent.icon = availabilityData.icon[newEvent.data.value?.toString() || '0']
    }
    let newDisplayData = _.cloneDeep(newEvent.displayData)
    newEvent.displayData.forEach((dd) => {
      if (!(dd.columnId in columnIndexes)) {
        _.remove(newDisplayData, (disD) => {
          return disD.columnId === dd.columnId && disD.weight === dd.weight
        })
      }
    })
    newEvent.displayData = newDisplayData
    i = newEvent.displayData.length - 1
    while (i > 0) {
      if (
        Math.abs(
          columnIndexes[newEvent.displayData[i].columnId] - columnIndexes[newEvent.displayData[i - 1].columnId]
        ) === 1
      ) {
        newEvent.displayData[i - 1].weight += newEvent.displayData[i].weight
        _.pullAt(newEvent.displayData, i)
      }
      i = i - 1
    }
    newEvents.push(newEvent)
  })
  newEvents.forEach((event) => {
    if (!map[event.data.start.date]) {
      map[event.data.start.date] = []
    }
    map[event.data.start.date].push(event)
  })
  return map
})

const columnsToDisplay = computed((): CalendarColumn[] => {
  if (showAvailabilities.value) {
    // TODO: Which component is responsible for columns IDs ?
    const availColumn: CalendarColumn = { id: (_.maxBy(props.columns, 'id')?.id as number) + 1, name: 'Av.', weight: 1 }
    return _.union(props.columns, [availColumn])
  }
  return props.columns
})

const totalWeight = computed(() => {
  if (columnsToDisplay.value !== undefined) {
    return _.sumBy(columnsToDisplay.value, (c: CalendarColumn) => c.weight)
  }
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
  displayData: { columnId: number; weight: number },
  timeStartPos: any = undefined,
  timeDurationHeight: any = undefined
) {
  const currentColumn = columnsToDisplay.value.find((c) => displayData.columnId == c.id)
  if (!currentColumn) return undefined
  const preceedingWeight = preWeight.value[displayData.columnId]

  const s: Record<string, string> = {
    top: '',
    height: '',
  }
  if (!event.toggled) {
    s['opacity'] = '0.5'
  }
  if (timeStartPos && timeDurationHeight) {
    s.top = timeStartPos(event.data?.start) + 'px'
    s.left = Math.round((preWeight.value[displayData.columnId] / totalWeight.value) * 100) + '%'
    s.width = Math.round((100 * displayData.weight) / totalWeight.value) + '%'
    s.height = timeDurationHeight(event.data?.duration) + 'px'
  }
  if (event.data.dataType === 'dropzone') {
    s['background-color'] = 'transparent'
  } else {
    s['background-color'] = event.bgcolor
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
 * * is being dragged at the start of the drag process
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

/**
 * Only returns the dropZone with the same ID as the event dragged
 */
const dropZoneToDisplay = computed((): CalendarEvent[] | undefined => {
  return _.filter(
    props.events,
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
 * @param timeDurationHeight function calculating the number of minutes from the position
 * @param layerY The position of the mouse on the Y-axis from the start of the parent element
 */
function currentTimeUpdate(dateTime: Timestamp, timeDurationHeight: Function, layerY: number): void {
  if (dateTime) {
    if (!currentTime.value || currentTime.value.date !== dateTime.date)
      currentTime.value = copyTimestamp(dateTime) as TimestampOrNull
    updateMinutes(currentTime.value as Timestamp, Math.round(parseTime(dateTime.time) + timeDurationHeight(layerY)))
  }
}

/**
 * Function called when the drag event is triggered, set isDragging and eventDragged refs
 * @param browserEvent The HTML triggered event
 * @param event The event we are currently dragging
 */
function onDragStart(browserEvent: DragEvent, event: CalendarEvent) {
  currentTime.value = copyTimestamp(event.data.start) as TimestampOrNull
  isDragging.value = true
  eventDragged.value = _.cloneDeep(event)
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
  if (!currentTime.value) {
    console.log('ERREUR CURRENT TIME')
    return
  }
  if (!eventDragged.value) {
    console.log("I don't know what happened: I lost the dragged event")
    return
  }
  let newEvent: CalendarEvent = _.cloneDeep(props.events.find((e) => eventDragged.value?.id === e.id) as CalendarEvent)
  if (dropZoneToDisplay.value) {
    dropZoneToDisplay.value.forEach((cdze) => {
      if (cdze.toggled) {
        newEvent.data.start = copyTimestamp(cdze.data.start)
      }
    })
  } else {
    console.log('NO DROPZONE FOR THIS EVENT OU ERREUR DE DROPZONE')
  }
  let newEvents: CalendarEvent[] = _.cloneDeep(props.events)
  _.remove(newEvents, (e: CalendarEvent) => {
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
const calendar: Ref<QCalendar | null> = ref(null)
function onToday(): void {
  calendar.value?.moveToToday()
}
function onPrev(): void {
  calendar.value?.prev()
}
function onNext(): void {
  calendar.value?.next()
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
