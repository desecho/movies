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
            v-model="email"
            variant="solo"
            :rules="[rules.required]"
            type="email"
            label="Email"
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
            <v-btn color="primary" :disabled="!isFormValid" @click="onSubmit">Register</v-btn>
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
import { useRouter } from "vue-router";

import type { CheckEmailAvailabilityErrorData } from "./types";
import type { AxiosError } from "axios";

import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const rules = rulesHelper;

const username = ref("");
const email = ref("");
const password = ref("");
const showPassword = ref(false);
const isFormValid = ref(false);

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

const { form, isValid } = useFormValidation();
const router = useRouter();

async function onSubmit(): Promise<void> {
  if (!(await isValid())) {
    return;
  }
  axios
    .post(getUrl("user/check-email-availability/"), { email: email.value })
    .then((response) => {
      const isEmailAvailable = response.data as boolean;
      if (isEmailAvailable) {
        axios
          .post(getUrl("user/register/"), {
            username: username.value,
            email: email.value,
            password: password.value,
          })
          .then(() => {
            $toast.success("You should receive an email to confirm registration");
            void router.push("/register/success");
          })
          .catch((error: AxiosError) => {
            console.log(error);
            if (error.response?.data === undefined) {
              $toast.error("Registration error");
            } else {
              const data = error.response.data as CheckEmailAvailabilityErrorData;
              if (data.password !== undefined) {
                data.password.forEach((err) => {
                  $toast.error(err);
                });
              }
              if (data.email !== undefined) {
                data.email.forEach((err) => {
                  $toast.error(err);
                });
              }
              if (data.username !== undefined) {
                data.username.forEach((err) => {
                  $toast.error(err);
                });
              }
            }
          });
      } else {
        $toast.error("A user with this email is already registered");
      }
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error checking email availability");
    });
}
</script>
