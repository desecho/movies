<template>
  <div class="controls-section">
    <v-row>
      <v-col cols="12" md="6">
        <div class="control-group">
          <label class="control-label">View Mode</label>
          <v-btn-toggle 
            :model-value="mode" 
            density="compact" 
            mandatory
            @update:model-value="$emit('update:mode', $event)"
          >
            <v-btn value="full" :size="modeButtonSize">Full</v-btn>
            <v-btn value="compact" :size="modeButtonSize">Compact</v-btn>
            <v-btn value="minimal" :size="modeButtonSize">Minimal</v-btn>
            <v-btn value="gallery" :size="modeButtonSize">Gallery</v-btn>
          </v-btn-toggle>
        </div>
      </v-col>
      <v-col cols="12" md="6">
        <div class="control-group">
          <label class="control-label">Sort By</label>
          <v-btn-toggle 
            :model-value="sort" 
            density="compact" 
            mandatory
            @update:model-value="$emit('update:sort', $event)"
          >
            <v-btn value="releaseDate" :size="sortButtonSize">Release date</v-btn>
            <v-btn value="rating" :size="sortButtonSize">Rating</v-btn>
            <v-btn value="additionDate" :size="sortButtonSize">Date added</v-btn>
            <v-btn v-if="currentListId == listToWatchId && !isProfileView" value="custom" :size="sortButtonSize">
              Custom
            </v-btn>
          </v-btn-toggle>
        </div>
      </v-col>
    </v-row>
    <!-- Filter Controls -->
    <v-row v-if="!isProfileView && (currentListId === listWatchedId || currentListId === listToWatchId)">
      <!-- To Rewatch filter (only for watched movies) -->
      <v-col v-if="currentListId === listWatchedId" cols="12" md="6">
        <div class="control-group">
          <label class="control-label">Filter</label>
          <v-btn-toggle 
            :model-value="toRewatchFilter" 
            density="compact"
            @update:model-value="$emit('update:toRewatchFilter', $event ?? false)"
          >
            <v-btn :value="true" :size="modeButtonSize">To Rewatch</v-btn>
          </v-btn-toggle>
        </div>
      </v-col>
      <!-- Filters (only for to-watch movies) -->
      <v-col v-if="currentListId === listToWatchId" cols="12" md="6">
        <div class="control-group">
          <label class="control-label">Filter</label>
          <div style="display: flex; gap: 8px">
            <v-btn-toggle 
              :model-value="hideUnreleasedMovies" 
              density="compact"
              @update:model-value="$emit('update:hideUnreleasedMovies', $event ?? false)"
            >
              <v-btn :value="true" :size="modeButtonSize">Hide Unreleased</v-btn>
            </v-btn-toggle>
            <v-btn-toggle 
              :model-value="recentReleasesFilter" 
              density="compact"
              @update:model-value="$emit('update:recentReleasesFilter', $event ?? false)"
            >
              <v-btn :value="true" :size="modeButtonSize">Recent Releases</v-btn>
            </v-btn-toggle>
          </div>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useMobile } from "../../composables/mobile";
import { listToWatchId, listWatchedId } from "../../const";

interface Props {
  mode: string;
  sort: string;
  currentListId: number;
  isProfileView: boolean;
  toRewatchFilter: boolean;
  hideUnreleasedMovies: boolean;
  recentReleasesFilter: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:mode": [mode: string];
  "update:sort": [sort: string];
  "update:toRewatchFilter": [filter: boolean];
  "update:hideUnreleasedMovies": [filter: boolean];
  "update:recentReleasesFilter": [filter: boolean];
}>();

const { isMobile } = useMobile();

const modeButtonSize = computed(() => {
  if (isMobile.value) {
    return "small";
  }
  return "default";
});

const sortButtonSize = computed(() => {
  if (isMobile.value) {
    return "x-small";
  }
  return "default";
});
</script>

<style scoped>
/* Controls section styling */
.controls-section {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

/* Dark theme control labels */
.dark-theme .control-label {
  color: var(--text-primary) !important;
}

.dark-theme .v-btn-toggle {
  background: rgba(31, 41, 55, 0.9);
}

.dark-theme {
  .controls-section {
    background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
    border: 1px solid #475569 !important;
  }
}

/* Enhanced button toggle styling */
:deep(.v-btn-toggle) {
  border-radius: 12px !important;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);

  .v-btn {
    border-radius: 8px !important;
    text-transform: none !important;
    font-weight: 500 !important;
    margin: 2px !important;
    transition: all 0.2s ease !important;
    color: #6c757d !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    &:hover {
      background: rgba(102, 126, 234, 0.1) !important;
      color: #667eea !important;
      transform: translateY(-1px);
    }

    &.v-btn--active {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      color: white !important;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }

    &.v-btn--size-small {
      font-size: 0.875rem !important;
      padding: 8px 12px !important;
    }

    &.v-btn--size-x-small {
      font-size: 0.75rem !important;
      padding: 6px 10px !important;
    }
  }
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .controls-section {
    padding: 16px;
    margin-bottom: 20px;
  }

  .control-group {
    gap: 6px;
  }

  .control-label {
    font-size: 0.8rem;
  }

  :deep(.v-btn-toggle) {
    padding: 2px;

    .v-btn {
      margin: 1px !important;
      font-size: 0.8rem !important;
      padding: 6px 8px !important;

      &.v-btn--size-small {
        font-size: 0.75rem !important;
        padding: 6px 8px !important;
      }

      &.v-btn--size-x-small {
        font-size: 0.7rem !important;
        padding: 4px 6px !important;
      }
    }
  }
}

@media (max-width: 480px) {
  .controls-section {
    padding: 12px;
    margin-bottom: 16px;
  }

  .control-label {
    font-size: 0.75rem;
  }
}
</style>