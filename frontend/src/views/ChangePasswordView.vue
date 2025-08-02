<template>
  <v-container>
    <v-row class="text-center">
      <v-col class="mb-4" cols="12">
        <v-form ref="form" v-model="isFormValid" lazy-validation @submit.prevent="onSubmit">
          <v-text-field
            v-model="oldPassword"
            variant="solo"
            :append-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[rules.required]"
            :type="showOldPassword ? 'text' : 'password'"
            label="Old Password"
            @click:append="showOldPassword = !showOldPassword"
            @keyup.enter="onSubmit"
          ></v-text-field>
          <v-text-field
            v-model="password"
            variant="solo"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[rules.required]"
            :type="showPassword ? 'text' : 'password'"
            label="New Password"
            @click:append="showPassword = !showPassword"
            @keyup.enter="onSubmit"
          ></v-text-field>
          <div class="d-flex justify-space-around align-center flex-column flex-md-row">
            <v-btn color="primary" :disabled="!isFormValid" @click="onSubmit">Change password</v-btn>
          </div>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { ref } from "vue";

import type { ChangePasswordErrorData } from "./types";
import type { AxiosError } from "axios";

import { useFormValidation } from "../composables/formValidation";
import { getUrl, rulesHelper } from "../helpers";
import { router } from "../router";
import { $toast } from "../toast";

const rules = rulesHelper;

const password = ref("");
const showPassword = ref(false);
const oldPassword = ref("");
const showOldPassword = ref(false);
const isFormValid = ref(false);

const { form, isValid } = useFormValidation();

async function onSubmit(): Promise<void> {
  if (!(await isValid())) {
    return;
  }
  axios
    .post(getUrl("user/change-password/"), {
      // eslint-disable-next-line camelcase
      old_password: oldPassword.value,
      password: password.value,
    })
    .then(() => {
      $toast.success("Password has been changed successfully");
      void router.push("/preferences");
    })
    .catch((error: AxiosError) => {
      console.log(error);
      if (error.response?.data === undefined) {
        $toast.error("Error changing password");
      } else {
        const data = error.response.data as ChangePasswordErrorData;
        if (data.password !== undefined) {
          data.password.forEach((err) => {
            $toast.error(err);
          });
        }
        if (data.old_password !== undefined) {
          data.old_password.forEach((err) => {
            $toast.error(err);
          });
        }
      }
    });
}
</script>
