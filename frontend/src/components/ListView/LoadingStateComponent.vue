<template>
  <v-row>
    <v-col cols="12" class="text-center">
      <div class="loading-container">
        <v-progress-circular :size="60" :width="4" color="primary" indeterminate></v-progress-circular>
        <div class="loading-text">Loading movies...</div>
      </div>
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
// No props needed for this simple loading component
</script>

<style scoped>
/* Loading State Styling */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 24px;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
  color: #6b7280;
  text-align: center;
}
</style>