<template>
  <v-container>
    <v-row class="text-center">
      <v-col class="mb-4" cols="12">
        <v-form v-if="!isLoggedIn" ref="form" v-model="isFormValid" lazy-validation @submit.prevent="onSubmit">
          <v-text-field
            v-model="username"
            variant="solo"
            label="Username"
            :rules="[rules.required]"
            :autofocus="true"
            @keyup.enter="onSubmit"
          ></v-text-field>
          <div class="d-flex justify-space-around align-center flex-column flex-md-row">
            <v-btn color="primary" :disabled="!isFormValid" @click="onSubmit">Reset password</v-btn>
          </div>
        </v-form>
        <p v-if="isLoggedIn">You are already logged in.</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { AxiosError } from "axios";

import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const rules = rulesHelper;

const username = ref("");
const isFormValid = ref(false);

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

const { form, isValid } = useFormValidation();

async function onSubmit(): Promise<void> {
  if (!(await isValid())) {
    return;
  }
  axios
    .post(getUrl("user/send-reset-password-link/"), {
      login: username.value,
    })
    .then(() => {
      $toast.success("You should receive an email with a password reset link");
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error resetting password");
    });
}
</script>
