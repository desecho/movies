<template>
  <v-select
    v-model="selectedYear"
    :items="yearOptions"
    item-title="label"
    item-value="value"
    label="Year"
    variant="outlined"
    density="compact"
    prepend-inner-icon="mdi-calendar"
    hide-details
    class="year-selector"
    @update:model-value="handleYearChange"
  >
    <template #selection="{ item }">
      <span class="year-selection">{{ item.title }}</span>
    </template>
  </v-select>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from "vue";

interface YearOption {
  label: string;
  value: number | null;
}

interface Props {
  availableYears: number[];
  currentYear?: number | null;
}

interface Emits {
  (e: "year-changed", year: number | null): void;
}

const props = withDefaults(defineProps<Props>(), {
  currentYear: null,
});

const emit = defineEmits<Emits>();

const selectedYear = ref<number | null>(props.currentYear);

const yearOptions = computed<YearOption[]>(() => {
  const options: YearOption[] = [{ label: "All Time", value: null }];

  // Add available years
  props.availableYears.forEach((year) => {
    options.push({
      label: year.toString(),
      value: year,
    });
  });

  return options;
});

function handleYearChange(year: number | null): void {
  selectedYear.value = year;
  emit("year-changed", year);
}

// Watch for external changes to currentYear prop
watch(
  () => props.currentYear,
  (newYear) => {
    if (selectedYear.value !== newYear) {
      selectedYear.value = newYear;
    }
  },
);
</script>

<style scoped>
.year-selector {
  max-width: 200px;
}

.year-selection {
  font-weight: 500;
}

:deep(.v-field__input) {
  font-weight: 500;
}

:deep(.v-field__prepend-inner) {
  .v-icon {
    opacity: 0.7;
  }
}
</style>
