<template>
  <nav id="menu-links">
    <ul>
      <li>
        <router-link
          :to="{
            name: routeNames.home,
            params: {
              dept: deptStore.getCurrentDepartment.abbrev,
              locale: locale,
            },
          }"
          >{{ $t('navbar.home') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.getCurrentDepartment.abbrev}/`">{{ $t('navbar.schedule') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.getCurrentDepartment.abbrev}/semaine-type`">{{
          $t('navbar.preferences')
        }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/ics/${deptStore.getCurrentDepartment.abbrev}/`">{{ $t('navbar.iCal') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.getCurrentDepartment.abbrev}/aide`">{{ $t('navbar.help') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <router-link
          :to="{
            name: routeNames.contact,
            params: {
              dept: deptStore.getCurrentDepartment.abbrev,
              locale: locale,
            },
          }"
          >{{ $t('navbar.messages') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.getCurrentDepartment.abbrev}/modules`">{{ $t('navbar.modules') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/INFO/decale`">{{ $t('navbar.move-cancel') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/cstmanager/manager/`">{{ $t('navbar.constraints') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/solve-board/${deptStore.getCurrentDepartment.abbrev}/main/`">{{
          $t('navbar.generate')
        }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/flopeditor/${deptStore.getCurrentDepartment.abbrev}/parameters`">{{
          $t('navbar.flop-editor')
        }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/configuration/`">{{ $t('navbar.import') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/admin/`">{{ $t('navbar.admin') }}</a>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { routeNames } from '@/router'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const authStore = useAuth()
const deptStore = useDepartmentStore()
const { t, locale } = useI18n()
onMounted(() => {
  if (!deptStore.isCurrentDepartmentSelected) {
    deptStore.getDepartmentFromURL()
  }
})
</script>

<style scoped>
a {
  text-decoration: none;
}
#menu-links {
  display: flex;
  flex-direction: row;
  color: white;
  font-size: 14px;
}
#menu-links li {
  float: left;
  border-right: 1px solid #bbb;
}
#menu-links li a {
  color: white;
  display: block;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  font-weight: bold;
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
  background-color: rgb(200, 200, 200);
}
</style>
