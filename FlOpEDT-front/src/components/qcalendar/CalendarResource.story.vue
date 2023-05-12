<template>
  <Story>
    <Variant title="Use case 1">
      <CalendarResource :events="useCase1.events" :resources="resources" />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CalendarResource from './CalendarResource.vue'
const useCase1 = {
  events: {
    1: [
      // John
      { start: '06:00', title: 'Gym', duration: 90 },
      { start: '08:00', title: 'Corporate Training - Partition A (Train new hires)', duration: 240 },
      { start: '12:00', title: 'Lunch', duration: 60 },
    ],
    2: [
      // Board room
    ],
    2.1: [
      // Room-1
      { start: '08:00', title: 'Board Meeting', duration: 120 },
    ],
    2.2: [
      // Room-2
    ],
    '2.2.1': [
      // Partition-A
      { start: '08:00', title: 'Corporate Training', duration: 240 },
    ],
    '2.2.2': [
      // Partition-B
    ],
    '2.2.3': [
      // Partition-C
    ],
    3: [
      // Mary
      { start: '08:00', title: 'Corporate Training - Partition A', duration: 240 },
      { start: '12:00', title: 'Lunch', duration: 60 },
    ],
    4: [
      // Susan
      { start: '08:00', title: 'Corporate Training - Partition A', duration: 240 },
      { start: '12:00', title: 'Lunch', duration: 60 },
    ],
    5: [
      // Olivia
      { start: '08:00', title: 'Corporate Training - Partition A', duration: 240 },
      { start: '12:00', title: 'Lunch', duration: 60 },
    ],
  },
}

const resources = [
  { id: '1', name: 'John' },
  {
    id: '2',
    name: 'Board Room',
    expanded: false,
    children: [
      { id: '2.1', name: 'Room-1' },
      {
        id: '2.2',
        name: 'Room-2',
        expanded: false,
        children: [
          { id: '2.2.1', name: 'Partition-A' },
          { id: '2.2.2', name: 'Partition-B' },
          { id: '2.2.3', name: 'Partition-C' },
        ],
      },
    ],
  },
  { id: '3', name: 'Mary' },
  { id: '4', name: 'Susan' },
  { id: '5', name: 'Olivia' },
]
</script>

<docs lang="md">
# Welcome

This is a demo book using Vue 3.

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>
