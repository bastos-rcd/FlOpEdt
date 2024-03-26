<template>
  <Story>
    <Variant title="useCase1">
      <CourseCard :event-id="1" />
    </Variant>
  </Story>
</template>

<script setup lang="ts">
import { useScheduledCourseStore } from '@/stores/timetable/course'
import CourseCard from './CourseCard.vue'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useRoomStore } from '@/stores/timetable/room'
import { onBeforeMount } from 'vue'
import { Course, Module, Room, User } from '@/stores/declarations'
import { Timestamp, parseTimestamp } from '@quasar/quasar-ui-qcalendar'

const courseStore = useScheduledCourseStore()
const permanentStore = usePermanentStore()
const tutorStore = useTutorStore()
const roomStore = useRoomStore()

const course: Course = {
  id: 1,
  no: 1,
  room: 12,
  tutorId: 7,
  suppTutorIds: [],
  module: 3,
  groupIds: [2, 5, 6],
  courseTypeId: 2,
  roomTypeId: 3,
  graded: false,
  workCopy: 1,
  start: parseTimestamp('2024-03-12T11:00') as Timestamp,
  end: parseTimestamp('2024-03-12T13:00') as Timestamp,
}
const module: Module = {
  id: 3,
  name: 'Anglais C1',
  abbrev: 'ANC1',
  trainProgId: 293,
  url: '',
}
const room: Room = {
  id: 12,
  abbrev: 'B002',
  name: 'B002',
  subroomIdOf: [],
  departmentIds: [44],
}
const user: User = {
  id: 7,
  username: 'PRG',
  firstname: 'Paul',
  lastname: 'Renaud-Goud',
  email: 'PRG@flop.fr',
  type: 'tutor',
  departments: new Map<number, boolean>(),
}

onBeforeMount(() => {
  console.log('BAMBINO')
  courseStore.addOrUpdateCourseToDate(course)
  console.log('courseStore', courseStore.courses)
  permanentStore.modules.push(module)
  tutorStore.tutors.push(user)
  roomStore.roomsFetched.push(room)
})
</script>
