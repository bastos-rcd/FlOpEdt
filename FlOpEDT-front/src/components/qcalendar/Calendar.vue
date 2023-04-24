<template>
  <div style="display: flex; max-width: 100%; width: 100%; height: 100%">
    <q-calendar-day
      ref="calendar"
      v-model="selectedDate"
      view="week"
      animated
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
          <template v-if="event.time !== undefined">
            <div
              v-for="columnId in event.columnIds"
              :key="event.id + '_' + columnId"
              class="my-event"
              :class="badgeClasses('event', event.bgcolor)"
              :style="badgeStyles(event, columnId, timeStartPos, timeDurationHeight)"
              draggable="true"
              @dragstart="onDragStart($event, event)"
              @dragend="isDragging = false"
            >
              <slot name="event" :event="event">
                <span class="title q-calendar__ellipsis">
                  {{ event.title }}
                  <!-- <q-tooltip>{{ event.details }}</q-tooltip> -->
                </span>
              </slot>
            </div>
          </template>
        </template>

        <!-- drop zone events to display -->
        <template
            v-if="dropzoneEvents?.possibleStarts[timestamp.date]"
            v-for="ts in dropzoneEvents?.possibleStarts[timestamp.date]"
            :key="dropzoneEvents.eventId + '_' + timestamp.date + '_' + ts"
          >
            <div
              v-for="columnId in dropzoneEvents.columnIds"
              :key="dropzoneEvents.eventId + '_' + timestamp.date + '_' + ts + '_' + columnId"
              class="my-event"
              :class="badgeClasses('dropzoneevent')"
              :style="badgeStyles({
                time: ts,
                duration: dropzoneEvents.duration
              }, columnId, timeStartPos, timeDurationHeight)"
            >
            </div>
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

import { CalendarColumn, CalendarEvent, CalendarDropzoneEvent } from './declaration'

import { computed, ref } from 'vue'

const props = defineProps<{
  events: CalendarEvent[]
  columns: CalendarColumn[]
  totalWeight: number,
  dropzoneEvents?: CalendarDropzoneEvent
}>()

const emits = defineEmits<{
  (e: 'dragstart', id: number): void
}>()


/**
 * QCalendar data to display
 * * styles,
 * * events
 */
const selectedDate = today()

const eventsByDate = computed(() => {
  const map: Record<string, any[]> = {}

  props.events.forEach((event) => {
    if (!map[event.date]) {
      map[event.date] = []
    }
    map[event.date].push(event)
    if (event.days) {
      let timestamp = parseTimestamp(event.date)
      let days = event.days
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
  switch(type) {
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

  const s: Record<string, string> = { top: '', height: '' /* width: widthPercentGroup.value + "%" */ }
  if (timeStartPos && timeDurationHeight) {
    s.top = timeStartPos(event.time) + 'px'
    s.left = Math.round((currentGroup?.x / props.totalWeight) * 100) + '%'
    s.width = Math.round((100 * currentGroup.weight) / props.totalWeight) + '%'
    s.height = timeDurationHeight(event.duration) + 'px'
  }
  s['align-items'] = 'flex-start'
  return s
}

/**
 * Drag and drop management
 */
let isDragging = ref(false)

function onDragStart(browserEvent: DragEvent, event: CalendarEvent) {
  isDragging.value = true
  console.log('onDragStart called', event)
  emits('dragstart', event.id)
  if (!browserEvent.dataTransfer) return
  browserEvent.dataTransfer.dropEffect = 'copy'
  browserEvent.dataTransfer.effectAllowed = 'move'
  browserEvent.dataTransfer.setData('ID', event.id.toString())
}

function onDragEnter(e, type, scope) {
  console.log('onDragEnter', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  e.preventDefault()
  return true
}

function onDragOver(e, type, scope) {
  console.log('onDragOver', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  e.preventDefault()
  return true
}

function onDragLeave(e, type, scope) {
  console.log('onDragLeave', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  return false
}

function onDrop(e, type, scope) {
  console.log('onDrop', e, type, scope, scope.timestamp.date, scope.timestamp.time)
  // const itemID = parseInt(e.dataTransfer.getData('ID'), 10)
  // const event = { ...this.defaultEvent }
  // event.id = this.events.length + 1
  // const item = this.dragItems.filter(item => item.id === itemID)
  // event.type = item[0].id
  // event.name = item[0].name
  // event.date = scope.timestamp.date
  // if (type === 'interval') {
  //   event.time = scope.timestamp.time
  // }
  // else { // head-day
  //   event.allDay = true
  // }
  // this.events.push(event)
  return false
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
