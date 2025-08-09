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

        <!-- Location Settings -->
        <v-card class="elevation-2 mb-6">
          <v-card-title class="text-h6">Location Settings</v-card-title>
          <v-card-text>
            <v-select
              v-model="country"
              :items="countryOptions"
              item-title="name"
              item-value="code"
              label="Country"
              placeholder="Select your country"
              clearable
              @update:model-value="onCountryChange"
            >
              <template #selection="{ item }">
                <span class="d-flex align-center">
                  <span v-if="item.raw.code" class="fi fi-{{ item.raw.code.toLowerCase() }} mr-2"></span>
                  {{ item.raw.name }}
                </span>
              </template>
              <template #item="{ props, item }">
                <v-list-item v-bind="props" :title="item.raw.name">
                  <template #prepend>
                    <span v-if="item.raw.code" class="fi fi-{{ item.raw.code.toLowerCase() }} mr-2"></span>
                  </template>
                </v-list-item>
              </template>
            </v-select>
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
import { parseString } from "../types/common";

const url = getUrl("user/preferences/");

const hidden = ref(false);
const country = ref<string>("");

// Country options for the dropdown
const countryOptions = ref([
  { code: "CA", name: "Canada" },
  { code: "US", name: "United States" },
]);

const profileLink = computed(() => {
  const { user } = useAuthStore();
  const username = parseString(user.username, "unknown");
  return `/users/${username}/list/watched/`;
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
      country.value = data.country || "";
    })
    .catch((error: AxiosError) => {
      console.log(error);
      $toast.error("Error loading preferences");
    });
}
function savePreferences(): void {
  axios.put(url, { hidden: hidden.value, country: country.value || null }).catch((error: AxiosError) => {
    console.log(error);
    $toast.error("Error saving preferences");
  });
}

function onCountryChange(selectedCountryCode: string | null): void {
  country.value = selectedCountryCode || "";
  savePreferences();
}
onMounted(() => {
  loadPreferences();
});
</script>

<style scoped>
/* Clean, simple styling - let Vuetify handle the rest */
</style>
