import { createRouter, createWebHistory } from 'vue-router'

export const routeNames = {
    departmentSelection: Symbol('department-selection'),
    home: Symbol('home'),
    roomReservation: Symbol('room-reservation'),
    back: Symbol('back'),
    notFound: Symbol('notFound'),
}

const routes = [
    {
        path: '/',
        name: routeNames.departmentSelection,
        component: () => import('@/views/DepartmentSelectionView.vue'),
        meta: {
            title: 'Ca floppe !',
        },
    },
    {
        path: '/edt/:dept',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
            title: 'Emploi du temps',
        },
    },
    {
        path: '/roomreservation/:dept',
        name: routeNames.roomReservation,
        component: () => import('@/views/RoomReservationView.vue'),
        meta: {
            title: 'Réservation de salles',
        },
    },
    {
        path: '/back',
        name: routeNames.back,
        component: () => import('@/views/BackView.vue'),
        meta: {
            title: 'Back to back',
        },
    },
    {
        path: '/:pathMatch(.*)',
        name: routeNames.notFound,
        component: () => import('@/views/NotFoundView.vue'),
        meta: {
            title: '404 Not Found',
        },
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
})

router.afterEach((to) => {
    document.title = to.meta.title as string
})

export default router
