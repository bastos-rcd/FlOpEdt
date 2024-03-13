import { InputCalendarEvent } from '@/components/calendar/declaration'
import { defineStore, storeToRefs } from 'pinia'
import { Ref, ref, watchEffect } from 'vue'
import { useScheduledCourseStore } from '../timetable/course'
import { Timestamp, copyTimestamp, parseTime } from '@quasar/quasar-ui-qcalendar'
import { useAvailabilityStore } from '../timetable/availability'
import { useColumnStore } from './column'
import { Course, Group, Module, Room, User } from '../declarations'
import { usePermanentStore } from '../timetable/permanent'
import { useGroupStore } from '../timetable/group'

export const useEventStore = defineStore('eventStore', () => {
  const courseStore = useScheduledCourseStore()
  const availabilityStore = useAvailabilityStore()
  const columnStore = useColumnStore()
  const permanentStore = usePermanentStore()
  const groupStore = useGroupStore()
  const { groups } = storeToRefs(groupStore)
  const { modules, moduleColor } = storeToRefs(permanentStore)
  const { columns } = storeToRefs(columnStore)
  const daysSelected: Ref<Timestamp[]> = ref<Timestamp[]>([])
  const calendarEvents: Ref<InputCalendarEvent[]> = ref([])
  const roomsSelected: Ref<Room[]> = ref([])
  const tutorsSelected: Ref<User[]> = ref([])
  const courseTypesSelected: Ref<{ id: number; name: string }[]> = ref([])
  const colorSelect: Ref<'courseType' | 'module'> = ref('module')
  let calendarEventIds: number = 0

  watchEffect(() => {
    const eventsReturned: InputCalendarEvent[] = []
    availabilityStore.getAvailabilityFromDates(daysSelected.value).forEach((av) => {
      const currentEvent: InputCalendarEvent = {
        id: ++calendarEventIds,
        title: '',
        toggled: true,
        bgcolor: '',
        columnIds: [],
        data: {
          dataId: av.id,
          dataType: 'avail',
          start: copyTimestamp(av.start),
          duration: av.duration,
          value: av.value,
        },
      }
      currentEvent.title = currentEvent.data.dataType
      const availColumn = columns.value.find((c) => c.name === 'Avail')
      if (availColumn) currentEvent.columnIds.push(availColumn.id)
      eventsReturned.push(currentEvent)
    })
    courseStore.getCoursesFromDates(daysSelected.value).forEach((c: Course) => {
      const module: Module | undefined = modules.value.find((m) => m.id === c.module)
      const currentEvent: InputCalendarEvent = {
        id: ++calendarEventIds,
        title: module ? module.abbrev : 'Cours',
        toggled:
          tutorsSelected.value.length === 0 &&
          roomsSelected.value.length === 0 &&
          courseTypesSelected.value.length === 0,
        bgcolor: 'blue',
        columnIds: [],
        data: {
          dataId: c.id,
          dataType: 'event',
          start: copyTimestamp(c.start),
          duration: parseTime(c.end) - parseTime(c.start),
        },
      }
      if (colorSelect.value === 'module') {
        if (module) {
          const eventColor = moduleColor.value.get(module.id)
          if (eventColor) {
            currentEvent.bgcolor = eventColor
          }
        }
      } else {
        if (c.courseTypeId !== -1) {
          const eventColor = courseStore.courseTypeColors.get(c.courseTypeId)
          if (eventColor) {
            currentEvent.bgcolor = eventColor
          }
        }
      }
      const courseGroupIds = c.groupIds.map((id) => groupStore.collectDescendantLeafNodeIds(id)).flat()
      courseGroupIds.forEach((courseGroup: number) => {
        const currentGroup: Group | undefined = groups.value.find((g) => g.id === courseGroup)
        if (currentGroup) {
          currentGroup.columnIds.forEach((cI) => {
            currentEvent.columnIds.push(cI)
          })
        }
      })
      currentEvent.toggled = isCurrentEventSelected(c)
      eventsReturned.push(currentEvent)
    })
    calendarEvents.value = eventsReturned
  })

  function isCurrentEventSelected(c: Course): boolean {
    let isTutorSelected = tutorsSelected.value.length === 0
    let isRoomSelected = roomsSelected.value.length === 0
    let isCourseTypeSelected = courseTypesSelected.value.length === 0
    let i = 0
    while (i < tutorsSelected.value.length && !isTutorSelected) {
      if (c.tutorId === tutorsSelected.value[i].id) {
        isTutorSelected = true
      }
      i++
    }
    i = 0
    while (i < roomsSelected.value.length && !isRoomSelected) {
      if (c.room === roomsSelected.value[i].id) {
        isRoomSelected = true
      }
      i++
    }
    i = 0
    while (i < courseTypesSelected.value.length && !isCourseTypeSelected) {
      if (c.courseTypeId === courseTypesSelected.value[i].id) {
        isCourseTypeSelected = true
      }
      i++
    }
    return isTutorSelected && isRoomSelected && isCourseTypeSelected
  }

  return {
    daysSelected,
    calendarEvents,
    roomsSelected,
    tutorsSelected,
    colorSelect,
    courseTypesSelected,
  }
})
