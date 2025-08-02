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
          <v-text-field
            v-model="password"
            variant="solo"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[rules.required]"
            :type="showPassword ? 'text' : 'password'"
            label="Password"
            @click:append="showPassword = !showPassword"
            @keyup.enter="onSubmit"
          ></v-text-field>
          <div class="d-flex justify-space-around align-center flex-column flex-md-row">
            <v-btn color="primary" :disabled="!isFormValid" @click="onSubmit">Login</v-btn>
          </div>
        </v-form>
        <br />
        <div v-if="!isLoggedIn">
          <div class="d-flex justify-space-around align-center flex-column flex-md-row">
            <v-btn color="primary" to="/register">Register</v-btn>
          </div>
          <br />
          <div class="d-flex justify-space-around align-center flex-column flex-md-row">
            <v-btn color="primary" to="/reset-password-request">Reset password</v-btn>
          </div>
        </div>
        <p v-if="isLoggedIn">You are already logged in.</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { ref } from "vue";

import type { TokenErrorData } from "./types";
import type { AxiosError } from "axios";

import { useFormValidation } from "../composables/formValidation";
import { rulesHelper } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const rules = rulesHelper;

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const isFormValid = ref(false);

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

const { form, isValid } = useFormValidation();

async function onSubmit(): Promise<void> {
  if (!(await isValid())) {
    return;
  }
  const { login } = useAuthStore();
  try {
    await login(username.value, password.value);
  } catch (error) {
    console.log(error);
    const errorAxios = error as AxiosError;
    const data = errorAxios.response.data as TokenErrorData;
    $toast.error(data.detail);
  }
}
</script>
