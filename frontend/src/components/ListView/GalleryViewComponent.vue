<template>
  <div v-cloak id="gallery">
    <draggable 
      :model-value="records" 
      item-key="id" 
      :disabled="!isSortable" 
      @update:model-value="$emit('update:records', $event)"
      @sort="$emit('sort')"
    >
      <template #item="{ element, index }">
        <div v-if="paginatedRecords.includes(element)" class="gallery-record">
          <!-- Only show move buttons for own lists -->
          <div v-if="!isProfileView" class="buttons">
            <button
              v-show="isSortable"
              type="button"
              class="up-button"
              title="Move to the top"
              @click="$emit('move-to-top', element, index)"
            >
              <v-icon icon="mdi-arrow-up" />
            </button>
            <button
              v-show="isSortable"
              type="button"
              class="down-button"
              title="Move to the bottom"
              @click="$emit('move-to-bottom', element, index)"
            >
              <v-icon icon="mdi-arrow-down" />
            </button>
          </div>
          <v-lazy-image
            class="poster-big"
            :class="{ draggable: isSortable }"
            :srcset="getSrcSet(element.movie.posterNormal, element.movie.posterBig)"
            :src="element.movie.posterBig"
            :title="element.movie.title"
            :alt="element.movie.title"
          />
        </div>
      </template>
    </draggable>
  </div>
</template>

<script lang="ts" setup>
import VLazyImage from "v-lazy-image";
import Draggable from "vuedraggable";
import type { RecordType } from "../../types";
import { getSrcSet } from "../../helpers";

interface Props {
  records: RecordType[];
  paginatedRecords: RecordType[];
  isSortable: boolean;
  isProfileView: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  "update:records": [records: RecordType[]];
  "sort": [];
  "move-to-top": [record: RecordType, index: number];
  "move-to-bottom": [record: RecordType, index: number];
}>();
</script>

<style scoped>
#gallery {
  margin: 0;
  padding: 12px;

  .gallery-record {
    display: inline-block;
    position: relative;
    margin: 8px;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;

    img {
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      transition: all 0.3s ease;

      &.draggable {
        cursor: grab;

        &:active {
          cursor: grabbing;
          transform: rotate(2deg);
        }
      }
    }

    button {
      opacity: 0;
      position: absolute;
      right: 12px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(0, 0, 0, 0.1);
      border-radius: 8px;
      padding: 8px;
      transition: all 0.2s ease;
      cursor: pointer;

      &:hover {
        background: white;
        transform: scale(1.05);
      }

      .v-icon {
        color: #667eea;
        font-size: 18px;
      }
    }

    .up-button {
      bottom: 70px;
    }

    .down-button {
      bottom: 25px;
    }

    &:hover {
      transform: translateY(-4px);

      img {
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);
        transform: scale(1.02);
      }

      button {
        opacity: 1;
      }
    }

    @media (max-width: 768px) {
      button {
        opacity: 1;
        background: rgba(255, 255, 255, 0.9);
      }
    }

    @media (min-width: 320px) and (max-width: 576px) {
      .poster-big {
        width: 92px;
      }

      .up-button {
        bottom: 50px;
      }

      .down-button {
        bottom: 15px;
      }

      button {
        padding: 6px;
        right: 8px;

        .v-icon {
          font-size: 16px;
        }
      }
    }
  }
}

.poster-big {
  width: 185px;
}
</style>