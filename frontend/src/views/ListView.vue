<template>
  <v-container>
    <!-- Profile header (only show when viewing another user's profile) -->
    <ProfileHeaderComponent
      v-if="isProfileView"
      :username="username"
      :user-avatar-url="userAvatarUrl"
      :selected-list="selectedProfileList"
      @update:selected-list="selectedProfileList = $event"
    />

    <!-- List selector for regular users (when not viewing profile) -->
    <UserListSelectorComponent
      v-if="!isProfileView"
      :selected-list="selectedUserList"
      @update:selected-list="selectedUserList = $event"
    />

    <!-- Controls Section -->
    <ListControlsComponent
      v-model:mode="mode"
      v-model:sort="sort"
      v-model:to-rewatch-filter="toRewatchFilter"
      v-model:hide-unreleased-movies="hideUnreleasedMovies"
      v-model:recent-releases-filter="recentReleasesFilter"
      :current-list-id="currentListId"
      :is-profile-view="isProfileView"
    />

    <!-- Search and Counts -->
    <SearchAndCountsComponent
      :query="query"
      :watched-count="watchedCount"
      :to-watch-count="toWatchCount"
      :filtered-count="sortedFilteredRecords.length"
      :are-records-loaded="areRecordsLoaded"
      :is-records-loading="isRecordsLoading"
      @update:query="setQuery"
    />

    <!-- Top Pagination -->
    <MovieListPaginationComponent
      :current-page="page"
      :total-pages="totalPages"
      :are-records-loaded="areRecordsLoaded"
      :is-records-loading="isRecordsLoading"
      @update:page="page = $event"
    />

    <!-- Loading state -->
    <LoadingStateComponent v-if="isRecordsLoading" />

    <!-- Content when not loading -->
    <v-row v-if="!isRecordsLoading">
      <v-col cols="12">
        <!-- Regular view modes (non-gallery) -->
        <div v-cloak v-if="mode != 'gallery'">
          <template v-for="(record, index) in paginatedRecords" :key="record.id">
            <MovieItemComponent
              :record="record"
              :record-index="index"
              :mode="mode"
              :current-list-id="currentListId"
              :is-profile-view="isProfileView"
              :is-sortable="isSortable"
              :is-logged-in="authStore.user.isLoggedIn"
              :my-records="myRecords"
              @remove="handleRemoveRecord"
              @add-to-my-list="handleAddToMyList"
              @add-to-list="addToList"
              @rating-changed="changeRating"
              @save-comment="saveComment"
              @show-comment-area="showCommentArea"
              @save-options="saveOptions"
              @update-comment="updateRecordComment"
            />
          </template>
        </div>

        <!-- Gallery view -->
        <GalleryViewComponent
          v-if="mode === 'gallery'"
          v-model:records="galleryRecords"
          :paginated-records="sort === 'custom' ? galleryRecords : paginatedRecords"
          :is-sortable="isSortable"
          :is-profile-view="isProfileView"
          @sort="handleSaveRecordsOrder"
          @move-to-top="handleMoveToTop"
          @move-to-bottom="handleMoveToBottom"
        />
      </v-col>
    </v-row>

    <!-- Bottom Pagination -->
    <MovieListPaginationComponent
      :current-page="page"
      :total-pages="totalPages"
      :are-records-loaded="areRecordsLoaded"
      :is-records-loading="isRecordsLoading"
      @update:page="page = $event"
    />
  </v-container>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, toRef, watch } from "vue";
import { useRouter } from "vue-router";
import Draggable from "vuedraggable";

import type { RecordType } from "../types";

// Import extracted components
import GalleryViewComponent from "../components/ListView/GalleryViewComponent.vue";
import ListControlsComponent from "../components/ListView/ListControlsComponent.vue";
import LoadingStateComponent from "../components/ListView/LoadingStateComponent.vue";
import MovieItemComponent from "../components/ListView/MovieItemComponent.vue";
import MovieListPaginationComponent from "../components/ListView/MovieListPaginationComponent.vue";
import ProfileHeaderComponent from "../components/ListView/ProfileHeaderComponent.vue";
import SearchAndCountsComponent from "../components/ListView/SearchAndCountsComponent.vue";
import UserListSelectorComponent from "../components/ListView/UserListSelectorComponent.vue";
// Import composables
import { useListNavigation } from "../composables/useListNavigation";
import { useMovieOperations } from "../composables/useMovieOperations";
import { useRecordFilters } from "../composables/useRecordFilters";
import { useRecordsData } from "../composables/useRecordsData";
import { useRecordSorting } from "../composables/useRecordSorting";
import { listToWatchId, listWatchedId } from "../const";
import { useAuthStore } from "../stores/auth";
import { useRecordsStore } from "../stores/records";

const props = defineProps<{
  listId: number;
  username?: string;
  isProfileView?: boolean;
}>();

const router = useRouter();

const recordsStore = useRecordsStore();
const authStore = useAuthStore();

const mode = ref("full");
const toRewatchFilter = ref(false);
const hideUnreleasedMovies = ref(false);
const recentReleasesFilter = ref(false);
const records = toRef(recordsStore, "records");
const areRecordsLoaded = toRef(recordsStore, "areLoaded");
const isRecordsLoading = toRef(recordsStore, "isLoading");

// Initialize composables
const recordsData = useRecordsData();
const { myRecords, userAvatarUrl, loadAllData, clearUserData } = recordsData;

const movieOperations = useMovieOperations();
const {
  addingToList,
  addToList,
  addToMyList,
  removeRecord,
  changeRating,
  saveOptions,
  saveComment,
  showCommentArea,
  updateRecordComment,
  saveRecordsOrder,
  moveToTop,
  moveToBottom,
} = movieOperations;

const listNavigation = useListNavigation(props.listId, props.isProfileView);
const { selectedProfileList, selectedUserList, currentListId, page, resetListSelections, initializeWatchers } =
  listNavigation;

// Initialize filtering and sorting composables
const filterComposable = useRecordFilters(records, currentListId, "");
const { query, setQuery } = filterComposable;
const sortingComposable = useRecordSorting(records, currentListId);
const { sort } = sortingComposable;

// Get filtered records using the composable
const filteredRecords = filterComposable.getFilteredRecords({
  toRewatchFilter,
  hideUnreleasedMovies,
  recentReleasesFilter,
});

// Simplified approach for custom sorting
const customSortableRecords = ref<RecordType[]>([]);

// Apply sorting to filtered records
const sortedFilteredRecords = computed(() => {
  if (!filteredRecords.value.length) {return [];}

  const recordsCopy = [...filteredRecords.value];

  switch (sort.value) {
    case "custom":
      return recordsCopy.sort((a, b) => a.order - b.order);
    case "releaseDate":
      return recordsCopy.sort((a, b) => b.movie.releaseDateTimestamp - a.movie.releaseDateTimestamp);
    case "rating":
      if (currentListId.value === listWatchedId) {
        return recordsCopy.sort((a, b) => b.rating - a.rating);
      } 
        return recordsCopy.sort((a, b) => b.movie.imdbRating - a.movie.imdbRating);
      
    default: // AdditionDate
      return recordsCopy.sort((a, b) => b.additionDate - a.additionDate);
  }
});

// Only populate custom sortable records when we actually need them for dragging
const initializeCustomSort = () => {
  if (sort.value === "custom" && customSortableRecords.value.length === 0) {
    const sortedRecords = [...filteredRecords.value].sort((a, b) => a.order - b.order);
    /* For performance, limit to first 50 items when dragging
       TODO: Implement proper pagination for custom sort later */
    customSortableRecords.value = sortedRecords.slice(0, 50);
  }
};

// Track if we're currently dragging to avoid expensive computations
const isDragging = ref(false);

// Simple reactive array for gallery drag operations
const galleryRecords = computed({
  get() {
    if (sort.value === "custom") {
      initializeCustomSort();
      return customSortableRecords.value;
    }
    return sortedFilteredRecords.value;
  },
  set(value) {
    if (sort.value === "custom") {
      isDragging.value = true;
      customSortableRecords.value = value;
      // Save after drag completes
      handleSaveRecordsOrder();
      isDragging.value = false;
    }
  },
});

// Get optimized count computations
const watchedCount = filterComposable.getWatchedCount();
const toWatchCount = filterComposable.getToWatchCount();

// Get pagination utilities
const perPage = 50;
const totalPages = computed(() => Math.ceil(sortedFilteredRecords.value.length / perPage));
const paginatedRecords = computed(() => {
  const start = (page.value - 1) * perPage;
  return sortedFilteredRecords.value.slice(start, start + perPage);
});

// Watch for query changes and update the composable
watch(query, (newQuery) => {
  setQuery(newQuery);
});

const listIdRef = toRef(props, "listId");
const usernameRef = toRef(props, "username");
const isProfileViewRef = toRef(props, "isProfileView");

// Wrapper function to load all data using the composable
async function loadData(): Promise<void> {
  await loadAllData(props.isProfileView, props.username, authStore.user.isLoggedIn);
}

// Wrapper functions for movie operations to maintain component interface
const handleAddToMyList = (movieId: number, listId: number) => {
  addToMyList(movieId, listId, records.value, myRecords.value, authStore.user.isLoggedIn);
};

const handleRemoveRecord = (record: RecordType) => {
  removeRecord(record, records.value);
};

const handleMoveToTop = (record: RecordType) => {
  moveToTop(record, records.value);
};

const handleMoveToBottom = (record: RecordType) => {
  moveToBottom(record, records.value);
};

let saveTimeout: number | null = null;

const handleSaveRecordsOrder = () => {
  // Prevent duplicate saves with debouncing
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }

  saveTimeout = setTimeout(() => {
    if (sort.value === "custom" && customSortableRecords.value.length > 0) {
      // Get all records for the current list, ordered by existing order
      const allCurrentListRecords = records.value
        .filter((r) => r.listId === currentListId.value)
        .sort((a, b) => a.order - b.order);

      // Update orders for the dragged items first
      customSortableRecords.value.forEach((sortedRecord, index) => {
        const originalRecord = allCurrentListRecords.find((r) => r.id === sortedRecord.id);
        if (originalRecord) {
          originalRecord.order = index + 1;
        }
      });

      // For items not in the dragged set, keep their relative positions after the dragged items
      const draggedIds = new Set(customSortableRecords.value.map((r) => r.id));
      const notDraggedRecords = allCurrentListRecords.filter((r) => !draggedIds.has(r.id));

      // Start numbering after the dragged items
      let nextOrder = customSortableRecords.value.length + 1;
      notDraggedRecords.forEach((record) => {
        record.order = nextOrder++;
      });

      saveRecordsOrder(allCurrentListRecords);
    }
    saveTimeout = null;
  }, 200); // Debounce saves to prevent multiple API calls
};

// Watch for changes in props that require reloading data
watch([listIdRef, usernameRef, isProfileViewRef], async () => {
  resetListSelections(props.listId);
  await loadData();
});

// Initialize list navigation watchers
initializeWatchers(props.username, loadData);

// Watch for login status changes
watch(
  () => authStore.user.isLoggedIn,
  async (isLoggedIn) => {
    if (isLoggedIn && props.isProfileView) {
      await recordsData.loadMyRecords(props.isProfileView, isLoggedIn);
    } else if (!isLoggedIn) {
      clearUserData();
    }
  },
);

// Computed properties
const isSortable = computed(() => {
  return (
    currentListId.value === listToWatchId &&
    sort.value === "custom" &&
    (mode.value === "minimal" || mode.value === "gallery") &&
    !props.isProfileView // Disable sorting for profile views
  );
});

onMounted(async () => {
  await loadData();
});
</script>

<style scoped>
/* Only minimal styles remain - most styles moved to individual components */
</style>
