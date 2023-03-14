<template>
    <h3>{{$t('authentication.title')}}</h3>
    <p>{{ $t("authentication.message") }}</p>
    <fieldset class="login">
        <legend>Authentification</legend>
        <div class="form-row">
            <label for="username" class="form-left">Nom d'utilisat.eur.rice</label>
            <input 
                id="username"
                class="form-right"
                v-model="username"
                placeholder="JohnDoe"/>
        </div>
        <div class="form-row">
            <label for="password" class="form-left">Mot de passe</label>
            <input
                id="password"
                class="form-right"
                v-model="password"
                placeholder=""
                type="password"/>
        </div>
        <div class="form-row">
            <span class="form-left">
                <a href="">
                    Mot de passe oublié ?
                </a>
            </span>
            <input class="submit form-right" type="button" value="Connexion" @click="submitAction"/>
        </div>
    </fieldset>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router'
const t = useI18n()
const username = ref("")
const password = ref("")
const route = useRoute()

function submitAction() {
    console.log(route.query.redirect)
    if(route.query.meta !== null)
        window.location.href = route.query.redirect as string
}
</script>


<style scoped>
h3 {
    font-weight: bolder;
    margin-top: 10px;
}
legend {
    position: relative;
    top: -10px;
    left: 20px;
    height: 20px;
    width: 120px;
    background: rgb(214, 214, 214);
    text-align: center;
    font-size: medium;
}
fieldset {
    border: 3px black;
    border-style:outset;
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