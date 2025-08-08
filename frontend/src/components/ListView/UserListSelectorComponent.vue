<template>
  <v-row>
    <v-col cols="12">
      <div class="user-list-selector">
        <div class="control-group">
          <label class="control-label">List</label>
          <v-btn-toggle 
            :model-value="selectedList" 
            density="compact" 
            mandatory 
            class="user-list-btn-toggle"
            @update:model-value="$emit('update:selectedList', $event)"
          >
            <v-btn :value="listWatchedId" :size="modeButtonSize"> Watched </v-btn>
            <v-btn :value="listToWatchId" :size="modeButtonSize"> To Watch </v-btn>
          </v-btn-toggle>
        </div>
      </div>
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useMobile } from "../../composables/mobile";
import { listToWatchId, listWatchedId } from "../../const";

interface Props {
  selectedList: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:selectedList": [listId: number];
}>();

const { isMobile } = useMobile();

const modeButtonSize = computed(() => {
  if (isMobile.value) {
    return "small";
  }
  return "default";
});
</script>

<style scoped>
/* User list selector styling for regular users */
.user-list-selector {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: center;
}

.user-list-selector .control-group {
  align-items: center;
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

.dark-theme {
  .user-list-selector {
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
  }
}

.dark-theme .v-btn-toggle {
  background: rgba(31, 41, 55, 0.9);
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .user-list-selector {
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
    }
  }
}

@media (max-width: 480px) {
  .user-list-selector {
    padding: 12px;
    margin-bottom: 16px;
  }

  .control-label {
    font-size: 0.75rem;
  }
}
</style>