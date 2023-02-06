<template>
  <header>
    <ul>
      <li><router-link :to="{name: routeNames.home, params:{}}">Home</router-link></li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/`">Consulter</a></li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a href="/fr/edt/INFO/decale">Décaler/Annuler</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/semaine-type`">Préférences</a></li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/ics/${deptStore.getCurrentDepartment.abbrev}/`">iCal</a></li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/aide`">Aide</a></li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/contact/`">Contact</a></li>
      <li v-if="deptStore.isCurrentDepartmentSelected"><a :href="`/fr/edt/${deptStore.getCurrentDepartment.abbrev}/modules`">Module</a></li>
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
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <router-link :to="{name: routeNames.roomReservation, params:{}}">Room reservation</router-link>
      </li>
      <li>
        <router-link :to="{name: routeNames.departmentSelection, params:{}}">Sélection du département</router-link>
      </li>
    </ul>
  </header>
  <router-view></router-view>
  <footer>

  </footer>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from './stores/auth'
import { useDepartmentStore } from './stores/department';
import { routeNames } from '@/router'

const authStore = useAuth()
const deptStore = useDepartmentStore()

onMounted(() => {
  authStore.fetchAuthUser()
  deptStore.fetchAllDepartments()
})

</script>

<style scoped>
li {
  list-style: none;
  display: inline;
  margin: 5px;
  padding: 5px;
  border-radius: 10%;
  background-color: aliceblue;
}
li:hover {
  background-color:rgb(255, 240, 222);
}
</style>
