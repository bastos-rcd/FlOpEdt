<template>
  <Story>
    <Variant title="Use case 1">
      <Calendar 
        :columns="useCase1.columns"
        :events="useCase1.events"
        :total-weight="useCase1.totalWeight"
        :dropzone-events="currentDropzoneEvents"
        @dragstart="onDragStart"
      />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import { parseDate, today } from '@quasar/quasar-ui-qcalendar'
import { computed, ref } from 'vue'

import Calendar from './Calendar.vue'

const CURRENT_DAY = new Date()

function getCurrentDay(day: any): string {
  const newDay = new Date(CURRENT_DAY)
  newDay.setDate(day)
  const tm = parseDate(newDay)
  return tm?.date || today()
}

const useCase1 = {
  days: ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'],
  dates: ['Lun 10/04', 'Mar 10/04', 'Mer 10/04', 'Jeu 10/04', 'Ven 10/04'],
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
      id: 1,
      title: '1st of the Month',
      details: 'Everything is funny as long as it is happening to someone else',
      date: getCurrentDay(24),
      bgcolor: 'orange',
    },
    {
      id: 2,
      title: 'Sisters Birthday',
      details: 'Buy a nice present',
      date: getCurrentDay(25),
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
    },
    {
      id: 3,
      title: 'Meeting',
      details: 'Time to pitch my idea to the company',
      date: getCurrentDay(25),
      time: '10:00',
      duration: 120,
      bgcolor: 'red',
      icon: 'fas fa-handshake',
      columnIds: [1, 3],
    },
    {
      id: 4,
      title: 'Lunch',
      details: 'Company is paying!',
      date: getCurrentDay(25),
      time: '11:30',
      duration: 90,
      bgcolor: 'teal',
      icon: 'fas fa-hamburger',
      columnIds: [2, 4],
    },
    {
      id: 5,
      title: 'Visit mom',
      details: 'Always a nice chat with mom',
      date: getCurrentDay(25),
      time: '17:00',
      duration: 90,
      bgcolor: 'grey',
      icon: 'fas fa-car',
      columnIds: [1],
    },
    {
      id: 6,
      title: 'Conference',
      details: 'Teaching Javascript 101',
      date: getCurrentDay(26),
      time: '08:00',
      duration: 540,
      bgcolor: 'blue',
      icon: 'fas fa-chalkboard-teacher',
      columnIds: [1, 2, 3],
    },
    {
      id: 7,
      title: 'Girlfriend',
      details: 'Meet GF for dinner at Swanky Restaurant',
      date: getCurrentDay(27),
      time: '19:00',
      duration: 180,
      bgcolor: 'teal',
      icon: 'fas fa-utensils',
    },
    {
      id: 8,
      title: 'Fishing',
      details: 'Time for some weekend R&R',
      date: getCurrentDay(27),
      bgcolor: 'purple',
      icon: 'fas fa-fish',
      days: 2,
    },
    {
      id: 9,
      title: 'Vacation',
      details: "Trails and hikes, going camping! Don't forget to bring bear spray!",
      date: getCurrentDay(27),
      bgcolor: 'purple',
      icon: 'fas fa-plane',
      days: 5,
    },
  ],
  dropzoneEvents: [{
    eventId: 5,
    duration: 90,
    columnIds: [1],
    possibleStarts: {
      [getCurrentDay(24)]: [
        '08:10',
        '08:50',
        '09:10',
        '10:10',
        '15:30',
      ],
      [getCurrentDay(25)]: [
        '10:10',
        '10:50',
        '11:10',
        '18:10',
        '14:30',
      ],
      [getCurrentDay(26)]: [
        '10:10',
        '10:50',
        '11:10',
        '18:10',
        '14:30',
      ],
      [getCurrentDay(27)]: [
        '10:10',
        '10:50',
        '11:10',
        '18:10',
        '14:30',
      ],
      [getCurrentDay(28)]: [
        '10:10',
        '10:50',
        '11:10',
        '18:10',
        '14:30',
      ],
    }
  }],
}
const currentEventId = ref<number|null>(5)
function onDragStart (eventId: number) {
  currentEventId.value = eventId
}

const currentDropzoneEvents = computed(() => {
  return useCase1.dropzoneEvents.find(d => d.eventId === currentEventId.value)
})

const useCase2 = {
  days: ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
}
</script>

<docs lang="md">
# Welcome

This is a demo book using Vue 3.

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>