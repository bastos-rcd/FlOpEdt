import { createRouter, createWebHistory } from 'vue-router'

export const routeNames = {
    home: Symbol('Home'),
    roomReservation: Symbol('room-reservation'),
    departmentSelection: Symbol('department-selection'),
    contact: Symbol('contact'),
    notFound: Symbol('notFound'),
}

const routes = [
    {
        path: '/roomreservation/:dept?',
        name: routeNames.roomReservation,
        component: () => import('@/views/RoomReservationView.vue'),
        meta: {
            title: 'Réservation de salles',
        },
    },
    {
        path: '/contact/:dept?',
        name: routeNames.contact,
        component: () => import('@/views/ContactView.vue'),
        meta: {
            title: 'Contact page',
        },
    },
    {
        path: '/:dept?',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
        meta: {
            title: 'Ca floppe !',
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