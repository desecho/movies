<template>
  <ErrorBoundary context="Movie List View" fallback-message="Unable to load your movie list">
    <v-container>
      <!-- Profile header (only show when viewing another user's profile) -->
      <ProfileHeaderComponent
        v-if="isProfileView && username"
        :username="username || ''"
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
        v-model:mode="modeComputed"
        v-model:sort="sortComputed"
        v-model:to-rewatch-filter="toRewatchFilter"
        v-model:hide-unreleased-movies="hideUnreleasedMovies"
        v-model:recent-releases-filter="recentReleasesFilter"
        :current-list-id="currentListId"
        :is-profile-view="!!isProfileView"
      />

      <!-- Search and Counts -->
      <SearchAndCountsComponent
        :query="query"
        :watched-count="watchedCount"
        :to-watch-count="toWatchCount"
        :filtered-count="filteredCount"
        :are-records-loaded="areRecordsLoaded"
        :is-records-loading="isRecordsLoading"
        @update:query="handleQueryUpdate"
      />

      <!-- Top Pagination -->
      <MovieListPaginationComponent
        :current-page="page"
        :total-pages="totalPages"
        :are-records-loaded="areRecordsLoaded"
        :is-records-loading="isRecordsLoading"
        @update:page="setStorePage"
      />

      <!-- Loading state -->
      <LoadingStateComponent v-if="isRecordsLoading" />

      <v-row v-else>
        <v-col cols="12">
          <!-- Regular view modes (non-gallery) -->
          <div v-cloak v-if="modeComputed !== 'gallery'">
            <template v-for="(record, index) in paginatedRecords" :key="record.id">
              <MovieItemComponent
                :record="record"
                :record-index="index"
                :mode="modeComputed"
                :current-list-id="currentListId"
                :is-profile-view="!!isProfileView"
                :is-sortable="isSortable"
                :is-logged-in="isLoggedIn"
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
            v-if="modeComputed === 'gallery'"
            v-model:records="galleryRecords"
            :paginated-records="sortComputed === 'custom' ? galleryRecords : paginatedRecords"
            :is-sortable="isSortable"
            :is-profile-view="!!isProfileView"
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
        @update:page="setStorePage"
      />
    </v-container>
  </ErrorBoundary>
</template>

<script lang="ts" setup>
import { storeToRefs } from "pinia";
import { computed, defineAsyncComponent, onMounted, onUnmounted, ref, shallowRef, toRef, watch } from "vue";

import type { RecordType } from "../types";
import type { SortType, ViewMode } from "../types/listView";

import ErrorBoundary from "../components/ErrorBoundary.vue";
import ListControlsComponent from "../components/ListView/ListControlsComponent.vue";
import LoadingStateComponent from "../components/ListView/LoadingStateComponent.vue";
import MovieListPaginationComponent from "../components/ListView/MovieListPaginationComponent.vue";
import ProfileHeaderComponent from "../components/ListView/ProfileHeaderComponent.vue";
import SearchAndCountsComponent from "../components/ListView/SearchAndCountsComponent.vue";
import UserListSelectorComponent from "../components/ListView/UserListSelectorComponent.vue";
// Import composables
import { useListNavigation } from "../composables/useListNavigation";
import { useListViewFiltering } from "../composables/useListViewFiltering";
import { useListViewPagination } from "../composables/useListViewPagination";
import { useListViewSorting } from "../composables/useListViewSorting";
import { useMovieOperations } from "../composables/useMovieOperations";
import { useRecordCounts } from "../composables/useRecordCounts";
import { useRecordsData } from "../composables/useRecordsData";
import { listToWatchId } from "../const";
import { useAuthStore } from "../stores/auth";
import { useListViewStore } from "../stores/listView";
import { useRecordsStore } from "../stores/records";

// Import extracted components
const GalleryViewComponent = defineAsyncComponent(
  async () => import("../components/ListView/GalleryViewComponent.vue"),
);

const MovieItemComponent = defineAsyncComponent(async () => import("../components/ListView/MovieItemComponent.vue"));

/**
 * Props for ListView component
 */
interface ListViewProps {
  /** ID of the list to display (1 for watched, 2 for to-watch) */
  listId: number;
  /** Username for profile view (optional, for viewing other user's lists) */
  username?: string;
  /** Whether this is a profile view (viewing another user's lists) */
  isProfileView?: boolean;
}

const props = defineProps<ListViewProps>();

const recordsStore = useRecordsStore();
const authStore = useAuthStore();
const listViewStore = useListViewStore();

const records = toRef(recordsStore, "records");
const areRecordsLoaded = toRef(recordsStore, "areLoaded");
const isRecordsLoading = toRef(recordsStore, "isLoading");

// Initialize ListView state from store
const { mode, sort: storeSort, query: storeQuery, filters, page: storePage } = storeToRefs(listViewStore);

const {
  setMode,
  setSort: setStoreSort,
  setQuery: setStoreQuery,
  setFilter,
  setPage: setStorePage,
  loadPersistedState,
} = listViewStore;

// Initialize composables
const recordsData = useRecordsData();
const { myRecords, userAvatarUrl, loadAllData, clearUserData } = recordsData;

const movieOperations = useMovieOperations();
const {
  addToList,
  addToMyList,
  removeRecord,
  changeRating,
  saveOptions,
  saveComment,
  showCommentArea,
  updateRecordComment,
  saveRecordsOrder,
} = movieOperations;

const listNavigation = useListNavigation(props.listId, props.isProfileView);
const { selectedProfileList, selectedUserList, currentListId, resetListSelections, initializeWatchers } =
  listNavigation;

// Use store values for query and sort, with page from navigation
const query = storeQuery;
const page = storePage;

// Centralized auth state
const isLoggedIn = computed(() => authStore.user?.isLoggedIn ?? false);

/**
 * Writable computed for view mode that integrates with the ListView store.
 * Provides two-way binding for v-model directives.
 */
const modeComputed = computed({
  get: () => {
    return mode.value || "full";
  },
  set: (value: ViewMode) => {
    setMode(value);
  },
});

/**
 * Writable computed for sort type that integrates with the ListView store.
 * Provides two-way binding for v-model directives.
 */
const sortComputed = computed({
  get: () => {
    return storeSort.value || "additionDate";
  },
  set: (value: SortType) => {
    setStoreSort(value);
  },
});

/**
 * Writable computed properties for filter bindings with the ListView store.
 * These provide two-way binding for various filter controls.
 */

/** Filter for showing only movies marked for rewatching (watched list only) */
const toRewatchFilter = computed({
  get: () => filters.value?.toRewatch ?? false,
  set: (value: boolean) => {
    setFilter("toRewatch", value);
  },
});

/** Filter for hiding unreleased movies (to-watch list only) */
const hideUnreleasedMovies = computed({
  get: () => filters.value?.hideUnreleased ?? false,
  set: (value: boolean) => {
    setFilter("hideUnreleased", value);
  },
});

/** Filter for showing only recent releases from last 6 months (to-watch list only) */
const recentReleasesFilter = computed({
  get: () => filters.value?.recentReleases ?? false,
  set: (value: boolean) => {
    setFilter("recentReleases", value);
  },
});

// Use filtering composable for clean separation of concerns
const { filteredRecords } = useListViewFiltering(records, currentListId, query, filters);

// Use shallowRef for large arrays to improve performance
const customSortableRecords = shallowRef<RecordType[]>([]);

// Use record counts composable for clean separation and reusability
const { watchedCount, toWatchCount, filteredCount } = useRecordCounts(records, filteredRecords);

// Use sorting composable for clean separation of concerns
const { sortedRecords: sortedFilteredRecords } = useListViewSorting(filteredRecords, sortComputed, currentListId);

/**
 * Optimized initialization of custom sortable records.
 * Refreshes records when filtering changes to ensure search works in custom mode.
 */
function initializeCustomSort(): void {
  if (sortComputed.value === "custom") {
    const sortedRecords = [...filteredRecords.value].sort((a, b) => (a.order ?? Infinity) - (b.order ?? Infinity));
    /* For performance, limit to first 50 items when dragging
       TODO: Implement proper pagination for custom sort later */
    customSortableRecords.value = sortedRecords.slice(0, 50);
  }
}

// Track if we're currently dragging to avoid expensive computations
const isDragging = ref(false);

let saveTimeout: ReturnType<typeof setTimeout> | null = null;

function handleSaveRecordsOrder(): void {
  // Prevent duplicate saves with debouncing
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }

  // Increased timeout for better performance during rapid drag operations
  saveTimeout = setTimeout(() => {
    if (sortComputed.value === "custom" && customSortableRecords.value.length > 0) {
      // Get all records for the current list, ordered by existing order
      const allCurrentListRecords = records.value
        .filter((r) => r.listId === currentListId.value)
        .sort((a, b) => (a.order ?? Infinity) - (b.order ?? Infinity));

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

      const payload = allCurrentListRecords.map((r) => ({ ...r }));
      saveRecordsOrder(payload);
    }
    saveTimeout = null;
  }, 300); // Increased debounce timeout for better performance during rapid drag operations
}

/**
 * Optimized reactive array for gallery drag operations.
 * Uses lazy initialization and avoids unnecessary computations during drag operations.
 */
const galleryRecords = computed({
  get() {
    if (sortComputed.value === "custom") {
      initializeCustomSort();
      return customSortableRecords.value;
    }
    // Return direct reference to avoid unnecessary copying for non-custom sorts
    return sortedFilteredRecords.value;
  },
  set(value) {
    if (sortComputed.value === "custom") {
      isDragging.value = true;
      customSortableRecords.value = value;
      // Rely on explicit @sort event for saving
      isDragging.value = false;
    }
  },
});

// Use pagination composable for clean separation of concerns
const { totalPages, paginatedRecords } = useListViewPagination(
  sortedFilteredRecords,
  page,
  50, // Items per page
);

// Wrapper function to update store query
function handleQueryUpdate(newQuery: string): void {
  setStoreQuery(newQuery);
}

const listIdRef = toRef(props, "listId");
const usernameRef = toRef(props, "username");
const isProfileViewRef = toRef(props, "isProfileView");

// Wrapper function to load all data using the composable with error handling
async function loadData(): Promise<void> {
  try {
    await loadAllData(props.isProfileView, props.username, authStore.user.isLoggedIn);
  } catch (error) {
    console.error("Error loading ListView data:", error);
    /* Could emit an error event or set an error state here
       For now, log the error and let the loading state handle it */
  }
}

// Wrapper functions for movie operations to maintain component interface
function handleAddToMyList(movieId: number, listId: number): void {
  addToMyList(movieId, listId, records.value, myRecords.value, authStore.user.isLoggedIn);
}

function handleRemoveRecord(record: RecordType): void {
  removeRecord(record, records.value);
}

function recomputeAndSaveOrderForCurrentList(updatedList: RecordType[]): void {
  // Re-number orders sequentially starting from 1
  updatedList.forEach((r, idx) => {
    r.order = idx + 1;
  });
  // Persist to backend
  saveRecordsOrder(updatedList);
  // Refresh local draggable source when in custom sort
  if (sortComputed.value === "custom") {
    // Sync the visible subset
    customSortableRecords.value = [...updatedList].slice(0, 50);
  }
}

function handleMoveToTop(record: RecordType): void {
  // Operate on full current-list records to avoid pagination/limit issues
  const allCurrentListRecords = records.value
    .filter((r) => r.listId === currentListId.value)
    .sort((a, b) => (a.order ?? Infinity) - (b.order ?? Infinity));

  const idx = allCurrentListRecords.findIndex((r) => r.id === record.id);
  if (idx === -1) {
    return;
  }
  allCurrentListRecords.splice(idx, 1);
  allCurrentListRecords.unshift(record);
  recomputeAndSaveOrderForCurrentList(allCurrentListRecords);
}

function handleMoveToBottom(record: RecordType): void {
  const allCurrentListRecords = records.value
    .filter((r) => r.listId === currentListId.value)
    .sort((a, b) => (a.order ?? Infinity) - (b.order ?? Infinity));

  const idx = allCurrentListRecords.findIndex((r) => r.id === record.id);
  if (idx === -1) {
    return;
  }
  allCurrentListRecords.splice(idx, 1);
  allCurrentListRecords.push(record);
  recomputeAndSaveOrderForCurrentList(allCurrentListRecords);
}

/**
 * Performance optimization: Debounced save operation to prevent excessive API calls
 * during drag operations. Uses a longer timeout for better batching.
 */

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
  async (loggedIn) => {
    if (loggedIn && props.isProfileView) {
      await recordsData.loadMyRecords(props.isProfileView, loggedIn);
    } else if (!loggedIn) {
      clearUserData();
    }
  },
);

// Computed properties
const isSortable = computed(() => {
  return (
    areRecordsLoaded.value &&
    paginatedRecords.value.length > 0 &&
    currentListId.value === listToWatchId &&
    sortComputed.value === "custom" &&
    modeComputed.value === "gallery" &&
    !props.isProfileView // Disable sorting for profile views
  );
});

onMounted(async () => {
  // Load persisted ListView state first
  loadPersistedState();

  // Initialize defaults if not set
  if (!mode.value) {
    setMode("full");
  }
  if (!storeSort.value) {
    setStoreSort("additionDate");
  }
  if (!page.value) {
    setStorePage(1);
  }

  // Ensure list selections are aligned before loading
  resetListSelections(props.listId);

  await loadData();
});

onUnmounted(() => {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
    saveTimeout = null;
  }
});
</script>

<style scoped>
/* Only minimal styles remain - most styles moved to individual components */
</style>
