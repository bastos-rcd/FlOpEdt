<template>
    <div id="app">
        <header class="border-solid border-bottom mb-5">
            <h1>HEADER</h1>
            <ul>
                <li>
                    <router-link :to="{ name: routeNames.departmentSelection }"> Home</router-link>
                </li>
                <li v-if="'dept' in useRoute().params">
                    <router-link
                        :to="{
                            name: routeNames.roomReservation,
                            params: useRoute().params,
                        }"
                    >
                        Room Reservation
                    </router-link>
                </li>
            </ul>
        </header>

        <RouterView />

        <footer class="border-solid border-top mt-5">
            <h1>FOOTER</h1>
        </footer>
    </div>
</template>

<script setup lang="ts">
import { routeNames } from '@/router'
import { RouterLink, RouterView, useRoute } from 'vue-router'
</script>

<style scoped></style>
