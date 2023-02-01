<template>
  <header>
    <ul>
      <li><router-link to="/">Home</router-link></li>
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
      <li><router-link to="/roomreservation">Room reservation</router-link></li>
    </ul>
  </header>
  <router-view></router-view>
  <footer>

  </footer>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from './stores/auth'

const authStore = useAuth()

onMounted(() => {
  authStore.getAuthUser()
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
