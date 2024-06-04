<template>
  <div id="full_logo" style="display: none">
    <span id="head_logo"></span>
    <ChangeLocale></ChangeLocale>
    <div style="margin-left: 10px; border: 2px solid black; padding: 3px; background-color: antiquewhite">
      <span v-if="authStore.isUserAuthenticated">{{ $t('header.logged-in') + authStore.getUser.username }}</span>
      <span v-else>{{ $t('header.logged-out') }}</span>
    </div>
  </div>
  <Menu></Menu>
</template>

<script setup lang="ts">
import Menu from '@/components/Menu.vue'
import ChangeLocale from '@/components/utils/ChangeLocale.vue'
import { useAuth } from '@/stores/auth'

const authStore = useAuth()
</script>

<style scoped>
#flopGreen {
  color: green;
  font-family: inherit;
  font-size: inherit;
}
#EDTRed {
  color: red;
  font-family: inherit;
  font-size: inherit;
}
#agpl {
  font-size: 10px;
  margin-left: auto;
  margin-top: 40px;
  margin-right: 10px;
  font-weight: 600;
}
#head_logo {
  font-size: 16px;
  font-family: 'Verdana';
  font-weight: bold;
  opacity: 0.7;
  margin-top: 45px;
  margin-left: 10px;
}
#full_logo {
  padding-top: 0px;
  font-family: 'flog';
  display: flex;
  flex-direction: row;
  color: black;
  align-items: center;
}
#acro_logo {
  font-size: 70px;
  font-family: inherit;
  font-weight: normal;
}
</style>
