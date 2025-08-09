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
            <v-btn
              color="primary"
              :disabled="!isFormValid || loginOperation.isLoading.value"
              :loading="loginOperation.isLoading.value"
              @click="onSubmit"
            >
              Login
            </v-btn>
          </div>

          <!-- Loading indicator for retry attempts -->
          <LoadingIndicator
            v-if="loginOperation.isRetrying.value"
            :show="true"
            variant="inline"
            size="small"
            message="Retrying login..."
            :retry-count="loginOperation.retryCount.value"
          />
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

import LoadingIndicator from "../components/LoadingIndicator.vue";
import { useFormValidation } from "../composables/formValidation";
import { useAsyncOperation } from "../composables/useAsyncOperation";
import { rulesHelper } from "../helpers";
import { useAuthStore } from "../stores/auth";

const rules = rulesHelper;

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const isFormValid = ref(false);

const { user } = useAuthStore();
const isLoggedIn = user.isLoggedIn;

const { form, isValid } = useFormValidation();

// Use async operation for login with proper error handling
const loginOperation = useAsyncOperation({
  context: "User Login",
  errorHandler: "authentication",
  showLoading: true,
  successMessage: "Welcome back!",
  showSuccess: true,
});

async function onSubmit(): Promise<void> {
  if (!(await isValid())) {
    return;
  }

  const { login } = useAuthStore();

  await loginOperation.execute(async () => {
    await login(username.value, password.value);
  });
}
</script>
