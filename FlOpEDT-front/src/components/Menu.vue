<template>
    <nav id="menu-links">
        <ul>
            <li><router-link :to="{name: routeNames.home, params:{dept: deptStore.getCurrentDepartment.abbrev}}">Home</router-link></li> 
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/`">Consulter</a>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/semaine-type`">Préférences</a>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/ics/${deptStore.getCurrentDepartment.abbrev}/`">iCal</a>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/aide`">Aide</a>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <router-link :to="{name: routeNames.contact, params:{dept:deptStore.getCurrentDepartment.abbrev}}">Contact</router-link>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/modules`">Module</a>
            </li>
            <li v-if="deptStore.isCurrentDepartmentSelected">
                <router-link :to="{name: routeNames.roomReservation, params:{dept:deptStore.getCurrentDepartment.abbrev}}">Room reservation</router-link>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a href="/fr/edt/INFO/decale">Décaler/Annuler</a>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a href="/fr/cstmanager/manager/">Contraintes</a>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/solve-board/${deptStore.getCurrentDepartment.abbrev}/main/`">Générer</a>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a :href="`/fr/flopeditor/${deptStore.getCurrentDepartment.abbrev}/parameters`">Flop!EDITOR</a>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a href="/fr/configuration/">Importer</a>
            </li>
            <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
                <a href="/fr/admin/">Admin</a>
            </li>
        </ul>
    </nav>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { routeNames } from '@/router'
import { onMounted } from 'vue';
const authStore = useAuth()
const deptStore = useDepartmentStore()

onMounted(() => {
    if(!deptStore.isCurrentDepartmentSelected) {
        deptStore.getDepartmentFromURL()
    }
})
</script>

<style scoped>
a {
    text-decoration: none;
}
#menu-links{
    display: flex;
    flex-direction:row;
    color: white;
    font-size:14px;
}
#menu-links li {
  float: left;
  border-right:1px solid #bbb;
}
#menu-links li a {
    color: white;
    display: block;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
    font-weight:bold;
}
#menu-links ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #333;
  width: 100%;
}
li:hover {
  background-color:rgb(200, 200, 200);
}
</style>
