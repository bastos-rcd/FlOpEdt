<template>
  <Story>
    <Variant title="Use case 1">
      <Calendar 
        :columns="useCase1.columns"
        :events="(useCase1.events as CalendarEvent[])"
        :total-weight="useCase1.totalWeight"
        :dropzone-events="(currentDropzoneEvents as CalendarDropzoneEvent)"
        @dragstart="onDragStart"
      />
    </Variant>
    <Variant title="Use case 2">
      <Calendar 
        :columns="useCase2.columns"
        :events="(useCase2.events as CalendarEvent[])"
        :total-weight="useCase2.totalWeight"
        :dropzone-events="(currentDropzoneEvents as CalendarDropzoneEvent)"
        @dragstart="onDragStart"
      />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import { TimestampOrNull, Timestamp, parseDate, parseTime, today, updateMinutes, getStartOfWeek, addToDate } from '@quasar/quasar-ui-qcalendar'
import { computed, ref } from 'vue'
import type { CalendarEvent, CalendarDropzoneEvent } from './declaration'

import Calendar from './Calendar.vue'

const CURRENT_DAY = new Date()

const weekStart = getStartOfWeek(parseDate(CURRENT_DAY) as Timestamp, [1,2,3,4,5])

function shiftInCurrentWeek(relativeDay: number, time?: string): Timestamp {
  const tm = addToDate(weekStart, {day: relativeDay})
  if(tm && time) {
    updateMinutes(tm, parseTime(time))
  }
  return tm as Timestamp
}


const useCase2 = {
  columns: [
    {
      id: 0,
      name: 'TD1',
      weight: 2,
      x: 0,
    },
    {
      id: 1,
      name: 'TD2',
      weight: 2,
      x: 2,
    },
    {
      id: 2,
      name: 'TP31',
      weight: 1,
      x: 4,
    },
    {
      id: 3,
      name: 'TP32',
      weight: 1,
      x: 5,
    },
  ],
  totalWeight: 6,
  events: [
    {
      title: 'TP INFO',
      details: 'Let\' work on our Python project',
      bgcolor: 'red',
      icon: 'fas fa-handshake',
      columnIds: [2, 3],
      data: {
        dataId: 3,
        dataType: "mok",
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      title: 'Lunch',
      details: 'Company is paying!',
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [0,1,2,3],
      data: {
        dataId: 4,
        dataType: "mok",
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
        dataType: "mok",
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
        dataType: "mok",
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
  ],
  dropzoneEvents: [{
    eventId: 5,
    duration: 90,
    columnIds: [0,1],
    possibleStarts: {
      [shiftInCurrentWeek(0)!.date]: [
        { isclose: false, timeStart: shiftInCurrentWeek(0, '08:10')},
        { isclose: false, timeStart: shiftInCurrentWeek(0, '08:50')},
        { isclose: false, timeStart: shiftInCurrentWeek(0, '09:10')},
        { isclose: false, timeStart: shiftInCurrentWeek(0, '10:10')},
        { isclose: false, timeStart: shiftInCurrentWeek(0, '15:30')},
      ],
      [shiftInCurrentWeek(1)!.date]: [
        {isClose: false, timeStart: shiftInCurrentWeek(1, '10:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(1, '10:50')},
        {isClose: false, timeStart: shiftInCurrentWeek(1, '11:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(1, '18:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(1, '14:30')},
      ],
      [shiftInCurrentWeek(2)!.date]: [
        {isClose: false, timeStart: shiftInCurrentWeek(2, '10:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(2, '10:50')},
        {isClose: false, timeStart: shiftInCurrentWeek(2, '11:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(2, '18:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(2, '14:30')},
      ],
      [shiftInCurrentWeek(3)!.date]: [
        {isClose: false, timeStart: shiftInCurrentWeek(3, '10:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(3, '10:50')},
        {isClose: false, timeStart: shiftInCurrentWeek(3, '11:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(3, '18:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(3, '14:30')},
      ],
      [shiftInCurrentWeek(4)!.date]: [
        {isClose: false, timeStart: shiftInCurrentWeek(4, '10:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(4, '10:50')},
        {isClose: false, timeStart: shiftInCurrentWeek(4, '11:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(4, '18:10')},
        {isClose: false, timeStart: shiftInCurrentWeek(4, '14:30')},
      ],
    }
  },
  {
    eventId: 4,
    duration: 120,
    columnIds: [0,1,2,3],
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
    columnIds: [2,3],
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
    }
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
    }
  }],
}

const useCase1 = {
  columns: [
    {
      id: 0,
      name: 'TPA',
      weight: 1,
      x: 0,
    },
    {
      id: 1,
      name: 'TPB',
      weight: 1,
      x: 1,
    },
    {
      id: 2,
      name: 'TPC',
      weight: 1,
      x: 2,
    },
    {
      id: 3,
      name: 'TPD',
      weight: 1,
      x: 3,
    },
    {
      id: 4,
      name: 'GIM2',
      weight: 3,
      x: 4,
    },
  ],
  totalWeight: 7,
  events: [
    {
      title: '1st of the Month',
      details: 'Everything is funny as long as it is happening to someone else',
      bgcolor: 'orange',
      data: {
        dataId: 1,
        dataType: "mok",
        start: shiftInCurrentWeek(0),
      },
    },
    {
      id: 2,
      title: 'Sisters Birthday',
      details: 'Buy a nice present',
      date: shiftInCurrentWeek(1),
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
      data: {
        dataId: 2,
        dataType: "mok",
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
        dataType: "mok",
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
        dataType: "mok",
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
        dataType: "mok",
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
        dataType: "mok",
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 540,
      },
    },
    {
      title: 'Girlfriend',
      details: 'Meet GF for dinner at Swanky Restaurant',
      bgcolor: 'teal',
      icon: 'fas fa-utensils',
      data: {
        dataId: 7,
        dataType: "mok",
        start: shiftInCurrentWeek(3, '19:00'),
        duration: 180,
      },
    },
    {
      title: 'Fishing',
      details: 'Time for some weekend R&R',
      bgcolor: 'purple',
      icon: 'fas fa-fish',
      data: {
        dataId: 8,
        dataType: "mok",
        start: shiftInCurrentWeek(3),
        days: 2,
      },
    },
    {
      title: 'Vacation',
      details: "Trails and hikes, going camping! Don't forget to bring bear spray!",
      bgcolor: 'purple',
      icon: 'fas fa-plane',
      data: {
        dataId: 9,
        dataType: "mok",
        start: shiftInCurrentWeek(3),
        days: 5,
      },
    },
  ],
  dropzoneEvents: [{
    eventId: 5,
    duration: 90,
    columnIds: [1],
    possibleStarts: {
      [shiftInCurrentWeek(0)!.date]: [
        shiftInCurrentWeek(0, '08:10'),
        shiftInCurrentWeek(0, '08:50'),
        shiftInCurrentWeek(0, '09:10'),
        shiftInCurrentWeek(0, '10:10'),
        shiftInCurrentWeek(0, '15:30'),
      ],
      [shiftInCurrentWeek(1)!.date]: [
        shiftInCurrentWeek(1, '10:10'),
        shiftInCurrentWeek(1, '10:50'),
        shiftInCurrentWeek(1, '11:10'),
        shiftInCurrentWeek(1, '18:10'),
        shiftInCurrentWeek(1, '14:30'),
      ],
      [shiftInCurrentWeek(2)!.date]: [
        shiftInCurrentWeek(2, '10:10'),
        shiftInCurrentWeek(2, '10:50'),
        shiftInCurrentWeek(2, '11:10'),
        shiftInCurrentWeek(2, '18:10'),
        shiftInCurrentWeek(2, '14:30'),
      ],
      [shiftInCurrentWeek(3)!.date]: [
        shiftInCurrentWeek(3, '10:10'),
        shiftInCurrentWeek(3, '10:50'),
        shiftInCurrentWeek(3, '11:10'),
        shiftInCurrentWeek(3, '18:10'),
        shiftInCurrentWeek(3, '14:30'),
      ],
      [shiftInCurrentWeek(4)!.date]: [
        shiftInCurrentWeek(4, '10:10'),
        shiftInCurrentWeek(4, '10:50'),
        shiftInCurrentWeek(4, '11:10'),
        shiftInCurrentWeek(4, '18:10'),
        shiftInCurrentWeek(4, '14:30'),
      ],
    }
  }],
}
const currentEventId = ref<number|null>(null)
function onDragStart (eventId: number) {
  currentEventId.value = eventId
}

const currentDropzoneEvents = computed(() => {
  return useCase2.dropzoneEvents.find(d => d.eventId === currentEventId.value)
})

</script>

<docs lang="md">
# Welcome

This is a demo book using Vue 3.

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>