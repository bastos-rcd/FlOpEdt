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
          <p>
            <span>Tutor: {{ courseTutor?.username }}</span
            ><br />
            <span>Room: {{ courseRoom?.name }}</span
            ><br />
            <span>graded: {{ course?.graded }}</span
            ><br />
            <span></span>
          </p>
        </div>
      </slot>
    </PopoverContent>
  </PopoverRoot>
</template>

<script setup lang="ts">
import { PopoverRoot, PopoverTrigger, PopoverContent, PopoverClose, PopoverArrow } from 'radix-vue'
import { Icon } from '@iconify/vue'
import { ref, watch } from 'vue'
import { useScheduledCourseStore } from '@/stores/timetable/course'
import { Course, Module, Room, User } from '@/stores/declarations'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useRoomStore } from '@/stores/timetable/room'
import { useTutorStore } from '@/stores/timetable/tutor'
import { useGroupStore } from '@/stores/timetable/group'
import { concat, includes } from 'lodash'

const courseStore = useScheduledCourseStore()
const permanentStore = usePermanentStore()
const roomStore = useRoomStore()
const tutorStore = useTutorStore()
const groupStore = useGroupStore()
const props = defineProps<{
  eventObjectId: number
}>()
const courseModule = ref<Module>()
const courseRoom = ref<Room>()
const courseTutor = ref<User>()
const course = ref<Course>()

watch(
  () => props.eventObjectId,
  async () => {
    // Need to fetch room, tutor, module, groups
    course.value = courseStore.getCourse(props.eventObjectId)
    if (course) {
      try {
        courseModule.value = await permanentStore.getModule(course.value!.module)
        courseRoom.value = await roomStore.getRoomById(course.value!.room)
        courseTutor.value = await tutorStore.getTutorById(course.value!.tutorId)
        const courseGroups = concat(
          groupStore.fetchedStructuralGroups.filter((gp) => includes(course.value!.groupIds, gp.id)),
          groupStore.fetchedTransversalGroups.filter((gp) => includes(course.value!.groupIds, gp.id))
        )
      } catch (error) {
        console.log('FetchCourseDetail: ', error)
      }
    }
  }
)
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
</style>
