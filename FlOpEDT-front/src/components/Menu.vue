<template>
  <nav id="menu-links">
    <div class="mobile-menu-button">
      <Icon icon="iconoir:menu" class="IconMenu" @click="toggleMobileMenu"></Icon>
      <label class="mobile-button" @click="toggleMobileMenu">{{ page.name }}</label>
      <button class="sidebar-button" @click="toggleSideBar()">
        <Icon icon="iconoir:filter" class="IconMenu"></Icon>
        FILTRES
      </button>
    </div>
    <ul :class="{ 'mobile-menu-open': isMobileMenuOpen }">
      <li v-if="authStore.isUserAuthenticated && !isMobileMenuOpen">
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
          @click="page.name = $t('navbar.home')"
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
          @click="page.name = $t('navbar.schedule')"
          >{{ $t('navbar.schedule') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a
          :href="`/${locale}/edt/${deptStore.current.abbrev}/semaine-type`"
          @click="page.name = $t('navbar.preferences')"
          >{{ $t('navbar.preferences') }}</a
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/ics/${deptStore.current.abbrev}/`" @click="page.name = $t('navbar.iCal')">{{
          $t('navbar.iCal')
        }}</a>
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.current.abbrev}/aide`" @click="page.name = $t('navbar.help')">{{
          $t('navbar.help')
        }}</a>
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
          @click="page.name = $t('navbar.messages')"
          >{{ $t('navbar.messages') }}</router-link
        >
      </li>
      <li v-if="deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/${deptStore.current.abbrev}/modules`" @click="page.name = $t('navbar.modules')">{{
          $t('navbar.modules')
        }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/edt/INFO/decale`" @click="page.name = $t('navbar.move-cancel')">{{
          $t('navbar.move-cancel')
        }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/cstmanager/manager/`" @click="page.name = $t('navbar.constraints')">{{
          $t('navbar.constraints')
        }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a
          :href="`/${locale}/solve-board/${deptStore.current.abbrev}/main/`"
          @click="page.name = $t('navbar.generate')"
          >{{ $t('navbar.generate') }}</a
        >
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a
          :href="`/${locale}/flopeditor/${deptStore.current.abbrev}/parameters`"
          @click="page.name = $t('navbar.flop-editor')"
          >{{ $t('navbar.flop-editor') }}</a
        >
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/configuration/`" @click="page.name = $t('navbar.import')">{{ $t('navbar.import') }}</a>
      </li>
      <li v-if="authStore.isUserAuthenticated && deptStore.isCurrentDepartmentSelected">
        <a :href="`/${locale}/admin/`" @click="page.name = $t('navbar.admin')">{{ $t('navbar.admin') }}</a>
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
import { ref } from 'vue'
import { usePageStore } from '@/stores/page'

const authStore = useAuth()
const deptStore = useDepartmentStore()
const { locale } = useI18n()
const router = useRouter()
const page = usePageStore()

const isMobileMenuOpen = ref(false)

onMounted(() => {
  if (!deptStore.isCurrentDepartmentSelected) {
    deptStore.getDepartmentFromURL()
  }
})

function toggleSideBar() {
  authStore.toggleSidePanel()
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
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
  align-items: center;
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
  color: #4747b2;
}
.sidebar-button {
  width: 85px;
  height: 50px;
  background-color: rgba(0, 0, 0, 0);
}
.mobile-menu-button {
  display: none;
}

.mobile-button {
  color: #4747b2;
  font-size: 18px;
  margin-left: 5px;
  margin-right: 5px;
}

@media (max-width: 768px) {
  #menu-links {
    flex-direction: column;
    align-items: flex-start;
  }
  #menu-links ul {
    display: none;
    width: 100%;
    flex-direction: column;
    background-color: transparent;
    border-bottom: 1px solid black;
    margin-bottom: 20px;
  }
  #menu-links ul.mobile-menu-open {
    display: flex;
  }
  #menu-links li {
    float: none;
    width: 100%;
    text-align: left;
  }
  #menu-links li a,
  #menu-links li span {
    color: #4747b2;
  }
  .mobile-menu-button {
    display: flex;
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    padding: 10px;
    align-items: center;
    width: 100%;
    justify-content: space-between;
  }
  .sidebar-button {
    width: 90px;
    height: 30px;
    background-color: #ffffff;
    border: 1px solid #e3e3e3;
    border-radius: 50px;
    font-size: x-small;
  }
  .IconMenu {
    vertical-align: text-top;
  }
}
</style>