<template>
  <v-container>
    <v-row class="text-center">
      <v-col class="mb-4" cols="12">
        <p>Logging out...</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";

import { useAuthStore } from "../stores/auth";

onMounted(() => {
  const { logout } = useAuthStore();
  logout();
});
</script>
