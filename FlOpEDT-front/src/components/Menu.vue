<template>
    <div class="menu-links">
        <ul>
            <li><router-link :to="{name: routeNames.home, params:{}}">Home</router-link></li>
        </ul>
        <ul v-if="deptStore.isCurrentDepartmentSelected"> 
            <li>
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/`">Consulter</a>
            </li>
            <li>
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/semaine-type`">Préférences</a>
            </li>
            <li>
                <a :href="`/fr/ics/${deptStore.getCurrentDepartment.abbrev}/`">iCal</a>
            </li>
            <li>
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/aide`">Aide</a>
            </li>
            <li>
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/contact/`">Contact</a>
            </li>
            <li>
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/modules`">Module</a>
            </li>
            <li>
                <router-link :to="{name: routeNames.roomReservation, params:{}}">Room reservation</router-link>
            </li>
        </ul>
        <ul v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
            <li>
                <a href="/fr/edt/INFO/decale">Décaler/Annuler</a>
            </li>
            <li>
                <a href="/fr/cstmanager/manager/">Contraintes</a>
            </li>
            <li>
                <a :href="`/fr/solve-board/${deptStore.getCurrentDepartment.abbrev}/main/`">Générer</a>
            </li>
            <li>
                <a :href="`/fr/flopeditor/${deptStore.getCurrentDepartment.abbrev}/parameters`">Flop!EDITOR</a>
            </li>
            <li>
                <a href="/fr/configuration/">Importer</a>
            </li>
            <li>
                <a href="/fr/admin/">Admin</a>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { routeNames } from '@/router'
const authStore = useAuth()
const deptStore = useDepartmentStore()
</script>

<style scoped>
.menu-links{
    display: flex;
    flex-direction: column;
}
li {
  list-style: none;
  display: inline;
  margin: 5px;
  padding: 15px;
  border-radius: 20%;
  background-color: aliceblue;
  border-color: rgb(200,200,200);
  border-style: solid;
  border-width: 1px;
}
li:hover {
  background-color:rgb(200, 200, 200);
}
</style>
