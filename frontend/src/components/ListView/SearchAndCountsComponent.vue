<template>
  <v-row>
    <v-col cols="6">
      <v-text-field
        :model-value="query"
        label="Search"
        variant="solo"
        :hide-details="true"
        class="mr-5"
        density="compact"
        title="You can search by movie title, director, or actor"
        @update:model-value="$emit('update:query', $event)"
      ></v-text-field>
    </v-col>
    <v-col cols="1"></v-col>
    <v-col v-if="areRecordsLoaded && !isRecordsLoading" cols="5">
      <div class="watch-count-container">
        <div class="watch-count-item watched">
          <div class="count-icon-wrapper watched-icon">
            <v-icon icon="mdi-eye" />
          </div>
          <div class="count-info">
            <span class="count-number">{{ watchedCount }}</span>
            <span class="count-label">Watched</span>
          </div>
        </div>
        <div class="watch-count-item to-watch">
          <div class="count-icon-wrapper to-watch-icon">
            <v-icon icon="mdi-eye-off" />
          </div>
          <div class="count-info">
            <span class="count-number">{{ toWatchCount }}</span>
            <span class="count-label">To Watch</span>
          </div>
        </div>
        <div class="watch-count-item filtered">
          <div class="count-icon-wrapper filtered-icon">
            <v-icon icon="mdi-filter" />
          </div>
          <div class="count-info">
            <span class="count-number">{{ filteredCount }}</span>
            <span class="count-label">Displayed</span>
          </div>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
interface Props {
  query: string;
  watchedCount: number;
  toWatchCount: number;
  filteredCount: number;
  areRecordsLoaded: boolean;
  isRecordsLoading: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:query": [query: string];
}>();
</script>

<style scoped>
/* Watch Count Component Styling */
.watch-count-container {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
}

.watch-count-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  min-width: 120px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.95);
  }

  &.watched {
    border-left: 3px solid #22c55e;
  }

  &.to-watch {
    border-left: 3px solid #3b82f6;
  }

  &.filtered {
    border-left: 3px solid #8b5cf6;
  }
}

.count-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;

  .v-icon {
    font-size: 1.4rem;
    color: white;
  }

  &.watched-icon {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
  }

  &.to-watch-icon {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }

  &.filtered-icon {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
  }
}

.count-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.count-number {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.count-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.watch-count-item:hover .count-icon-wrapper {
  transform: scale(1.05);
}

.watch-count-item.watched:hover .count-icon-wrapper.watched-icon {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
}

.watch-count-item.to-watch:hover .count-icon-wrapper.to-watch-icon {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.watch-count-item.filtered:hover .count-icon-wrapper.filtered-icon {
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

/* Responsive Design for Watch Count */
@media (max-width: 768px) {
  .watch-count-container {
    gap: 12px;
    justify-content: center;
  }

  .watch-count-item {
    padding: 10px 12px;
    min-width: 100px;
    gap: 10px;
  }

  .count-icon-wrapper {
    width: 35px;
    height: 35px;

    .v-icon {
      font-size: 1.2rem;
    }
  }

  .count-number {
    font-size: 1.2rem;
  }

  .count-label {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .watch-count-container {
    gap: 8px;
    flex-direction: column;
    align-items: stretch;
  }

  .watch-count-item {
    padding: 8px 12px;
    min-width: auto;
    justify-content: center;
  }

  .count-icon-wrapper {
    width: 32px;
    height: 32px;

    .v-icon {
      font-size: 1.1rem;
    }
  }

  .count-number {
    font-size: 1.1rem;
  }

  .count-label {
    font-size: 0.65rem;
  }
}
</style>
