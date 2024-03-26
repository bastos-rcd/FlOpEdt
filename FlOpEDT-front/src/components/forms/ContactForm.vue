<template>
  <form method="post" action="/fr/api/base/contact">
    <legend>{{ $t('contact.title') }}</legend>
    <fieldset>
      <legend>{{ $t('contact.infos-title') }}</legend>
      <label for="email">{{ $t('contact.email-label') }}</label>
      <input
        id="email"
        v-model="emailadress"
        type="email"
        :placeholder="$t('contact.email-placeholder')"
        required
        @input="updateEmail()"
      />
      <label for="recipient">{{ $t('contact.recipient-label') }}</label>
      <input
        id="recipient"
        v-model="recipient"
        maxlength="20"
        :placeholder="$t('contact.recipient-placeholder')"
        required
        @input="updateRecipient()"
      />
    </fieldset>
    <fieldset>
      <legend>{{ $t('contact.message-title') }}</legend>
      <label for="subject">{{ $t('contact.object-label') }}</label>
      <input
        id="subject"
        v-model="subject"
        type="text"
        maxlength="100"
        :placeholder="$t('contact.object-placeholder')"
        required
        @input="updateSubject()"
      />

      <label for="message">{{ $t('contact.message-label') }}</label>
      <textarea
        id="message"
        v-model="message"
        cols="50"
        rows="10"
        maxlength="2000"
        :placeholder="$t('contact.message-placeholder')"
        required
        @input="updateMessage()"
      >
      </textarea>
    </fieldset>
    <input class="form-button" type="submit" :value="$t('contact.submit-button')" />
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emailadress = ref('')
const recipient = ref('')
const subject = ref('')
const message = ref('')

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
  background: linear-gradient(#b4bbbe, #f3f3f3);
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
input,
textarea {
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
  background: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.1));
  width: 100%;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
}
.form-button:hover {
  background: #9bb6a4;
}
</style>
