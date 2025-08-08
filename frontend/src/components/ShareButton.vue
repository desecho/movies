<template>
  <button
    type="button"
    class="btn btn-secondary share-button"
    :class="{ disabled: isSharing || !canShare }"
    :disabled="isSharing || !canShare"
    title="Share on X"
    @click="handleShare"
  >
    <v-icon v-if="isSharing" icon="mdi-loading" class="rotating-icon" />
    <v-icon v-else icon="mdi-share-variant" />
  </button>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { RecordType } from "../types";

import { useSocialSharing } from "../composables/useSocialSharing";
import { listWatchedId } from "../const";

interface Props {
  record: RecordType;
}

const props = defineProps<Props>();

const { isSharing, shareToX } = useSocialSharing();

// Can only share watched movies with ratings or comments
const canShare = computed(() => {
  return props.record.listId === listWatchedId && (props.record.rating > 0 || props.record.comment.trim().length > 0);
});

async function handleShare(): Promise<void> {
  if (canShare.value) {
    await shareToX(props.record.id);
  }
}
</script>

<style scoped>
.share-button {
  min-width: auto !important;
  transition: all 0.2s ease;
}

.share-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.share-button.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.rotating-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
