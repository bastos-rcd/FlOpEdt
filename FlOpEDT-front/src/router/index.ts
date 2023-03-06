import { createRouter, createWebHistory } from 'vue-router'
import { useDepartmentStore } from '@/stores/department'
import { useAuth } from '@/stores/auth'
import  i18n from '@/i18n';

export const routeNames = {
    home: Symbol('Home'),
    roomReservation: Symbol('room-reservation'),
    departmentSelection: Symbol('department-selection'),
    contact: Symbol('contact'),
    notFound: Symbol('notFound'),
    login: Symbol('login')
}

const routes = [
    {
        path: '/roomreservation/:locale?/:dept?',
        name: routeNames.roomReservation,
        component: () => import('@/views/RoomReservationView.vue'),
        meta: {
            title: 'Réservation de salles',
            needsAuth: true,
        },
    },
    {
        path: '/contact/:locale?/:dept?',
        name: routeNames.contact,
        component: () => import('@/views/ContactView.vue'),
        meta: {
            title: 'Contact',
            needsAuth: true,
        },
    },
    {
        path: '/:locale?/:dept?',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
            title: 'Ca floppe !',
            needsAuth: false,
        },
    },
    {
        path: '/:locale?/:pathMatch(.*)',
        name: routeNames.notFound,
        component: () => import('@/views/NotFoundView.vue'),
        meta: {
            title: '404 Not Found',
            needsAuth: false,
        },
    },    
    {
        path: '/login/:locale?/:dept?',
        name: routeNames.login,
        component: () => import('@/views/LoginView.vue'),
        meta: {
            title: 'Connexion',
            needsAuth: false,
            nextPath: ''
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
    const authStore = useAuth()
    if(deptStore.getCurrentDepartment.id === -1) 
        deptStore.getDepartmentFromURL(to.fullPath)

    if(!authStore.isUserFetchTried) 
        await authStore.fetchAuthUser()

    availableLocales.forEach((currentLocale: string) => {
        to.fullPath.split('/').forEach(arg => {
            if(arg.includes(currentLocale) && arg.length === currentLocale.length) {
                locale.value = currentLocale
            }
        })
    })
    if(to.meta.needsAuth && !authStore.isUserAuthenticated) { 
        next({ path: `/login/${deptStore.getCurrentDepartment.abbrev}`, query: { redirect: to.fullPath } })
    } else {
        next()
    }
})

router.afterEach((to) => {
    document.title = to.meta.title as string
})

export default router