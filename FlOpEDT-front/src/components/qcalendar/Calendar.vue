<template>
  <div style="display: flex; max-width: 100%; width: 100%; height: 100%">
    <div style="display: flex">
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
    </div>
    <q-calendar-day
      ref="calendar"
      v-model="selectedDate"
      view="week"
      bordered
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
      :drop-func="onDrop"
    >
      <template #head-day-event="{ scope: { timestamp } }">
        <div style="display: flex">
          <template v-for="column in props.columns" :key="column.name">
            <div
              :class="badgeClasses('header')"
              style="cursor: pointer;height: 12px;font-size: 10px;margin-bottom: 1px;margin-top: 1px;border-color: 1px solid black;color: black;"
              :style="{
                'flex-basis': Math.round((100 * column.weight) / totalWeight) + '%',
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
            <div draggable="true" @dragstart="onDragStart($event, event)" @dragend="isDragging = false">
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
                    <!-- <q-tooltip>{{ event.details }}</q-tooltip> -->
                  </span>
                </slot>
              </div>
            </div>
          </template>
        </template>

        <!-- drop zone events to display -->
        <template
          v-if="isDragging && dropzoneEvents?.possibleStarts[timestamp.date]"
          v-for="ts in dropzoneEvents?.possibleStarts[timestamp.date]"
          :key="dropzoneEvents.eventId + '_' + timestamp.date + '_' + ts"
        >
          <div
            v-for="columnId in dropzoneEvents.columnIds"
            :key="dropzoneEvents.eventId + '_' + timestamp.date + '_' + ts.timeStart + '_' + columnId"
            class="my-event"
            :class="badgeClasses('dropzoneevent')"
            :style="
              badgeStyles(
                {
                  data: { start: ts.timeStart, duration: dropzoneEvents.duration, dataId: 0, dataType: 'dropzone' },
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
import { sortBy, map, clone, sumBy } from 'lodash'

import { CalendarColumn, CalendarEvent, CalendarDropzoneEvent, CalendarDynamicColumn } from './declaration'

import { computed, ref, Ref } from 'vue'
import { Timestamp, TimestampOrNull, diffTimestamp, parseTime, parsed, updateMinutes } from '@quasar/quasar-ui-qcalendar'

const props = defineProps<{
  events: CalendarEvent[]
  columns: CalendarColumn[] | CalendarDynamicColumn[]
  dropzoneEvents?: CalendarDropzoneEvent
}>()

const emits = defineEmits<{
  (e: 'dragstart', id: number): void
  (e: 'dropevent', data: any): void
}>()

const dynamicColumns : Ref<Array<CalendarDynamicColumn>> = ref(map(
  sortBy(props.columns, ['x']),
  col => {
    const dCol : CalendarDynamicColumn = clone(col) as CalendarDynamicColumn
    if (dCol.active === undefined) {
      dCol.active = true
    }
    return dCol
  }
  )
)

const totalWeight = computed(() => sumBy(
  dynamicColumns.value,
  (c : CalendarDynamicColumn) => c.active ? c.weight : 0)
)

const preWeight = computed(() => {
  const map: Record<number, number> = {}
  let preceeding = 0
  for (let i = 0 ; i < dynamicColumns.value.length ; i++) {
    const curColumn = dynamicColumns.value[i]
    map[curColumn.id] = preceeding
    if (curColumn.active) {
      preceeding += curColumn.weight
    }
  }
  return map
})

function toggleActive(columnId: number) {
  const col = dynamicColumns.value.find(c => c.id === columnId)
  if (col !== undefined) {
    col.active = !col.active
  }
}
  
/**
 * QCalendar data to display
 * * styles,
 * * events
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
  const currentGroup = dynamicColumns.value.find((c) => c.id === columnId)

  if (!currentGroup) return undefined

  const preceedingWeight = preWeight.value[columnId]

  const s: Record<string, string> = {
    top: '',
    height: '',
    'background-color': event.bgcolor || 'transparent',
  }
  if (timeStartPos && timeDurationHeight) {
    s.top = timeStartPos(event.data?.start) + 'px'
    s.left = Math.round((preWeight.value[columnId] / totalWeight.value) * 100) + '%'
    s.width = (currentGroup.active?Math.round((100 * currentGroup.weight) / totalWeight.value):0) + '%'
    s.height = timeDurationHeight(event.data?.duration) + 'px'
  }
  if(event.data?.dataType === "dropzone" && event.data.start.time === closestStartTime.value && event.data.start.date === currentTime.value?.date) {
    s['border-color'] = 'green'
    s['border-width'] = '3px'
  }
  s['align-items'] = 'flex-start'
  return s
}

/**
 * Drag and drop management
 */
const isDragging = ref(false)
const currentTime = ref<TimestampOrNull>(null)
const closestStartTime = computed(() => {
  let closest : string = ''
  if(!currentTime.value || !props.dropzoneEvents) return closest
  let i = 0
  let timeDiff: number = 0
  while(i < props.dropzoneEvents.possibleStarts[currentTime.value.date]?.length) {
    let currentDiff: number = 0
    if(i === 0) {
      timeDiff = Math.abs(diffTimestamp(props.dropzoneEvents.possibleStarts[currentTime.value.date][i].timeStart, currentTime.value, false))
      closest = props.dropzoneEvents.possibleStarts[currentTime.value.date][i].timeStart.time
    }
    else { 
        currentDiff = Math.abs(diffTimestamp(props.dropzoneEvents.possibleStarts[currentTime.value.date][i].timeStart, currentTime.value, false))
        if (timeDiff > currentDiff) {
          timeDiff = currentDiff
          closest = props.dropzoneEvents.possibleStarts[currentTime.value.date][i].timeStart.time
      }
    }
    i = i + 1
  }
  return closest
})

function onDragStart(browserEvent: DragEvent, event: CalendarEvent) {
  isDragging.value = true
  console.log('onDragStart called', event)
  emits('dragstart', event.data.dataId)
  if (!browserEvent.dataTransfer) return
  browserEvent.dataTransfer.dropEffect = 'copy'
  browserEvent.dataTransfer.effectAllowed = 'move'
  browserEvent.dataTransfer.setData('ID', event.data.dataId.toString())
}

function onDragEnter(e: any, type: string, scope: { timestamp: Timestamp, timeDurationHeight: any }) {
  console.log('onDragEnter', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  e.preventDefault()
  return true
}


function onDragOver(e: any, type: string, scope: { timeDurationHeight: any, timestamp: Timestamp }) {
  console.log('onDragOver', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  e.preventDefault()
  return true
}

function onDragLeave(e: any, type: string, scope: { timestamp: Timestamp, timeDurationHeight: any }) {
  console.log('onDragLeave', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  currentTimeUpdate(scope.timestamp, scope.timeDurationHeight, e.layerY)
  dropZoneCloseUpdate(scope.timestamp)
  return false
}

function onDrop(e: any, type: string, scope: { timestamp: Timestamp }) {
  console.log('onDrop', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  emits('dropevent', scope.timestamp)
  return false
}

function dropZoneCloseUpdate(dateTime: Timestamp): void {
  props.dropzoneEvents?.possibleStarts[dateTime.date].forEach((ts) => {
    if(ts.timeStart.time === closestStartTime.value) {
      ts.isClose = true
    } else {
      ts.isClose = false
    }
  })
}

function currentTimeUpdate(dateTime: Timestamp, timeDurationHeight: any, layerY: number): void {
  if(dateTime) {
    currentTime.value = updateMinutes(dateTime, Math.round(parseTime(dateTime.time)+timeDurationHeight(layerY)))
  }
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
</style>
