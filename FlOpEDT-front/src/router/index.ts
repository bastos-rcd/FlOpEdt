import { createRouter, createWebHistory } from 'vue-router'

export const routeNames = {
    departmentSelection: Symbol('department-selection'),
    home: Symbol('Home'),
    roomReservation: Symbol('room-reservation'),
    notFound: Symbol('notFound'),
}

const routes = [
    {
        path: '/',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
            title: 'Ca floppe !',
        },
    },
    /*{
        path: '/edt/:dept',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
            title: 'Emploi du temps',
        },
    },*/
    {
        path: '/roomreservation/',
        name: routeNames.roomReservation,
        component: () => import('@/views/RoomReservationView.vue'),
        meta: {
            title: 'Réservation de salles',
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