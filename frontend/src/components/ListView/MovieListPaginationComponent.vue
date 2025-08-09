<template>
  <v-row v-if="areRecordsLoaded && !isRecordsLoading">
    <v-col cols="10">
      <v-pagination 
        :model-value="currentPage" 
        :pages="totalPages" 
        :range-size="1" 
        :active-color="paginationActiveColor"
        @update:model-value="$emit('update:page', $event)" 
      />
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
import VPagination from "@hennge/vue3-pagination";
import { computed } from "vue";

import { useThemeStore } from "../../stores/theme";

interface Props {
  currentPage: number;
  totalPages: number;
  areRecordsLoaded: boolean;
  isRecordsLoading: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:page": [page: number];
}>();

const themeStore = useThemeStore();

const paginationActiveColor = computed(() => {
  return themeStore.isDark ? "#667eea" : "#DCEDFF";
});
</script>

<style src="@hennge/vue3-pagination/dist/vue3-pagination.css"></style>