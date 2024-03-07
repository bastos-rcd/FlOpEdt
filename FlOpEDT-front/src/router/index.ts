import { createRouter, createWebHistory } from 'vue-router'
import { useDepartmentStore } from '@/stores/department'
import { useAuth } from '@/stores/auth'
import i18n from '@/i18n'
import { usePermanentStore } from '@/stores/timetable/permanent'
import { useTutorStore } from '@/stores/timetable/tutor'
import { storeToRefs } from 'pinia'
import { useRoomStore } from '@/stores/timetable/room'

export const routeNames = {
  home: Symbol('Home'),
  departmentSelection: Symbol('department-selection'),
  contact: Symbol('contact'),
  notFound: Symbol('notFound'),
  login: Symbol('login'),
  schedule: Symbol('schedule'),
}

const routes = [
  {
    path: '/schedule/:dept?/:locale?',
    name: routeNames.schedule,
    component: () => import('@/views/ScheduleView.vue'),
    meta: {
      needsAuth: false,
    },
  },
  // {
  //   path: '/roomreservation/:locale?/:dept?',
  //   name: routeNames.roomReservation,
  //   component: () => import('@/views/RoomReservationView.vue'),
  //   meta: {
  //     title: 'Réservation de salles',
  //     needsAuth: true,
  //   },
  // },
  {
    path: '/login/:dept?/:locale?',
    name: routeNames.login,
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: 'Connexion',
      needsAuth: false,
      nextPath: '',
    },
  },
  {
    path: '/contact/:dept?/:locale?',
    name: routeNames.contact,
    component: () => import('@/views/ContactView.vue'),
    meta: {
      title: 'Contact',
      needsAuth: true,
    },
  },
  {
    path: '/:dept?/:locale?',
    name: routeNames.home,
    component: () => import('@/views/HomeView.vue'),
    meta: {
      title: 'Ca floppe !',
      needsAuth: false,
    },
  },
  {
    path: '/:pathMatch(.*)',
    name: routeNames.notFound,
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '404 Not Found',
      needsAuth: false,
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})
router.beforeEach(async (to, from, next) => {
  const { availableLocales, locale } = i18n.global
  const deptStore = useDepartmentStore()
  const roomStore = useRoomStore()
  const authStore = useAuth()
  const permanentStore = usePermanentStore()
  const tutorStore = useTutorStore()
  const { isTrainProgsFetched, isModulesFetched } = storeToRefs(permanentStore)
  if (deptStore.current.id === -1) deptStore.getDepartmentFromURL(to.fullPath)
  if (!authStore.isUserFetchTried) await authStore.fetchAuthUser()
  if (!isModulesFetched.value) await permanentStore.fetchModules()
  if (!isTrainProgsFetched.value) await permanentStore.fetchTrainingProgrammes()
  if (!tutorStore.isAllTutorsFetched) await tutorStore.fetchTutors()
  if (!deptStore.isAllDepartmentsFetched) await deptStore.fetchAllDepartments()
  if (!roomStore.isRoomFetched) await roomStore.fetchRooms()
  availableLocales.forEach((currentLocale: 'fr' | 'en' | 'es') => {
    to.fullPath.split('/').forEach((arg) => {
      if (arg.includes(currentLocale) && arg.length === currentLocale.length) {
        locale.value = currentLocale
      }
    })
  })
  if (to.meta.needsAuth && !authStore.isUserAuthenticated) {
    next({ path: `/login/${deptStore.current.abbrev}`, query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

router.afterEach((to) => {
  document.title = to.meta.title as string
})

export default router
