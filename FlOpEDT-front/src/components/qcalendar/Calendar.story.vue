<template>
  <Story>
    <Variant title="Use case 1">
      <Calendar
        :columns="useCase1.columns"
        v-model:events="useCase1.events.value"
        :dropzone-events="useCase1.dropzoneEvents"
        @dragstart="onDragStart"
      />
    </Variant>
    <Variant title="Use case 2">
      <Calendar
        :columns="useCase2.columns"
        v-model:events="useCase2.events.value"
        :dropzone-events="useCase2.dropzoneEvents"
        @dragstart="onDragStart"
      />
    </Variant>
    <Variant title="Use case 3">
      <Calendar :columns="useCase3.columns" v-model:events="useCase1.events.value" @dragstart="onDragStart" />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import type { CalendarEvent, CalendarDropzoneEvent, CalendarColumn } from './declaration'
import _ from 'lodash'
import { Timestamp, parseDate, parseTime, updateMinutes, getStartOfWeek, addToDate } from '@quasar/quasar-ui-qcalendar'
import { ref, Ref, computed } from 'vue'

import Calendar from './Calendar.vue'

const CURRENT_DAY = new Date()

const weekStart = getStartOfWeek(parseDate(CURRENT_DAY) as Timestamp, [1, 2, 3, 4, 5])

function shiftInCurrentWeek(relativeDay: number, time?: string): Timestamp {
  const tm = addToDate(weekStart, { day: relativeDay })
  if (tm && time) {
    updateMinutes(tm, parseTime(time))
  }
  return tm as Timestamp
}

interface UseCase {
  columns: CalendarColumn[]
  events: Ref<CalendarEvent[]>
  dropzoneEvents: CalendarDropzoneEvent[]
}

const useCase2: UseCase = {
  columns: [
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
  ],
  events: ref([
    {
      title: 'TP INFO',
      details: "Let' work on our Python project",

      bgcolor: 'red',
      icon: 'fas fa-handshake',

      columnIds: [2, 3],

      data: {
        dataId: 3,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      title: 'Lunch',
      details: 'Company is paying!',
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [0, 1, 2, 3],
      data: {
        dataId: 4,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
      },
    },
    {
      title: 'Conference TD1',
      details: 'Always a nice chat with mom',
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [0],
      data: {
        dataId: 5,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      title: 'Conference TD2',
      details: 'Teaching Javascript 101',
      bgcolor: 'grey',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1],
      data: {
        dataId: 6,
        dataType: 'mok',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
  ]),
  dropzoneEvents: [
    {
      eventId: 5,
      duration: 90,
      columnIds: [0, 1],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '09:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '15:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '14:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '14:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '14:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '14:30') },
        ],
      },
    },
    {
      eventId: 4,
      duration: 120,
      columnIds: [0, 1, 2, 3],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '13:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '13:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '13:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '11:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '13:30') },
        ],
      },
    },
    {
      eventId: 3,
      duration: 120,
      columnIds: [2, 3],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '10:30') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '14:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '16:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '16:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '16:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '16:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '13:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '16:30') },
        ],
      },
    },
    {
      eventId: 6,
      duration: 150,
      columnIds: [1],
      possibleStarts: {
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '08:00') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '16:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '16:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '19:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '16:30') },
        ],
      },
    },
  ],
}

// _.forEach(useCase2.columns as Array<CalendarColumn>, col => col.active = true)

const useCase1 = {
  columns: [
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
  ],
  totalWeight: 7,
  events: ref([
    {
      title: '1st of the Month',
      details: 'Everything is funny as long as it is happening to someone else',
      bgcolor: 'orange',
      columnIds: [1],
      data: {
        dataId: 1,
        dataType: 'mok',
        start: shiftInCurrentWeek(0),
      },
    },
    {
      title: 'Sisters Birthday',
      details: 'Buy a nice present',
      date: shiftInCurrentWeek(1),
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
      columnIds: [1],
      data: {
        dataId: 2,
        dataType: 'mok',
        start: shiftInCurrentWeek(1),
      },
    },
    {
      title: 'Meeting',
      details: 'Time to pitch my idea to the company',
      bgcolor: 'red',
      icon: 'fas fa-handshake',
      columnIds: [1, 3],
      data: {
        dataId: 3,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '10:00'),
        duration: 120,
      },
    },
    {
      title: 'Lunch',
      details: 'Company is paying!',
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [2, 4],
      data: {
        dataId: 4,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '11:30'),
        duration: 90,
      },
    },
    {
      title: 'Visit mom',
      details: 'Always a nice chat with mom',
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [1],
      data: {
        dataId: 5,
        dataType: 'mok',
        start: shiftInCurrentWeek(1, '17:00'),
        duration: 90,
      },
    },
    {
      title: 'Conference',
      details: 'Teaching Javascript 101',
      bgcolor: 'blue',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1, 2, 3],
      data: {
        dataId: 6,
        dataType: 'mok',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 540,
      },
    },
    {
      title: 'Girlfriend',
      details: 'Meet GF for dinner at Swanky Restaurant',
      bgcolor: 'teal',
      icon: 'fas fa-utensils',
      columnIds: [1],
      data: {
        dataId: 7,
        dataType: 'mok',
        start: shiftInCurrentWeek(3, '19:00'),
        duration: 180,
      },
    },
    {
      title: 'Fishing',
      details: 'Time for some weekend R&R',
      bgcolor: 'purple',
      icon: 'fas fa-fish',
      columnIds: [1],
      data: {
        dataId: 8,
        dataType: 'mok',
        start: shiftInCurrentWeek(3),
        days: 2,
      },
    },
    {
      title: 'Vacation',
      details: "Trails and hikes, going camping! Don't forget to bring bear spray!",
      bgcolor: 'purple',
      icon: 'fas fa-plane',
      columnIds: [1],
      data: {
        dataId: 9,
        dataType: 'mok',
        start: shiftInCurrentWeek(3),
        days: 5,
      },
    },
  ]),
  dropzoneEvents: [
    {
      eventId: 5,
      duration: 90,
      columnIds: [1],
      possibleStarts: {
        [shiftInCurrentWeek(0)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '08:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '09:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(0, '15:30') },
        ],
        [shiftInCurrentWeek(1)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(1, '14:30') },
        ],
        [shiftInCurrentWeek(2)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(2, '14:30') },
        ],
        [shiftInCurrentWeek(3)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(3, '14:30') },
        ],
        [shiftInCurrentWeek(4)!.date]: [
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '10:50') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '11:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '18:10') },
          { isClose: false, timeStart: shiftInCurrentWeek(4, '14:30') },
        ],
      },
    },
  ],
}

// _.forEach(useCase1.columns as Array<CalendarColumn>, col => col.active = true)

const currentEventId = ref<number | null>(null)
function onDragStart(eventId: number) {
  currentEventId.value = eventId
}

const currentDropzoneEvents = computed(() => {
  return useCase2.dropzoneEvents.find((d) => d.eventId === currentEventId.value)
})

const useCase3: UseCase = {
  columns: [
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
  ],
  events: useCase1.events,
  dropzoneEvents: [],
}
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

## TODO

- The aesthetics should be improved
- Drag computation could be optimized

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>
