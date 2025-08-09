<template>
  <ErrorBoundary context="User Preferences" fallback-message="Unable to load user preferences">
    <v-container>
      <v-row>
        <v-col cols="12" md="8" lg="6" class="mx-auto">
          <h1 class="text-h4 mb-6">User Preferences</h1>

          <!-- Loading indicator for initial load -->
          <LoadingIndicator
            v-if="loadPreferencesOperation.isLoading.value"
            :show="true"
            variant="overlay"
            message="Loading your preferences..."
          />

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
                :disabled="savePreferencesOperation.isLoading.value"
                @change="savePreferences()"
              ></v-checkbox>

              <!-- Saving indicator -->
              <LoadingIndicator
                v-if="savePreferencesOperation.isLoading.value"
                :show="true"
                variant="inline"
                size="small"
                message="Saving..."
                class="mt-2"
              />
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
                :disabled="savePreferencesOperation.isLoading.value"
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
  </ErrorBoundary>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, onMounted, ref } from "vue";

import type { GetUserPreferencesData } from "./types";

import AvatarUploadComponent from "../components/AvatarUploadComponent.vue";
import ErrorBoundary from "../components/ErrorBoundary.vue";
import LoadingIndicator from "../components/LoadingIndicator.vue";
import { useApiCall } from "../composables/useAsyncOperation";
import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { $toast } from "../toast";
import { parseString } from "../types/common";

const url = getUrl("user/preferences/");

const hidden = ref(false);
const country = ref<string>("");

// Error handling composables
const loadPreferencesOperation = useApiCall("Load User Preferences");
const savePreferencesOperation = useApiCall("Save User Preferences");

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

async function loadPreferences(): Promise<void> {
  const result = await loadPreferencesOperation.execute(async () => {
    const response = await axios.get(url);
    return response.data as GetUserPreferencesData;
  });

  if (result.success && result.data) {
    hidden.value = result.data.hidden;
    country.value = result.data.country || "";
  }
}

async function savePreferences(): Promise<void> {
  const result = await savePreferencesOperation.execute(async () => {
    const response = await axios.put(url, {
      hidden: hidden.value,
      country: country.value || null,
    });
    return response.data as Record<string, unknown>;
  });

  if (result.success) {
    $toast.success("Preferences saved successfully!");
  }
}

function onCountryChange(selectedCountryCode: string | null): void {
  country.value = selectedCountryCode || "";
  void savePreferences();
}

onMounted(() => {
  void loadPreferences();
});
</script>

<style scoped>
/* Clean, simple styling - let Vuetify handle the rest */
</style>
