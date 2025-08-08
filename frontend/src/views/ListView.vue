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
      v-model:mode="modeComputed"
      v-model:sort="sortComputed"
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

    <!-- Content when not loading -->
    <v-row v-if="!isRecordsLoading">
      <v-col cols="12">
        <!-- Regular view modes (non-gallery) -->
        <div v-cloak v-if="modeComputed != 'gallery'">
          <template v-for="(record, index) in paginatedRecords" :key="record.id">
            <MovieItemComponent
              :record="record"
              :record-index="index"
              :mode="modeComputed"
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
          v-if="modeComputed === 'gallery'"
          v-model:records="galleryRecords"
          :paginated-records="sortComputed === 'custom' ? galleryRecords : paginatedRecords"
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
      @update:page="setStorePage"
    />
  </v-container>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, shallowRef, toRef, watch } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
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
import { useListViewStore } from "../stores/listView";

const props = defineProps<{
  listId: number;
  username?: string;
  isProfileView?: boolean;
}>();

const router = useRouter();

const recordsStore = useRecordsStore();
const authStore = useAuthStore();
const listViewStore = useListViewStore();

const records = toRef(recordsStore, "records");
const areRecordsLoaded = toRef(recordsStore, "areLoaded");
const isRecordsLoading = toRef(recordsStore, "isLoading");

// Initialize ListView state from store
const {
  mode,
  sort: storeSort,
  query: storeQuery,
  filters,
  page: storePage,
} = storeToRefs(listViewStore);

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
const { selectedProfileList, selectedUserList, currentListId, resetListSelections, initializeWatchers } =
  listNavigation;

// Use store values for query and sort, with page from navigation  
const query = storeQuery;
const page = storePage;

// Create writable computed for mode and sort
const modeComputed = computed({
  get: () => {
    return mode.value || 'full';
  },
  set: (value: string) => {
    setMode(value as any);
  }
});

const sortComputed = computed({
  get: () => {
    return storeSort.value || 'additionDate';
  },
  set: (value: string) => {
    setStoreSort(value as any);
  }
});

// Create writable computed properties for filter bindings
const toRewatchFilter = computed({
  get: () => filters.value?.toRewatch ?? false,
  set: (value: boolean) => setFilter('toRewatch', value)
});

const hideUnreleasedMovies = computed({
  get: () => filters.value?.hideUnreleased ?? false,
  set: (value: boolean) => setFilter('hideUnreleased', value)
});

const recentReleasesFilter = computed({
  get: () => filters.value?.recentReleases ?? false,
  set: (value: boolean) => setFilter('recentReleases', value)
});

// Filtered records with all filters applied
const filteredRecords = computed(() => {
  if (!records.value.length) {
    return [];
  }
  
  return records.value.filter((record) => {
    // Basic list filter - must match current list
    if (record.listId !== currentListId.value) {
      return false;
    }
    
    // Search filter
    const searchQuery = query.value?.trim().toLowerCase();
    if (searchQuery) {
      const movieTitle = record.movie.title.toLowerCase();
      const originalTitle = record.movie.titleOriginal.toLowerCase();
      const director = record.movie.director?.toLowerCase() || '';
      const actors = record.movie.actors?.toLowerCase() || '';
      
      if (!movieTitle.includes(searchQuery) && 
          !originalTitle.includes(searchQuery) && 
          !director.includes(searchQuery) && 
          !actors.includes(searchQuery)) {
        return false;
      }
    }
    
    // To Rewatch filter (only for watched list)
    if (toRewatchFilter.value && currentListId.value === 1) { // listWatchedId
      if (!(record.rating === 5 &&
            ((!record.options.ultraHd && !record.options.theatre) ||
             !record.options.original) &&
            !record.options.ignoreRewatch)) {
        return false;
      }
    }
    
    // Hide unreleased movies filter (only for to-watch list)
    if (hideUnreleasedMovies.value && currentListId.value === 2) { // listToWatchId
      if (!record.movie.isReleased) {
        return false;
      }
    }
    
    // Recent releases filter (only for to-watch list)
    if (recentReleasesFilter.value && currentListId.value === 2) { // listToWatchId
      if (!record.movie.releaseDate || !record.movie.releaseDateTimestamp) {
        return false;
      }
      
      const sixMonthsAgo = new Date();
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
      const movieReleaseDate = new Date(record.movie.releaseDateTimestamp * 1000);
      
      if (movieReleaseDate < sixMonthsAgo) {
        return false;
      }
    }
    
    return true;
  });
});

// Use shallowRef for large arrays to improve performance
const customSortableRecords = shallowRef<RecordType[]>([]);

// Simple count computations
const watchedCount = computed(() => {
  return records.value.filter(record => record.listId === 1).length; // listWatchedId
});

const toWatchCount = computed(() => {
  return records.value.filter(record => record.listId === 2).length; // listToWatchId  
});

// Apply sorting to filtered records
const sortedFilteredRecords = computed(() => {
  if (!filteredRecords.value.length) {
    return [];
  }

  const recordsCopy = [...filteredRecords.value];

  switch (sortComputed.value) {
    case "custom":
      return recordsCopy.sort((a, b) => a.order - b.order);
    case "releaseDate":
      return recordsCopy.sort((a, b) => b.movie.releaseDateTimestamp - a.movie.releaseDateTimestamp);
    case "rating":
      if (currentListId.value === listWatchedId) {
        return recordsCopy.sort((a, b) => b.rating - a.rating);
      } else {
        return recordsCopy.sort((a, b) => b.movie.imdbRating - a.movie.imdbRating);
      }
    default: // AdditionDate
      return recordsCopy.sort((a, b) => b.additionDate - a.additionDate);
  }
});

// Only populate custom sortable records when we actually need them for dragging
const initializeCustomSort = () => {
  if (sortComputed.value === "custom" && customSortableRecords.value.length === 0) {
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
    if (sortComputed.value === "custom") {
      initializeCustomSort();
      return customSortableRecords.value;
    }
    return sortedFilteredRecords.value;
  },
  set(value) {
    if (sortComputed.value === "custom") {
      isDragging.value = true;
      customSortableRecords.value = value;
      // Save after drag completes
      handleSaveRecordsOrder();
      isDragging.value = false;
    }
  },
});


// Get pagination utilities with performance optimization
const perPage = 50;
const totalPages = computed(() => Math.ceil(sortedFilteredRecords.value.length / perPage));

// Memoize pagination to avoid unnecessary recalculations
let lastPageValue = 0;
let lastRecordsLength = 0; 
let cachedPaginatedRecords: RecordType[] = [];

const paginatedRecords = computed(() => {
  const currentRecords = sortedFilteredRecords.value;
  const currentPage = page.value || 1; // Default to page 1 if undefined
  
  // Use cache if page and records haven't changed
  if (currentPage === lastPageValue && currentRecords.length === lastRecordsLength) {
    return cachedPaginatedRecords;
  }
  
  const start = (currentPage - 1) * perPage;
  const result = currentRecords.slice(start, start + perPage);
  
  // Update cache
  lastPageValue = currentPage;
  lastRecordsLength = currentRecords.length;
  cachedPaginatedRecords = result;
  
  return result;
});

// Wrapper function to update store query
const handleQueryUpdate = (newQuery: string) => {
  setStoreQuery(newQuery);
};

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
    sortComputed.value === "custom" &&
    (modeComputed.value === "minimal" || modeComputed.value === "gallery") &&
    !props.isProfileView // Disable sorting for profile views
  );
});

onMounted(async () => {
  // Load persisted ListView state first
  loadPersistedState();
  
  // Initialize defaults if not set
  if (!mode.value) {
    setMode('full');
  }
  if (!storeSort.value) {
    setStoreSort('additionDate');
  }
  if (!page.value) {
    setStorePage(1);
  }
  
  await loadData();
});
</script>

<style scoped>
/* Only minimal styles remain - most styles moved to individual components */
</style>
