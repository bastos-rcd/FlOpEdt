<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <slot name="trigger">
        <span>Default Slot</span>
      </slot>
    </PopoverTrigger>
    <PopoverContent side="bottom" :side-offset="5" class="PopoverContent">
      <PopoverClose aria-label="Close" class="PopoverClose" as-child>
        <Icon icon="iconoir:cancel" class="IconClose" /> </PopoverClose
      ><slot name="content">
        <PopoverArrow class="PopoverArrow" />
        <div class="content-div">
          <div class="popover-title">{{ courseModule?.name }}</div>
          <div class="popover-section">
            <div class="popover-title">Tutor</div>
            <span>{{ courseTutor?.firstname }} {{ courseTutor?.lastname }} </span><br />
            <span>{{ courseTutor?.email }}</span>
          </div>
          <div class="popover-section">
            <div class="popover-title">Room</div>
            <span>{{ courseRoom?.name }}</span> <br />
          </div>
          <div class="popover-section">
            <div class="popover-title">graded</div>
            <span>{{ course?.graded ? 'yes' : 'no' }}</span> <br />
          </div>
        </div>
      </slot>
    </PopoverContent>
  </PopoverRoot>
</template>

<script setup lang="ts">
import { PopoverRoot, PopoverTrigger, PopoverContent, PopoverClose, PopoverArrow } from 'radix-vue'
import { Icon } from '@iconify/vue'
import { onBeforeMount, ref } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { Course, Module, Room, User } from '@/stores/declarations'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useRoomStore } from '@/stores/timetable/room'
import { useTutorStore } from '@/stores/timetable/tutor'

const courseStore = useScheduledCourseStore()
const permanentStore = usePermanentStore()
const roomStore = useRoomStore()
const tutorStore = useTutorStore()
const props = defineProps<{
  eventObjectId: number
}>()
const courseModule = ref<Module>()
const courseRoom = ref<Room>()
const courseTutor = ref<User>()
const course = ref<Course>()
onBeforeMount(async () => {
  // Need to fetch room, tutor, module, groups
  course.value = courseStore.getCourse(props.eventObjectId)
  if (course) {
    courseModule.value = await permanentStore.getModule(course.value!.module)
    courseRoom.value = await roomStore.getRoomById(course.value!.room)
    courseTutor.value = await tutorStore.getTutorById(course.value!.tutorId)
  }
})
</script>

<style>
.PopoverContent {
  border-radius: 4px;
  padding: 20px;
  width: 260px;
  background-color: white;
  box-shadow: hsl(206 22% 7% / 35%) 0px 10px 38px -10px, hsl(206 22% 7% / 20%) 0px 10px 20px -15px;
  animation-duration: 400ms;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform, opacity;
  z-index: 5;
  position: relative;
}

.PopoverClose {
  background-color: rgb(245, 245, 240);
}

.IconClose {
  font-family: inherit;
  border-radius: 100%;
  height: 25px;
  width: 25px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: 5px;
  right: 5px;
}

.PopoverClose:hover {
  background-color: rgb(200, 195, 195);
}
.PopoverClose:focus {
  box-shadow: 0 0 0 2px rgb(50, 50, 50);
}
.PopoverArrow {
  fill: white;
}
.content-div {
  color: black;
}
.popover-title {
  font-weight: bold;
  font-size: medium;
  margin: 0px 3px 0px 6px;
}
.popover-section {
  display: flex;
  flex-direction: column;
  background-color: rgb(240, 240, 240);
  margin: 2px;
  padding: 5px;
  align-items: flex-start;
  justify-content: space-around;
}
.popover-section span {
  width: 100%;
}
</style>
