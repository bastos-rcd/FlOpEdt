<template>
  <header>
    <ul>
      <li><router-link :to="{name: routeNames.home, params:{}}">Home</router-link></li>
      <li><a href="/fr/edt/INFO/">Consulter</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/edt/INFO/decale">Décaler/Annuler</a></li>
      <li><a href="/fr/edt/INFO/semaine-type">Préférences</a></li>
      <li><a href="/fr/ics/INFO/">iCal</a></li>
      <li><a href="/fr/edt/INFO/aide">Aide</a></li>
      <li><a href="/fr/edt/INFO/contact/">Contact</a></li>
      <li><a href="/fr/edt/INFO/modules">Module</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/cstmanager/manager/">Contraintes</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/solve-board/INFO/main/">Générer</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/flopeditor/INFO/parameters">Flop!EDITOR</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/configuration/">Importer</a></li>
      <li v-if="authStore.isUserAuthenticated"><a href="/fr/admin/">Admin</a></li>
      <li><router-link :to="{name: routeNames.roomReservation, params:{}}">Room reservation</router-link></li>
      <li><router-link :to="{name: routeNames.departmentSelection, params:{}}">Sélection du département</router-link></li>
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
