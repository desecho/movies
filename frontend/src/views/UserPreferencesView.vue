<template>
  <v-container>
    <v-row>
      <v-col v-cloak cols="12">
        <!-- <v-form
                    ref="form"
                    v-model="isFormValid"
                    lazy-validation
                    @submit.prevent="savePreferences"
                >
                    <v-text-field
                        v-model="username"
                        label="Username"
                        variant="solo"
                        :hide-details="true"
                        :rules="[rules.required]"
                        class="mr-5"
                    ></v-text-field>
                </v-form> -->

        <v-checkbox v-model="hidden" label="Hide profile" hide-details @change="savePreferences()"></v-checkbox>
        <span class="profile-label">Profile link: </span>
        <router-link :to="profileLink" class="profile-link">{{ absoluteProfileLink }}</router-link>
        <br /><br />
        <router-link to="/change-password" class="change-password-link">Change password</router-link>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";

import type { GetUserPreferencesData } from "./types";
import type { AxiosError } from "axios";

import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";

const url = getUrl("user/preferences/");

const hidden = ref(false);

const profileLink = computed(() => {
  const { user } = useAuthStore();
  // `username` is always not null when user is logged in
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  return `/users/${user.username!}/list/watched/`;
});
const absoluteProfileLink = computed(() => {
  return `${location.origin}${profileLink.value}`;
});

function loadPreferences(): void {
  axios
    .get(url)
    .then((response) => {
      const data = response.data as GetUserPreferencesData;
      hidden.value = data.hidden;
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error loading preferences");
    });
}
function savePreferences(): void {
  axios.put(url, { hidden: hidden.value }).catch((error: AxiosError) => {
    console.log(error);
    $toast.error("Error saving preferences");
  });
}
onMounted(() => {
  loadPreferences();
});
</script>

<style scoped>
.profile-label {
  color: var(--text-primary);
  font-weight: 500;
}

.profile-link,
.change-password-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.profile-link:hover,
.change-password-link:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

/* Dark theme specific styles */
:global(.dark-theme) .profile-label {
  color: var(--text-primary);
}

:global(.dark-theme) .profile-link,
:global(.dark-theme) .change-password-link {
  color: #93c5fd;
}

:global(.dark-theme) .profile-link:hover,
:global(.dark-theme) .change-password-link:hover {
  color: #bfdbfe;
}
</style>
