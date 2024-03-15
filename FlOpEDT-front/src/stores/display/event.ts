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
import { isTimestampInDayTime } from '@/helpers'
import { useDepartmentStore } from '../department'

export const useEventStore = defineStore('eventStore', () => {
  const courseStore = useScheduledCourseStore()
  const departmentStore = useDepartmentStore()
  const availabilityStore = useAvailabilityStore()
  const columnStore = useColumnStore()
  const permanentStore = usePermanentStore()
  const groupStore = useGroupStore()
  const { current } = storeToRefs(departmentStore)
  const { groups } = storeToRefs(groupStore)
  const { modules, moduleColor, timeSettings, modulesSelected } = storeToRefs(permanentStore)
  const { columns } = storeToRefs(columnStore)
  const daysSelected: Ref<Timestamp[]> = ref<Timestamp[]>([])
  const calendarEvents: Ref<InputCalendarEvent[]> = ref([])
  const roomsSelected: Ref<Room[]> = ref([])
  const tutorsSelected: Ref<User[]> = ref([])
  const courseTypesSelected: Ref<{ id: number; name: string }[]> = ref([])
  const colorSelect: Ref<'courseType' | 'module'> = ref('module')
  const calendarEventIds: Ref<number> = ref(2)
  const dropzonesIds: Ref<number> = ref(1)

  watchEffect(() => {
    const dayStartTime = timeSettings.value.get(current.value.id)?.dayStartTime
    const dayEndTime = timeSettings.value.get(current.value.id)?.dayEndTime
    const eventsReturned: InputCalendarEvent[] = []
    if (dayStartTime && dayEndTime) {
      availabilityStore.getAvailabilityFromDates(daysSelected.value).forEach((av) => {
        if (isTimestampInDayTime(dayStartTime, dayEndTime, av.start)) {
          const currentEvent: InputCalendarEvent = {
            id: calendarEventIds.value,
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
          calendarEventIds.value += 2
          currentEvent.title = currentEvent.data.dataType
          const availColumn = columns.value.find((c) => c.name === 'Avail')
          if (availColumn) currentEvent.columnIds.push(availColumn.id)
          eventsReturned.push(currentEvent)
        }
      })
    }
    courseStore.getCoursesFromDates(daysSelected.value).forEach((c: Course) => {
      const module: Module | undefined = modules.value.find((m) => m.id === c.module)
      const currentEvent: InputCalendarEvent = {
        id: ++calendarEventIds.value,
        title: module ? module.abbrev : 'Cours',
        toggled:
          tutorsSelected.value.length === 0 &&
          roomsSelected.value.length === 0 &&
          courseTypesSelected.value.length === 0 &&
          modulesSelected.value.length === 0,
        bgcolor: 'blue',
        columnIds: [],
        data: {
          dataId: c.id,
          dataType: 'event',
          start: copyTimestamp(c.start),
          duration: parseTime(c.end) - parseTime(c.start),
        },
      }
      calendarEventIds.value += 2
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
    let isModulesSelected = modulesSelected.value.length === 0
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
    i = 0
    while (i < modulesSelected.value.length && !isModulesSelected) {
      if (c.module === modulesSelected.value[i].id) {
        isModulesSelected = true
      }
      i++
    }
    return isTutorSelected && isRoomSelected && isCourseTypeSelected && isModulesSelected
  }

  return {
    daysSelected,
    calendarEvents,
    roomsSelected,
    tutorsSelected,
    colorSelect,
    courseTypesSelected,
    calendarEventIds,
    dropzonesIds,
  }
})
