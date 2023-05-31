<template>
  <Story>
    <Variant title="Use case 1">
      <Calendar :columns="useCase1.columns" v-model:events="useCase2.events.value" @dragstart="onDragStart" />
    </Variant>
    <Variant title="Use case 2">
      <Calendar :columns="useCase2.columns" v-model:events="useCase2.events.value" @dragstart="onDragStart" />
    </Variant>
    <Variant title="Use case 3">
      <Calendar :columns="useCase3.columns" v-model:events="useCase2.events.value" @dragstart="onDragStart" />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import type { CalendarEvent, CalendarColumn } from './declaration'
import _ from 'lodash'
import { Timestamp, parseDate, parseTime, updateMinutes, getStartOfWeek, addToDate } from '@quasar/quasar-ui-qcalendar'
import { ref, Ref } from 'vue'

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
  events: ref<CalendarEvent[]>([
    {
      id: 1,
      title: 'TP INFO',
      toggled: false,

      bgcolor: 'red',
      icon: 'fas fa-handshake',

      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],

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
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
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
      toggled: false,
      bgcolor: 'grey',
      icon: 'fas fa-car',
      displayData: [{ columnId: 0, weight: 2 }],
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
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'event',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 150,
      },
    },
    // Drop zones
    {
      id: 5,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '14:00'),
        duration: 150,
      },
    },
    {
      id: 6,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '11:00'),
        duration: 150,
      },
    },
    {
      id: 7,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:50'),
        duration: 150,
      },
    },
    {
      id: 8,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:00'),
        duration: 150,
      },
    },
    {
      id: 9,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:50'),
        duration: 150,
      },
    },
    {
      id: 10,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 150,
      },
    },
    {
      id: 11,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 150,
      },
    },
    {
      id: 12,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:50'),
        duration: 150,
      },
    },
    {
      id: 13,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:00'),
        duration: 150,
      },
    },
    {
      id: 14,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 2 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '08:50'),
        duration: 150,
      },
    },
    {
      id: 15,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 120,
      },
    },
    {
      id: 16,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '13:30'),
        duration: 120,
      },
    },
    {
      id: 17,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '11:00'),
        duration: 120,
      },
    },
    {
      id: 18,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '13:30'),
        duration: 120,
      },
    },
    {
      id: 19,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '11:00'),
        duration: 120,
      },
    },
    {
      id: 20,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '13:30'),
        duration: 120,
      },
    },
    {
      id: 57,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '11:00'),
        duration: 120,
      },
    },
    {
      id: 58,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '13:30'),
        duration: 120,
      },
    },
    {
      id: 59,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '11:00'),
        duration: 120,
      },
    },
    {
      id: 60,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 0, weight: 2 },
        { columnId: 1, weight: 2 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 4,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '13:30'),
        duration: 120,
      },
    },
    {
      id: 21,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '08:00'),
        duration: 120,
      },
    },
    {
      id: 22,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '10:30'),
        duration: 120,
      },
    },
    {
      id: 23,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 120,
      },
    },
    {
      id: 24,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '16:30'),
        duration: 120,
      },
    },
    {
      id: 25,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 120,
      },
    },
    {
      id: 26,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '10:50'),
        duration: 120,
      },
    },
    {
      id: 27,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '13:10'),
        duration: 120,
      },
    },
    {
      id: 28,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '19:10'),
        duration: 120,
      },
    },
    {
      id: 29,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '16:30'),
        duration: 120,
      },
    },
    {
      id: 30,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 120,
      },
    },
    {
      id: 31,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '10:50'),
        duration: 120,
      },
    },
    {
      id: 32,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '13:10'),
        duration: 120,
      },
    },
    {
      id: 33,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '19:10'),
        duration: 120,
      },
    },
    {
      id: 34,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '16:30'),
        duration: 120,
      },
    },
    {
      id: 35,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '08:00'),
        duration: 120,
      },
    },
    {
      id: 36,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '10:50'),
        duration: 120,
      },
    },
    {
      id: 37,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '13:10'),
        duration: 120,
      },
    },
    {
      id: 38,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '19:10'),
        duration: 120,
      },
    },
    {
      id: 39,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '16:30'),
        duration: 120,
      },
    },
    {
      id: 40,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '08:00'),
        duration: 120,
      },
    },
    {
      id: 41,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '10:50'),
        duration: 120,
      },
    },
    {
      id: 42,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '13:10'),
        duration: 120,
      },
    },
    {
      id: 43,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '19:10'),
        duration: 120,
      },
    },
    {
      id: 44,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
      data: {
        dataId: 3,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(4, '16:30'),
        duration: 120,
      },
    },
    {
      id: 45,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '16:30'),
        duration: 90,
      },
    },
    {
      id: 46,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '08:00'),
        duration: 90,
      },
    },
    {
      id: 47,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '10:50'),
        duration: 90,
      },
    },
    {
      id: 48,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '19:10'),
        duration: 90,
      },
    },
    {
      id: 49,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '16:30'),
        duration: 90,
      },
    },
    {
      id: 50,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:00'),
        duration: 90,
      },
    },
    {
      id: 51,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '10:50'),
        duration: 90,
      },
    },
    {
      id: 52,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '19:10'),
        duration: 90,
      },
    },
    {
      id: 53,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '16:30'),
        duration: 90,
      },
    },
    {
      id: 54,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '08:00'),
        duration: 90,
      },
    },
    {
      id: 55,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '10:50'),
        duration: 90,
      },
    },
    {
      id: 56,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 0, weight: 2 }],
      data: {
        dataId: 5,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '19:10'),
        duration: 90,
      },
    },
    {
      id: 57,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '07:00'),
        duration: 150,
        value: 0,
      },
    },
    {
      id: 62,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '09:30'),
        duration: 90,
        value: 4,
      },
    },
    {
      id: 63,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 60,
        value: 6,
      },
    },
    {
      id: 64,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '12:00'),
        duration: 120,
        value: 0,
      },
    },
    {
      id: 65,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 60,
        value: 7,
      },
    },
    {
      id: 66,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '15:00'),
        duration: 60,
        value: 3,
      },
    },
    {
      id: 67,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(0, '16:00'),
        duration: 180,
        value: 1,
      },
    },
    {
      id: 68,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(1, '12:00'),
        duration: 120,
        value: 0,
      },
    },
    {
      id: 58,
      title: '1',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(1, '07:00'),
        duration: 300,
        value: 1,
      },
    },
    {
      id: 59,
      title: '2',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(1, '14:00'),
        duration: 300,
        value: 2,
      },
    },
    {
      id: 60,
      title: '3',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(3, '11:30'),
        duration: 450,
        value: 3,
      },
    },
    {
      id: 61,
      title: '8',
      toggled: true,
      bgcolor: '',
      displayData: [{ columnId: -1, weight: 1 }],
      data: {
        dataId: 69,
        dataType: 'avail',
        start: shiftInCurrentWeek(4, '07:00'),
        duration: 720,
        value: 8,
      },
    },
  ]),
}

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
      id: 1,
      title: '1st of the Month',
      toggled: true,
      bgcolor: 'orange',
      displayData: [{ columnId: 1, weight: 1 }],
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
      date: shiftInCurrentWeek(1),
      bgcolor: 'green',
      icon: 'fas fa-birthday-cake',
      displayData: [{ columnId: 1, weight: 1 }],
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
      displayData: [
        { columnId: 1, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
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
      displayData: [
        { columnId: 2, weight: 1 },
        { columnId: 4, weight: 1 },
      ],
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
      displayData: [{ columnId: 1, weight: 1 }],
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
      displayData: [
        { columnId: 1, weight: 1 },
        { columnId: 2, weight: 1 },
        { columnId: 3, weight: 1 },
      ],
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
      displayData: [{ columnId: 1, weight: 1 }],
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
      displayData: [{ columnId: 1, weight: 1 }],
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
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 9,
        dataType: 'event',
        start: shiftInCurrentWeek(3),
      },
    },
    {
      id: 10,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '14:00'),
        duration: 150,
      },
    },
    {
      id: 11,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '11:00'),
        duration: 150,
      },
    },
    {
      id: 12,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:50'),
        duration: 150,
      },
    },
    {
      id: 13,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '09:00'),
        duration: 150,
      },
    },
    {
      id: 14,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(2, '08:50'),
        duration: 150,
      },
    },
    {
      id: 15,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '14:00'),
        duration: 150,
      },
    },
    {
      id: 16,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '11:00'),
        duration: 150,
      },
    },
    {
      id: 17,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:50'),
        duration: 150,
      },
    },
    {
      id: 18,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '09:00'),
        duration: 150,
      },
    },
    {
      id: 19,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(0, '08:50'),
        duration: 150,
      },
    },
    {
      id: 20,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '14:00'),
        duration: 150,
      },
    },
    {
      id: 21,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '11:00'),
        duration: 150,
      },
    },
    {
      id: 22,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '09:50'),
        duration: 150,
      },
    },
    {
      id: 23,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '09:00'),
        duration: 150,
      },
    },
    {
      id: 24,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(3, '08:50'),
        duration: 150,
      },
    },
    {
      id: 25,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '14:00'),
        duration: 150,
      },
    },
    {
      id: 26,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '11:00'),
        duration: 150,
      },
    },
    {
      id: 27,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '09:50'),
        duration: 150,
      },
    },
    {
      id: 28,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '09:00'),
        duration: 150,
      },
    },
    {
      id: 29,
      title: '',
      toggled: false,
      bgcolor: 'rgba(0,0,0,0.5)',
      displayData: [{ columnId: 1, weight: 1 }],
      data: {
        dataId: 6,
        dataType: 'dropzone',
        start: shiftInCurrentWeek(1, '08:50'),
        duration: 150,
      },
    },
  ]),
}

const currentEventId = ref<number | null>(null)
function onDragStart(eventId: number) {
  currentEventId.value = eventId
}

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
  events: useCase2.events,
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

### Implementation details

I don't know why, but a dragover event, supposedly listened via `:drag-over-func="onDragOver"`
at the `q-calendar` level does not go to there if we are dragging over a calendar event. Someone
seems to stop the propagation, but I could not figure out who.

**Workaround:** we force the call to `onDragOver` at the calendar event level.

## TODO

- The aesthetics should be improved
- Drag computation could be optimized

---

Learn more about Histoire [here](https://histoire.dev/).
</docs>
