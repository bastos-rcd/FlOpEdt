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
  const { groupsSelected, groups } = storeToRefs(groupStore)
  const { modules, moduleColor } = storeToRefs(permanentStore)
  const { columns } = storeToRefs(columnStore)
  const daysSelected: Ref<Timestamp[]> = ref<Timestamp[]>([])
  const calendarEvents: Ref<InputCalendarEvent[]> = ref([])
  const roomsSelected: Ref<Room[]> = ref([])
  const tutorSelected: Ref<User | undefined> = ref()
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
        toggled: !tutorSelected.value && roomsSelected.value.length === 0,
        bgcolor: 'blue',
        columnIds: [],
        data: {
          dataId: c.id,
          dataType: 'event',
          start: copyTimestamp(c.start),
          duration: parseTime(c.end) - parseTime(c.start),
        },
      }
      if (module) {
        currentEvent.bgcolor = moduleColor.value.get(module.id)!
      }
      const courseGroupIds = c.groupIds.map((id) => groupStore.collectDescendantLeafNodeIds(id)).flat()
      courseGroupIds.forEach((courseGroup: number) => {
        let currentGroup: Group | undefined
        if (groupsSelected.value && groupsSelected.value.length !== 0)
          currentGroup = groupsSelected.value.find((g: Group) => g.id === courseGroup)
        else currentGroup = groups.value.find((g) => g.id === courseGroup)
        if (currentGroup) {
          currentGroup.columnIds.forEach((cI) => {
            currentEvent.columnIds.push(cI)
          })
        }
      })
      if (tutorSelected.value) if (c.tutorId === tutorSelected.value.id) currentEvent.toggled = true
      if (roomsSelected.value.length !== 0) {
        roomsSelected.value.forEach((room: Room) => {
          if (c.room === room.id) currentEvent.toggled = true
        })
      }
      eventsReturned.push(currentEvent)
    })
    calendarEvents.value = eventsReturned
  })

  return {
    daysSelected,
    calendarEvents,
    roomsSelected,
    tutorSelected,
  }
})
