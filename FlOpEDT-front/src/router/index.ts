import { createRouter, createWebHistory } from 'vue-router'

export const routeNames = {
    departmentSelection: Symbol('department-selection'),
    home: Symbol('home'),
    roomReservation: Symbol('room-reservation'),
}

const routes = [
    {
        path: '/',
        name: routeNames.departmentSelection,
        component: () => import('@/views/DepartmentSelectionView.vue'),
    },
    {
        path: '/edt/:dept',
        name: routeNames.home,
        component: () => import('@/views/HomeView.vue'),
    },
    {
        path: '/roomreservation/:dept',
        name: routeNames.roomReservation,
        component: () => import('@/views/RoomReservationView.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
})

export default router
