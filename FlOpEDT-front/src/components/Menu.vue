<template>
  <nav id="menu-links">
    <ul>
      <li v-if="authStore.isUserAuthenticated">
        <button class="sidebar-button" @click="toggleSideBar()">
          <Icon icon="iconoir:menu" class="IconMenu"></Icon>
        </button>
      </li>
      <li>
        <router-link
          :to="{
            name: routeNames.home,
            params: {
              dept: deptStore.current.abbrev,
              locale: locale,
            },
          }"
          >{{ $t('navbar.home') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <router-link
          :to="{
            name: routeNames.schedule,
            params: {
              dept: deptStore.current.abbrev,
              locale: locale,
            },
          }"
          >{{ $t('navbar.schedule') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.current.abbrev}/semaine-type`">{{ $t('navbar.preferences') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/ics/${deptStore.current.abbrev}/`">{{ $t('navbar.iCal') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.current.abbrev}/aide`">{{ $t('navbar.help') }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <router-link
          :to="{
            name: routeNames.contact,
            params: {
              dept: deptStore.current.abbrev,
              locale: locale,
            },
          }"
          >{{ $t('navbar.messages') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.current.abbrev}/modules`">{{ $t('navbar.modules') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/INFO/decale`">{{ $t('navbar.move-cancel') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/cstmanager/manager/`">{{ $t('navbar.constraints') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/solve-board/${deptStore.current.abbrev}/main/`">{{ $t('navbar.generate') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/flopeditor/${deptStore.current.abbrev}/parameters`">{{ $t('navbar.flop-editor') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/configuration/`">{{ $t('navbar.import') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/admin/`">{{ $t('navbar.admin') }}</a>
      </li>
      <li v-if="!authStore.isUserAuthenticated" style="float: right">
        <a :href="`/login/`">Se connecter</a>
      </li>
      <li v-else style="float: right">
        <span @click="logout">Se déconnecter</span>
        <!-- <a :href="`/${locale}/accounts/logout-vue/`"></a> -->
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { useAuth } from '@/stores/auth'
import { useDepartmentStore } from '@/stores/department'
import { routeNames } from '@/router'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'

const authStore = useAuth()
const deptStore = useDepartmentStore()
const { locale } = useI18n()
const router = useRouter()
onMounted(() => {
  if (!deptStore.isCurrentDepartmentSelected) {
    deptStore.getDepartmentFromURL()
  }
})

function toggleSideBar() {
  authStore.toggleSidePanel()
}

function logout() {
  console.log('logout')
  fetch(`/${locale.value}/accounts/logout-vue`, { method: 'GET', credentials: 'include' })
    .then((response) => {
      if (response.ok) {
        return authStore.fetchAuthUser()
      }
    })
    .then(() => {
      return router.push('/')
    })
    .catch((error) => {
      console.log(error)
    })
}
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
  min-width: 85px;
  min-height: 50px;
}
#menu-links li a,
#menu-links li span {
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
.IconMenu {
  color: red;
}
.sidebar-button {
  width: 85px;
  height: 50px;
  background-color: rgba(0, 0, 0, 0);
}
</style>
