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
import type { ViewMode, SortType } from "../types/listView";

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

/**
 * Writable computed for view mode that integrates with the ListView store.
 * Provides two-way binding for v-model directives.
 */
const modeComputed = computed({
  get: () => {
    return mode.value || 'full';
  },
  set: (value: ViewMode) => {
    setMode(value);
  }
});

/**
 * Writable computed for sort type that integrates with the ListView store.
 * Provides two-way binding for v-model directives.
 */
const sortComputed = computed({
  get: () => {
    return storeSort.value || 'additionDate';
  },
  set: (value: SortType) => {
    setStoreSort(value);
  }
});

/**
 * Writable computed properties for filter bindings with the ListView store.
 * These provide two-way binding for various filter controls.
 */

/** Filter for showing only movies marked for rewatching (watched list only) */
const toRewatchFilter = computed({
  get: () => filters.value?.toRewatch ?? false,
  set: (value: boolean) => setFilter('toRewatch', value)
});

/** Filter for hiding unreleased movies (to-watch list only) */
const hideUnreleasedMovies = computed({
  get: () => filters.value?.hideUnreleased ?? false,
  set: (value: boolean) => setFilter('hideUnreleased', value)
});

/** Filter for showing only recent releases from last 6 months (to-watch list only) */
const recentReleasesFilter = computed({
  get: () => filters.value?.recentReleases ?? false,
  set: (value: boolean) => setFilter('recentReleases', value)
});

/**
 * Computes filtered records based on current list, search query, and active filters.
 * Applies comprehensive error handling for malformed data.
 * 
 * @returns Array of RecordType objects that match all active filters
 */
const filteredRecords = computed(() => {
  try {
    if (!records.value || !Array.isArray(records.value) || records.value.length === 0) {
      return [];
    }
    
    return records.value.filter((record) => {
      try {
        // Validate record structure
        if (!record || !record.movie || typeof record.listId !== 'number') {
          console.warn('Invalid record structure:', record);
          return false;
        }
        
        // Basic list filter - must match current list
        if (record.listId !== currentListId.value) {
          return false;
        }
        
        // Search filter with null safety
        const searchQuery = query.value?.trim().toLowerCase();
        if (searchQuery) {
          const movieTitle = record.movie.title?.toLowerCase() || '';
          const originalTitle = record.movie.titleOriginal?.toLowerCase() || '';
          const director = record.movie.director?.toLowerCase() || '';
          const actors = record.movie.actors?.toLowerCase() || '';
          
          if (!movieTitle.includes(searchQuery) && 
              !originalTitle.includes(searchQuery) && 
              !director.includes(searchQuery) && 
              !actors.includes(searchQuery)) {
            return false;
          }
        }
        
        // To Rewatch filter (only for watched list) with null safety
        if (toRewatchFilter.value && currentListId.value === 1) { // listWatchedId
          if (!record.options || typeof record.rating !== 'number') {
            return false;
          }
          if (!(record.rating === 5 &&
                ((!record.options.ultraHd && !record.options.theatre) ||
                 !record.options.original) &&
                !record.options.ignoreRewatch)) {
            return false;
          }
        }
        
        // Hide unreleased movies filter (only for to-watch list)
        if (hideUnreleasedMovies.value && currentListId.value === 2) { // listToWatchId
          if (typeof record.movie.isReleased !== 'boolean' || !record.movie.isReleased) {
            return false;
          }
        }
        
        // Recent releases filter (only for to-watch list) with date validation
        if (recentReleasesFilter.value && currentListId.value === 2) { // listToWatchId
          if (!record.movie.releaseDate || 
              typeof record.movie.releaseDateTimestamp !== 'number' || 
              record.movie.releaseDateTimestamp <= 0) {
            return false;
          }
          
          try {
            const sixMonthsAgo = new Date();
            sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
            const movieReleaseDate = new Date(record.movie.releaseDateTimestamp * 1000);
            
            if (isNaN(movieReleaseDate.getTime()) || movieReleaseDate < sixMonthsAgo) {
              return false;
            }
          } catch (dateError) {
            console.warn('Date processing error for record:', record.id, dateError);
            return false;
          }
        }
        
        return true;
      } catch (recordError) {
        console.warn('Error processing record:', record?.id || 'unknown', recordError);
        return false;
      }
    });
  } catch (error) {
    console.error('Error in filteredRecords computation:', error);
    return [];
  }
});

// Use shallowRef for large arrays to improve performance
const customSortableRecords = shallowRef<RecordType[]>([]);

/**
 * Optimized count computations with memoization for better performance.
 * Only recalculates when records array changes, not on every render.
 */
const watchedCount = computed(() => {
  if (!records.value || !Array.isArray(records.value)) return 0;
  return records.value.filter(record => record.listId === 1).length; // listWatchedId
});

const toWatchCount = computed(() => {
  if (!records.value || !Array.isArray(records.value)) return 0;
  return records.value.filter(record => record.listId === 2).length; // listToWatchId  
});

// Apply sorting to filtered records with error handling
const sortedFilteredRecords = computed(() => {
  try {
    if (!filteredRecords.value || !Array.isArray(filteredRecords.value) || filteredRecords.value.length === 0) {
      return [];
    }

    const recordsCopy = [...filteredRecords.value];

    switch (sortComputed.value) {
      case "custom":
        return recordsCopy.sort((a, b) => {
          try {
            const orderA = typeof a.order === 'number' ? a.order : 0;
            const orderB = typeof b.order === 'number' ? b.order : 0;
            return orderA - orderB;
          } catch (error) {
            console.warn('Error sorting by custom order:', error);
            return 0;
          }
        });
      case "releaseDate":
        return recordsCopy.sort((a, b) => {
          try {
            const timestampA = typeof a.movie?.releaseDateTimestamp === 'number' ? a.movie.releaseDateTimestamp : 0;
            const timestampB = typeof b.movie?.releaseDateTimestamp === 'number' ? b.movie.releaseDateTimestamp : 0;
            return timestampB - timestampA;
          } catch (error) {
            console.warn('Error sorting by release date:', error);
            return 0;
          }
        });
      case "rating":
        if (currentListId.value === listWatchedId) {
          return recordsCopy.sort((a, b) => {
            try {
              const ratingA = typeof a.rating === 'number' ? a.rating : 0;
              const ratingB = typeof b.rating === 'number' ? b.rating : 0;
              return ratingB - ratingA;
            } catch (error) {
              console.warn('Error sorting by user rating:', error);
              return 0;
            }
          });
        } else {
          return recordsCopy.sort((a, b) => {
            try {
              const imdbA = typeof a.movie?.imdbRating === 'number' ? a.movie.imdbRating : 0;
              const imdbB = typeof b.movie?.imdbRating === 'number' ? b.movie.imdbRating : 0;
              return imdbB - imdbA;
            } catch (error) {
              console.warn('Error sorting by IMDB rating:', error);
              return 0;
            }
          });
        }
      default: // AdditionDate
        return recordsCopy.sort((a, b) => {
          try {
            const dateA = typeof a.additionDate === 'number' ? a.additionDate : 0;
            const dateB = typeof b.additionDate === 'number' ? b.additionDate : 0;
            return dateB - dateA;
          } catch (error) {
            console.warn('Error sorting by addition date:', error);
            return 0;
          }
        });
    }
  } catch (error) {
    console.error('Error in sortedFilteredRecords computation:', error);
    return filteredRecords.value || [];
  }
});

/**
 * Optimized initialization of custom sortable records.
 * Only populates when needed for dragging operations and limits items for performance.
 */
const initializeCustomSort = () => {
  if (sortComputed.value === "custom" && customSortableRecords.value.length === 0) {
    const sortedRecords = [...filteredRecords.value].sort((a, b) => {
      // Safe sorting with fallback values
      const orderA = typeof a.order === 'number' ? a.order : 0;
      const orderB = typeof b.order === 'number' ? b.order : 0;
      return orderA - orderB;
    });
    /* For performance, limit to first 50 items when dragging
       TODO: Implement proper pagination for custom sort later */
    customSortableRecords.value = sortedRecords.slice(0, 50);
  }
};

// Track if we're currently dragging to avoid expensive computations
const isDragging = ref(false);

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
      // Save after drag completes (debounced)
      handleSaveRecordsOrder();
      isDragging.value = false;
    }
  },
});


// Get pagination utilities with performance optimization and error handling
const perPage = 50;
const totalPages = computed(() => {
  try {
    const recordsLength = sortedFilteredRecords.value?.length || 0;
    if (recordsLength === 0) return 1;
    const pages = Math.ceil(recordsLength / perPage);
    return pages > 0 ? pages : 1;
  } catch (error) {
    console.warn('Error calculating total pages:', error);
    return 1;
  }
});

/**
 * Performance optimization: Memoize pagination to avoid unnecessary recalculations.
 * This cache is particularly important for large datasets where slicing operations
 * can be expensive when performed on every render cycle.
 */
let lastPageValue = 0;
let lastRecordsLength = 0; 
let cachedPaginatedRecords: RecordType[] = [];

const paginatedRecords = computed(() => {
  try {
    const currentRecords = sortedFilteredRecords.value || [];
    const currentPage = Math.max(1, Math.min(page.value || 1, totalPages.value)); // Ensure page is within valid range
    
    // Use cache if page and records haven't changed
    if (currentPage === lastPageValue && currentRecords.length === lastRecordsLength) {
      return cachedPaginatedRecords;
    }
    
    // Validate pagination bounds
    const start = Math.max(0, (currentPage - 1) * perPage);
    const end = Math.min(currentRecords.length, start + perPage);
    const result = currentRecords.slice(start, end);
    
    // Update cache
    lastPageValue = currentPage;
    lastRecordsLength = currentRecords.length;
    cachedPaginatedRecords = result;
    
    return result;
  } catch (error) {
    console.error('Error in paginatedRecords computation:', error);
    return cachedPaginatedRecords || [];
  }
});

// Wrapper function to update store query
const handleQueryUpdate = (newQuery: string) => {
  setStoreQuery(newQuery);
};

const listIdRef = toRef(props, "listId");
const usernameRef = toRef(props, "username");
const isProfileViewRef = toRef(props, "isProfileView");

// Wrapper function to load all data using the composable with error handling
async function loadData(): Promise<void> {
  try {
    await loadAllData(props.isProfileView, props.username, authStore.user.isLoggedIn);
  } catch (error) {
    console.error('Error loading ListView data:', error);
    // Could emit an error event or set an error state here
    // For now, log the error and let the loading state handle it
  }
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

/**
 * Performance optimization: Debounced save operation to prevent excessive API calls
 * during drag operations. Uses a longer timeout for better batching.
 */
let saveTimeout: number | null = null;

const handleSaveRecordsOrder = () => {
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
  }, 300); // Increased debounce timeout for better performance during rapid drag operations
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
