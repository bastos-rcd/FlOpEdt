<template>
  <form method="get" action="">
    <legend>Formulaire de contact</legend>
    <fieldset>
      <legend>Coordonnées et Destinataire</legend>
      <label for="email">Votre adresse mail</label> 
      <input v-model="emailadress" id="email" type="email" @input="updateEmail()" placeholder="your@adresse.mail" required/>
      <label for="recipient">Nom de votre destinataire</label>
      <input 
        v-model="recipient"
        id="recipient"
        maxlength="20" 
        @input="updateRecipient()" 
        placeholder="Dupont" 
        required/>

    </fieldset>
    <fieldset>
      <legend>Votre message</legend>
      <label for="subject">Objet de votre message</label>
      <input 
        v-model="subject"
        type="text"
        maxlength="100"
        id="subject" 
        @input="updateSubject()" 
        placeholder="Final physics exam" 
        required/>

      <label for="subject">Votre message</label>
      <textarea 
        v-model="message" 
        id="message" 
        cols="50" 
        rows="10"
        maxlength="2000"
        @input="updateMessage()" 
        placeholder="Hello Pr Dupont, when is our final exam ?" 
        required>
      </textarea>
    </fieldset>
    <input class="form-button" type="submit" value="Envoyer"/>  
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emailadress = ref("")
const recipient = ref("")
const subject = ref("")
const message = ref("")

function updateEmail() {
    console.log(emailadress.value)
}
function updateRecipient() {
    console.log(recipient.value)
}
function updateSubject() {
    console.log(subject.value)
}
function updateMessage() {
    console.log(message.value)
}
</script>

<style scoped>
fieldset {
  background: linear-gradient(#b4bbbe ,#f3f3f3);
  border-radius: 10px;
  border-style: solid;
  border-color: #000000;
  border-width: 3px;
  margin-bottom: 4px;
  margin-top: 4px;
  width: 80%;
  margin-left: 10%;
  margin-right: 10%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
legend {
  font-weight: bolder;
}
input, textarea {
  background-color: aliceblue;
  color: black;
  margin: 10px;
  border-radius: 5px;
}
label {
  font-weight: bolder;
  padding-right: 4px;
}
form {
  background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.1));
  width: 100%;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
}
.form-button:hover {
  background: #9bb6a4;
}

</style>