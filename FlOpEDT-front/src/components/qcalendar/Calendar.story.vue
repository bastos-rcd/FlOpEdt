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
import { TimestampOrNull, parseDate, parseTime, today, updateMinutes } from '@quasar/quasar-ui-qcalendar'
import { computed, ref } from 'vue'
import type { CalendarEvent, CalendarDropzoneEvent } from './declaration'

import Calendar from './Calendar.vue'

const CURRENT_DAY = new Date()

function getCurrentDay(day: any, time?: string): TimestampOrNull {
  const newDay = new Date(CURRENT_DAY)
  newDay.setDate(day)
  const tm = parseDate(newDay)
  if(tm && time) {
    updateMinutes(tm, parseTime(time))
  }
  return tm
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
        start: getCurrentDay(25, '08:00'),
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
        start: getCurrentDay(25, '12:00'),
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
        start: getCurrentDay(25, '17:00'),
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
        start: getCurrentDay(26, '08:00'),
        duration: 150,
      },
    },
  ],
  dropzoneEvents: [{
    eventId: 5,
    duration: 90,
    columnIds: [0,1],
    possibleStarts: {
      [getCurrentDay(24)!.date]: [
        getCurrentDay(24, '08:10'),
        getCurrentDay(24, '08:50'),
        getCurrentDay(24, '09:10'),
        getCurrentDay(24, '10:10'),
        getCurrentDay(24, '15:30'),
      ],
      [getCurrentDay(25)!.date]: [
        getCurrentDay(25, '10:10'),
        getCurrentDay(25, '10:50'),
        getCurrentDay(25, '11:10'),
        getCurrentDay(25, '18:10'),
        getCurrentDay(25, '14:30'),
      ],
      [getCurrentDay(26)!.date]: [
        getCurrentDay(26, '10:10'),
        getCurrentDay(26, '10:50'),
        getCurrentDay(26, '11:10'),
        getCurrentDay(26, '18:10'),
        getCurrentDay(26, '14:30'),
      ],
      [getCurrentDay(27)!.date]: [
        getCurrentDay(27, '10:10'),
        getCurrentDay(27, '10:50'),
        getCurrentDay(27, '11:10'),
        getCurrentDay(27, '18:10'),
        getCurrentDay(27, '14:30'),
      ],
      [getCurrentDay(28)!.date]: [
        getCurrentDay(28, '10:10'),
        getCurrentDay(28, '10:50'),
        getCurrentDay(28, '11:10'),
        getCurrentDay(28, '18:10'),
        getCurrentDay(28, '14:30'),
      ],
    }
  },
  {
    eventId: 4,
    duration: 120,
    columnIds: [0,1,2,3],
    possibleStarts: {
      [getCurrentDay(24)!.date]: [
        getCurrentDay(24, '11:00'),
        getCurrentDay(24, '13:30'),
      ],
      [getCurrentDay(25)!.date]: [
        getCurrentDay(25, '11:00'),
        getCurrentDay(25, '13:30'),
      ],
      [getCurrentDay(26)!.date]: [
        getCurrentDay(26, '11:00'),
        getCurrentDay(26, '13:30'),
      ],
      [getCurrentDay(28)!.date]: [
        getCurrentDay(28, '11:00'),
        getCurrentDay(28, '13:30'),
      ],
    },
  },
  {
    eventId: 3,
    duration: 120,
    columnIds: [2,3],
    possibleStarts: {
      [getCurrentDay(24)!.date]: [
        getCurrentDay(24, '08:00'),
        getCurrentDay(24, '10:30'),
        getCurrentDay(24, '14:00'),
        getCurrentDay(24, '16:30'),
      ],
      [getCurrentDay(25)!.date]: [
        getCurrentDay(25, '08:00'),
        getCurrentDay(25, '10:50'),
        getCurrentDay(25, '13:10'),
        getCurrentDay(25, '19:10'),
        getCurrentDay(25, '16:30'),
      ],
      [getCurrentDay(26)!.date]: [
        getCurrentDay(26, '08:10'),
        getCurrentDay(26, '10:50'),
        getCurrentDay(26, '13:10'),
        getCurrentDay(26, '19:10'),
        getCurrentDay(26, '16:30'),
      ],
      [getCurrentDay(27)!.date]: [
        getCurrentDay(27, '08:10'),
        getCurrentDay(27, '10:50'),
        getCurrentDay(27, '13:10'),
        getCurrentDay(27, '19:10'),
        getCurrentDay(27, '16:30'),
      ],
      [getCurrentDay(28)!.date]: [
        getCurrentDay(28, '08:10'),
        getCurrentDay(28, '10:50'),
        getCurrentDay(28, '13:10'),
        getCurrentDay(28, '19:10'),
        getCurrentDay(28, '16:30'),
      ],
    }
  },
  {
    eventId: 6,
    duration: 150,
    columnIds: [1],
    possibleStarts: {
      [getCurrentDay(25)!.date]: [
        getCurrentDay(25, '08:00'),
        getCurrentDay(25, '10:50'),
        getCurrentDay(25, '19:10'),
        getCurrentDay(25, '16:30'),
      ],
      [getCurrentDay(26)!.date]: [
        getCurrentDay(26, '08:10'),
        getCurrentDay(26, '10:50'),
        getCurrentDay(26, '19:10'),
        getCurrentDay(26, '16:30'),
      ],
      [getCurrentDay(27)!.date]: [
        getCurrentDay(27, '08:10'),
        getCurrentDay(27, '10:50'),
        getCurrentDay(27, '19:10'),
        getCurrentDay(27, '16:30'),
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
        start: getCurrentDay(24),
      },
    },
    {
      id: 2,
      title: 'Sisters Birthday',
      details: 'Buy a nice present',
      date: getCurrentDay(25),
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
      data: {
        dataId: 2,
        dataType: "mok",
        start: getCurrentDay(25),
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
        start: getCurrentDay(25, '10:00'),
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
        start: getCurrentDay(25, '11:30'),
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
        start: getCurrentDay(25, '17:00'),
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
        start: getCurrentDay(26, '08:00'),
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
        start: getCurrentDay(27, '19:00'),
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
        start: getCurrentDay(27),
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
        start: getCurrentDay(27),
        days: 5,
      },
    },
  ],
  dropzoneEvents: [{
    eventId: 5,
    duration: 90,
    columnIds: [1],
    possibleStarts: {
      [getCurrentDay(24)!.date]: [
        getCurrentDay(24, '08:10'),
        getCurrentDay(24, '08:50'),
        getCurrentDay(24, '09:10'),
        getCurrentDay(24, '10:10'),
        getCurrentDay(24, '15:30'),
      ],
      [getCurrentDay(25)!.date]: [
        getCurrentDay(25, '10:10'),
        getCurrentDay(25, '10:50'),
        getCurrentDay(25, '11:10'),
        getCurrentDay(25, '18:10'),
        getCurrentDay(25, '14:30'),
      ],
      [getCurrentDay(26)!.date]: [
        getCurrentDay(26, '10:10'),
        getCurrentDay(26, '10:50'),
        getCurrentDay(26, '11:10'),
        getCurrentDay(26, '18:10'),
        getCurrentDay(26, '14:30'),
      ],
      [getCurrentDay(27)!.date]: [
        getCurrentDay(27, '10:10'),
        getCurrentDay(27, '10:50'),
        getCurrentDay(27, '11:10'),
        getCurrentDay(27, '18:10'),
        getCurrentDay(27, '14:30'),
      ],
      [getCurrentDay(28)!.date]: [
        getCurrentDay(28, '10:10'),
        getCurrentDay(28, '10:50'),
        getCurrentDay(28, '11:10'),
        getCurrentDay(28, '18:10'),
        getCurrentDay(28, '14:30'),
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