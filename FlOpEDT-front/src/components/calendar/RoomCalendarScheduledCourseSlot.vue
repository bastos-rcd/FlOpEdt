<template>
  <CalendarScheduledCourseSlot :data="props.data">
    <template #text>
      <p class="col-xl-auto">{{ props.data.course.course.module.abbrev }}</p>
      <p class="col-xl-auto">{{ props.data.course.tutor }}</p>
      <p class="col-xl-auto ms-auto">{{ startHour }} - {{ endHour }}</p>
    </template>
  </CalendarScheduledCourseSlot>
</template>

<script setup lang="ts">
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import type { CalendarScheduledCourseSlotData } from '@/ts/type'
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  data: CalendarScheduledCourseSlotData
}
const { locale } = useI18n()
const props = defineProps<Props>()
const startHour = ref('')
const endHour = ref('')

watch(locale, () => {
  if (!(typeof props.data.course.start_time === 'string')) {
    startHour.value = props.data.course.start_time.toLocaleTimeString(locale.value)
    endHour.value = props.data.course.end_time.toLocaleTimeString(locale.value)
  }
})
onMounted(() => {
  // TEMPORARY PATCH
  // WHY SOME DATE ARE NOT CORRECTLY FORMATTED ?
  if (typeof props.data.course.start_time === 'string' && typeof props.data.course.end_time === 'string') {
    startHour.value = props.data.course.start_time
    endHour.value = props.data.course.end_time
  } else {
    startHour.value = props.data.course.start_time.toLocaleTimeString(locale.value)
    endHour.value = props.data.course.end_time.toLocaleTimeString(locale.value)
  }
})
</script>

<script lang="ts">
export default {
  name: 'RoomCalendarScheduledCourseSlot',
  components: {},
}
</script>

<style scoped></style>
