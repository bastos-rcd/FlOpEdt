<template>
  <!-- <h3>{{ $t('authentication.title') }}</h3>
  <p>{{ $t('authentication.message') }}</p> -->
  <fieldset class="login">
    <legend>Authentification</legend>
    <div class="form-row">
      <label for="username" class="form-left">Nom d'utilisat.eur.rice</label>
      <input id="username" v-model="username" class="form-right" placeholder="JohnDoe" />
    </div>
    <div class="form-row">
      <label for="password" class="form-left">Mot de passe</label>
      <input id="password" v-model="password" class="form-right" placeholder="" type="password" />
    </div>
    <div class="form-row">
      <!-- <span class="form-left">
        <a href=""> Mot de passe oublié ? </a>
      </span> -->
      <input class="submit form-right" type="button" value="Connexion" @click="submitAction" />
    </div>
  </fieldset>
  <span> {{ authMessage }}</span>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { getCookie } from '@/utils/api'
import { useAuth } from '@/stores/auth'
const username = ref('')
const password = ref('')
const authMessage = ref('')
const router = useRouter()

const authStore = useAuth()
const csrfToken = getCookie('csrftoken')

function submitAction() {
  console.log(getCookie('sessionid'))
  fetch('/fr/accounts/login-vue/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      //'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ username: username.value, password: password.value }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Response not ok')
      }
      return response.json()
    })
    .then((data) => {
      console.log(data)
      if (data.message === 'Login successful') {
        authMessage.value = 'Authentification réussie.'
        return authStore.fetchAuthUser()
      } else {
        throw new Error(data.message)
      }
    })
    .then(() => {
      return router.push('/')
    })
    .catch((error) => {
      console.log(error)
      authMessage.value = "L'authentification a échoué."
    })
  // console.log(route.query.redirect)
  // if (route.query.meta !== null) window.location.href = route.query.redirect as string
}
</script>

<style scoped>
h3 {
  font-weight: bolder;
  margin-top: 10px;
}
legend {
  position: relative;
  /* top: -10px; */
  /* left: 20px; */
  height: 20px;
  width: 120px;
  background: rgb(90, 89, 89);
  text-align: center;
  font-size: medium;
}
label,
span {
  color: black;
}
fieldset {
  border: 3px black;
  border-style: outset;
  margin-right: 10%;
  margin-left: 10%;
  padding-bottom: 10px;
  padding-left: 15px;
  padding-right: 15px;
}
.form-row {
  display: flex;
  flex-direction: row;
}
.form-right {
  flex-grow: 2;
  max-width: 50%;
}
.form-left {
  flex-grow: 1;
}
</style>
