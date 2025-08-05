<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8" lg="6" class="mx-auto">
        <h1 class="text-h4 mb-6">User Preferences</h1>

        <!-- Avatar Upload Section -->
        <div class="mb-8">
          <AvatarUploadComponent />
        </div>

        <!-- Privacy Settings -->
        <v-card class="elevation-2 mb-6">
          <v-card-title class="text-h6">Privacy Settings</v-card-title>
          <v-card-text>
            <v-checkbox
              v-model="hidden"
              label="Hide profile from other users"
              hide-details
              @change="savePreferences()"
            ></v-checkbox>
            <div class="mt-4">
              <div class="text-body-2 text-medium-emphasis mb-1">Your profile link:</div>
              <router-link :to="profileLink" class="profile-link text-primary">
                {{ absoluteProfileLink }}
              </router-link>
            </div>
          </v-card-text>
        </v-card>

        <!-- Account Settings -->
        <v-card class="elevation-2">
          <v-card-title class="text-h6">Account Settings</v-card-title>
          <v-card-text>
            <v-btn color="primary" variant="outlined" :to="'/change-password'" prepend-icon="mdi-lock">
              Change Password
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";

import type { GetUserPreferencesData } from "./types";
import type { AxiosError } from "axios";

import AvatarUploadComponent from "../components/AvatarUploadComponent.vue";
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
