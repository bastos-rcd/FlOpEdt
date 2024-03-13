<template>
  <Story>
    <Variant title="Use case 1">
      <Calendar
        :columns="useCase1.columns.value"
        v-model:events="useCase2.events.value"
        :dropzones="dropzonesUseCase1"
        @dragstart="onDragStart"
        :end-of-day-hours="19"
        :workcopy="3"
      />
    </Variant>
    <Variant title="Use case 2">
      <Calendar
        :columns="useCase2.columns.value"
        v-model:events="useCase2.events.value"
        :dropzones="dzs"
        @dragstart="onDragStart"
        @weekdays="(wd: number[]) => (weekdays = wd)"
        :end-of-day-hours="19"
        :workcopy="3"
      />
    </Variant>
    <Variant title="Use case 3">
      <Calendar
        :columns="useCase3.columns.value"
        v-model:events="useCase3.events.value"
        @dragstart="onDragStart"
        :end-of-day-hours="19"
        :workcopy="3"
      />
    </Variant>
    <Variant title="Availabilities">
      <button color="orange" style="margin: 2px" @click="toggleAvailabilities()">Show Availabilities</button>
      <Calendar
        :columns="useCase4.columns.value"
        v-model:events="useCase4.events.value"
        :dropzones="dzs"
        @dragstart="onDragStart"
        :end-of-day-hours="19"
        :workcopy="3"
      />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import type { CalendarColumn, CalendarEvent, InputCalendarEvent } from './declaration'
import { concat, maxBy, remove } from 'lodash'
import { Timestamp, parseDate, parseTime, updateMinutes, getStartOfWeek, addToDate } from '@quasar/quasar-ui-qcalendar'
import { ref, Ref } from 'vue'

import Calendar from './Calendar.vue'

const CURRENT_DAY = new Date()
const weekdays = ref([1, 2, 3, 4, 5])
const weekStart = getStartOfWeek(parseDate(CURRENT_DAY) as Timestamp, weekdays.value)

function shiftInCurrentWeek(relativeDay: number, time?: string): Timestamp {
  const tm = addToDate(weekStart, { day: relativeDay })
  if (tm && time) {
    updateMinutes(tm, parseTime(time))
  }
  return tm as Timestamp
}

const dropzonesUseCase1 = ref<CalendarEvent[]>([])

interface UseCase {
  columns: Ref<CalendarColumn[]>
  events: Ref<InputCalendarEvent[]>
}

const useCase2: UseCase = {
  columns: ref([
    {
      id: 0,
      name: 'TD1',
      weight: 2,
    },
    {
      id: 1,
      name: 'TD2',
      weight: 2,
    },
    {
      id: 2,
      name: 'TP31',
      weight: 1,
    },
    {
      id: 3,
      name: 'TP32',
      weight: 1,
    },
  ]),
  events: ref<InputCalendarEvent[]>([
    {
      id: 1,
      title: 'TP INFO',
      toggled: true,

      bgcolor: 'red',
      icon: 'fas fa-handshake',

      columnIds: [2, 3],

      data: {
        dataId: 3,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      id: 2,
      title: 'Lunch',
      toggled: true,
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
      },
    },
    {
      id: 3,
      title: 'Conference TD1',
      toggled: true,
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      id: 4,
      title: 'Conference TD2',
      toggled: true,
      bgcolor: 'grey',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'event',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
  ]),
}

const useCase1: UseCase = {
  columns: ref([
    {
      id: 0,
      name: 'TPA',
      weight: 1,
    },
    {
      id: 1,
      name: 'TPB',
      weight: 1,
    },
    {
      id: 2,
      name: 'TPC',
      weight: 1,
    },
    {
      id: 3,
      name: 'TPD',
      weight: 1,
    },
    {
      id: 4,
      name: 'GIM2',
      weight: 3,
    },
  ]),
  events: ref<InputCalendarEvent[]>([
    {
      id: 1,
      title: '1st of the Month',
      toggled: true,
      bgcolor: 'orange',
      columnIds: [1],
      data: {
        dataId: 1,
        dataType: 'event',
        start: shiftInCurrentWeek(0),
      },
    },
    {
      id: 2,
      title: 'Sisters Birthday',
      toggled: true,
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
      columnIds: [1],
      data: {
        dataId: 2,
        dataType: 'event',
        start: shiftInCurrentWeek(1),
      },
    },
    {
      id: 3,
      title: 'Meeting',
      toggled: true,
      bgcolor: 'red',
      icon: 'fas fa-handshake',
      columnIds: [1, 3],
      data: {
        dataId: 3,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '10:00'),
        duration: 120,
      },
    },
    {
      id: 4,
      title: 'Lunch',
      toggled: true,
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [2, 4],
      data: {
        dataId: 4,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '11:30'),
        duration: 90,
      },
    },
    {
      id: 5,
      title: 'Visit mom',
      toggled: true,
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [1],
      data: {
        dataId: 5,
        dataType: 'event',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      id: 6,
      title: 'Conference',
      toggled: true,
      bgcolor: 'blue',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1, 2, 3],
      data: {
        dataId: 6,
        dataType: 'event',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 540,
      },
    },
    {
      id: 7,
      title: 'Girlfriend',
      toggled: true,
      bgcolor: 'teal',
      icon: 'fas fa-utensils',
      columnIds: [1],
      data: {
        dataId: 7,
        dataType: 'event',
        start: shiftInCurrentWeek(3, '19:00'),
        duration: 180,
      },
    },
    {
      id: 8,
      title: 'Fishing',
      toggled: true,
      bgcolor: 'purple',
      icon: 'fas fa-fish',
      columnIds: [1],
      data: {
        dataId: 8,
        dataType: 'event',
        start: shiftInCurrentWeek(3),
      },
    },
    {
      id: 9,
      title: 'Vacation',
      toggled: true,
      bgcolor: 'purple',
      icon: 'fas fa-plane',
      columnIds: [1],
      data: {
        dataId: 9,
        dataType: 'event',
        start: shiftInCurrentWeek(3),
      },
    },
  ]),
}

const currentEventId = ref<number | null>(null)
function onDragStart(eventId: number) {
  currentEventId.value = eventId
}

const useCase3: UseCase = {
  columns: ref([
    {
      id: 0,
      name: 'TPA',
      weight: 1,
    },
    {
      id: 1,
      name: 'TPB',
      weight: 1,
    },
    {
      id: 2,
      name: 'TPC',
      weight: 1,
    },
    {
      id: 3,
      name: 'TPD',
      weight: 1,
    },
    {
      id: 4,
      name: 'GIM2',
      weight: 3,
    },
  ]),
  events: useCase2.events,
}

const useCase4: UseCase = {
  columns: ref(useCase2.columns.value),
  events: ref(useCase2.events.value),
}

let nextEventId = (maxBy(useCase4.events.value, (event) => event.id)?.id as number) + 1

const availabilityColumn = {
  id: 4,
  name: 'Avail',
  weight: 1,
}

function toggleAvailabilities() {
  const excluded = remove(useCase4.columns.value, (c) => c.id == availabilityColumn.id)
  if (excluded.length == 0) {
    useCase4.columns.value.push(availabilityColumn)
  }
}

useCase4.events.value = concat(useCase4.events.value, [
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '07:00'),
      duration: 150,
      value: 0,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '09:30'),
      duration: 90,
      value: 4,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '11:00'),
      duration: 60,
      value: 6,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '12:00'),
      duration: 120,
      value: 0,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '14:00'),
      duration: 60,
      value: 7,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '15:00'),
      duration: 60,
      value: 3,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(0, '16:00'),
      duration: 180,
      value: 1,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(1, '12:00'),
      duration: 120,
      value: 0,
    },
  },
  {
    id: nextEventId++,
    title: '1',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(1, '07:00'),
      duration: 300,
      value: 1,
    },
  },
  {
    id: nextEventId++,
    title: '2',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(1, '14:00'),
      duration: 300,
      value: 2,
    },
  },
  {
    id: nextEventId++,
    title: '3',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(3, '11:30'),
      duration: 450,
      value: 3,
    },
  },
  {
    id: nextEventId++,
    title: '8',
    toggled: true,
    bgcolor: '',
    columnIds: [4],
    data: {
      dataId: 69,
      dataType: 'avail',
      start: shiftInCurrentWeek(4, '07:00'),
      duration: 720,
      value: 8,
    },
  },
])

let dzs: CalendarEvent[] = []
</script>

<docs lang="md">
# Welcome To a copied doc

## Technical use

### Input/output

- The component receives 3 types of data:
  - A list of **CalendarEvent**s
    This data is used to create visual events inside bodies of the days
  - A list of **CalendarColumn**s
    This data is used to create the columns at the top of each days
  - A list of **CalendarDropzoneEvent**s
    This data can be passed as a list of every zones for every events or
    already filtered for the currently dragged event (with the dragstart event)
    It is used to display the possible drop zone areas

## User interface

- Click on an event and start dragging => dropzones appear inside day bodies
- Stop dragging => event is dropped on the nearest dropzone and change its value
  or put back at its original place
- Click on the navigation bar above the calendar => change the week displayed

### Implementation details

I don't know why, but a dragover event, supposedly listened via `:drag-over-func="onDragOver"`
at the `q-calendar` level does not go to there if we are dragging over a calendar event. Someone
seems to stop the propagation, but I could not figure out who.

**Workaround:** we force the call to `onDragOver` at the calendar event level.

## TODO

- The aesthetics should be improved
- Drag computation could be optimized
- Put the avail step and day boundaries as component's parameters

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>
