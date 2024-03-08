<template>
  <div class="title">
    <span>{{ courseModule?.abbrev }}</span>
    <span>{{ courseTutor?.username }}</span>
    <span>{{ courseRoom?.name }}</span>
  </div>
</template>
<script setup lang="ts">
import { Course, Module, Room, User } from '@/stores/declarations'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useRoomStore } from '@/stores/timetable/room'
import { useTutorStore } from '@/stores/timetable/tutor'
import { onBeforeMount, ref } from 'vue'
const props = defineProps<{
  eventId: number
}>()
const courseStore = useScheduledCourseStore()
const permanentStore = usePermanentStore()
const roomStore = useRoomStore()
const tutorStore = useTutorStore()
const courseModule = ref<Module>()
const courseRoom = ref<Room>()
const courseTutor = ref<User>()
const course = ref<Course>()
onBeforeMount(async () => {
  // Need to fetch room, tutor, module, groups
  course.value = courseStore.getCourse(props.eventId)
  if (course) {
    courseModule.value = await permanentStore.getModule(course.value!.module)
    courseRoom.value = await roomStore.getRoomById(course.value!.room)
    courseTutor.value = await tutorStore.getTutorById(course.value!.tutorId)
  }
})
</script>

<style scoped>
span {
  font-weight: bold;
}
</style>
