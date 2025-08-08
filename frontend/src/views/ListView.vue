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
      @update:query="setQuery"
      :watched-count="watchedCount"
      :to-watch-count="toWatchCount"
      :filtered-count="sortedFilteredRecords.length"
      :are-records-loaded="areRecordsLoaded"
      :is-records-loading="isRecordsLoading"
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
              @remove="removeRecord"
              @add-to-my-list="addToMyList"
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
          v-model:records="sortedFilteredRecords"
          :paginated-records="paginatedRecords"
          :is-sortable="isSortable"
          :is-profile-view="isProfileView"
          @sort="saveRecordsOrder"
          @move-to-top="moveToTop"
          @move-to-bottom="moveToBottom"
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
import axios from "axios";
import { computed, onMounted, ref, toRef, watch } from "vue";
import { useRouter } from "vue-router";
import Draggable from "vuedraggable";

import type { RecordType, SortData } from "../types";

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
import { useRecordFilters } from "../composables/useRecordFilters";
import { useRecordSorting } from "../composables/useRecordSorting";
import { useRequestDeduplication } from "../composables/useRequestDeduplication";
import { listToWatchId, listWatchedId } from "../const";
import { getUrl } from "../helpers";
import { useAuthStore } from "../stores/auth";
import { useRecordsStore } from "../stores/records";
import { $toast } from "../toast";

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

// Request deduplication composable
const { deduplicateRequest } = useRequestDeduplication();

// For profile views, allow switching between lists
const selectedProfileList = ref(props.listId);

// For regular users, allow switching between their own lists
const selectedUserList = ref(props.listId);

// User avatar for profile views
const userAvatarUrl = ref<string | null>(null);

// Track loading state for add to list buttons
const addingToList = ref<Record<string, boolean>>({});

// Store user's own records for checking if movie already exists
const myRecords = ref<RecordType[]>([]);

// Computed property to get the current list ID (either from props or selected by user)
const currentListId = computed(() => {
  return props.isProfileView ? selectedProfileList.value : selectedUserList.value;
});

// Initialize composables
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

// Apply sorting to filtered records
const sortedFilteredRecords = computed(() => {
  if (!filteredRecords.value.length) return [];
  
  const recordsCopy = [...filteredRecords.value];

  switch (sort.value) {
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
    default: // additionDate
      return recordsCopy.sort((a, b) => b.additionDate - a.additionDate);
  }
});

// Get optimized count computations
const watchedCount = filterComposable.getWatchedCount();
const toWatchCount = filterComposable.getToWatchCount();

// Get pagination utilities
const page = ref(1);
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

async function loadRecordsData(): Promise<void> {
  const { loadRecords } = useRecordsStore();
  
  const cacheKey = props.isProfileView && props.username 
    ? `records-profile-${props.username}` 
    : 'records-user';

  return deduplicateRequest(cacheKey, async () => {
    try {
      if (props.isProfileView && props.username) {
        await loadRecords(props.username);
      } else {
        await loadRecords();
      }
    } catch (error: unknown) {
      console.log(error);
      const errorMessage =
        props.isProfileView && props.username ? `Error loading ${props.username}'s movies` : "Error loading movies";
      $toast.error(errorMessage);
      throw error; // Re-throw to prevent caching failed requests
    }
  });
}

// Load user's own records when viewing a profile (if logged in)
async function loadMyRecords(): Promise<void> {
  if (props.isProfileView && authStore.user.isLoggedIn) {
    return deduplicateRequest('my-records', async () => {
      try {
        const response = await axios.get(getUrl("records/"));
        myRecords.value = response.data as RecordType[];
      } catch (error) {
        console.log("Error loading user's records:", error);
        throw error;
      }
    });
  }
}

// Load user avatar for profile views
async function loadUserAvatar(): Promise<void> {
  if (props.isProfileView && props.username) {
    const cacheKey = `avatar-${props.username}`;
    return deduplicateRequest(cacheKey, async () => {
      try {
        const response = await axios.get(getUrl(`users/${props.username}/avatar/`));
        const userData = response.data as { username: string; avatar_url: string | null };
        userAvatarUrl.value = userData.avatar_url;
      } catch (error) {
        console.log("Error loading user avatar:", error);
        userAvatarUrl.value = null;
        throw error;
      }
    });
  }
}

function addToList(movieId: number, listId: number, record?: RecordType): void {
  axios
    .post(getUrl(`add-to-list/${movieId}/`), {
      listId,
    })
    .then(() => {
      if (record !== undefined) {
        record.listId = listId;
        record.additionDate = Date.now();
      }
    })
    .catch(() => {
      $toast.error("Error adding the movie to the list");
    });
}

// Add movie to user's own list
function addToMyList(movieId: number, listId: number): void {
  if (!authStore.user.isLoggedIn) {
    $toast.error("You must be logged in to add movies to your list");
    return;
  }

  const loadingKey = `${movieId}-${listId}`;
  addingToList.value[loadingKey] = true;

  try {
    // Add to myRecords for immediate UI update
    const movieData = records.value.find((record) => record.movie.id === movieId)?.movie;
    addToList(movieId, listId); // Call the existing addToList function
    if (movieData) {
      const newRecord: RecordType = {
        id: Date.now(),
        movie: movieData,
        listId,
        rating: 0,
        comment: "",
        additionDate: Date.now(),
        order: myRecords.value.length + 1,
        options: {
          original: false,
          extended: false,
          theatre: false,
          hd: false,
          fullHd: false,
          ultraHd: false,
          ignoreRewatch: false,
        },
        providerRecords: [],
        ratingOriginal: 0,
        commentArea: false,
      };
      myRecords.value.push(newRecord);
    }

    const listName = listId === listWatchedId ? "Watched" : "To Watch";
    $toast.success(`Movie added to your ${listName} list`);
  } catch (error) {
    console.log("Error adding movie to list:", error);
    $toast.error("Error adding movie to your list");
  } finally {
    addingToList.value[loadingKey] = false;
  }
}

// Watch for changes in props that require reloading data
watch([listIdRef, usernameRef, isProfileViewRef], async () => {
  selectedProfileList.value = props.listId; // Reset profile list selector
  selectedUserList.value = props.listId; // Reset user list selector
  // Force reload records when switching contexts - run in parallel for better performance
  await Promise.all([
    loadUserAvatar(), // Load user's avatar if viewing profile
    loadRecordsData(),
    loadMyRecords(), // Load user's records if viewing profile
  ]);
  // Sort records after data is loaded
  sortRecords();
});

// Watch for profile list selection changes
watch(selectedProfileList, async (newListId) => {
  if (props.isProfileView && props.username) {
    page.value = 1; // Reset to first page when switching lists

    // Navigate to the appropriate profile route
    const newPath =
      newListId === listWatchedId ? `/users/${props.username}/list/watched` : `/users/${props.username}/list/to-watch`;
    if (router.currentRoute.value.path !== newPath) {
      await router.push(newPath);
    }

    // Re-load data to ensure we have the latest order values
    await loadRecordsData();
    sortRecords();
  }
});

// Watch for user list selection changes (for regular users)
watch(selectedUserList, async (newListId) => {
  if (!props.isProfileView) {
    page.value = 1; // Reset to first page when switching lists

    // Navigate to the appropriate route
    const newPath = newListId === listWatchedId ? "/list/watched" : "/list/to-watch";
    if (router.currentRoute.value.path !== newPath) {
      await router.push(newPath);
    }

    // Re-load data to ensure we have the latest order values
    await loadRecordsData();
    sortRecords();
  }
});

// Watch for login status changes
watch(
  () => authStore.user.isLoggedIn,
  async (isLoggedIn) => {
    if (isLoggedIn && props.isProfileView) {
      await loadMyRecords();
    } else if (!isLoggedIn) {
      myRecords.value = [];
    }
  },
);

// Update record comment from child component
function updateRecordComment(record: RecordType, comment: string): void {
  record.comment = comment;
}

const isSortable = computed(() => {
  return (
    currentListId.value === listToWatchId &&
    sort.value === "custom" &&
    (mode.value === "minimal" || mode.value === "gallery") &&
    !props.isProfileView // Disable sorting for profile views
  );
});

function saveRecordsOrder(): void {
  function getSortData(): SortData[] {
    const data: SortData[] = [];
    records.value.forEach((record, index) => {
      const sortData = { id: record.id, order: index + 1 };
      // Update the local order value to match the new position
      record.order = index + 1;
      data.push(sortData);
    });
    return data;
  }

  axios.put(getUrl("save-records-order/"), { records: getSortData() }).catch(() => {
    $toast.error("Error saving movie order");
  });
}

function changeRating(record: RecordType, rating: number): void {
  axios
    .put(getUrl(`change-rating/${record.id}/`), { rating })
    .then(() => {
      record.ratingOriginal = record.rating;
    })
    .catch(() => {
      record.rating = record.ratingOriginal;
      $toast.error("Error saving the rating");
    });
}

function saveOptions(record: RecordType, field: keyof RecordType["options"]): void {
  const data = {
    options: record.options,
  };

  axios.put(getUrl(`record/${record.id}/options/`), data).catch(() => {
    record.options[field] = !record.options[field];
    $toast.error("Error saving options");
  });
}

function removeRecord(record: RecordType, index: number): void {
  axios
    .delete(getUrl(`remove-record/${record.id}/`))
    .then(() => {
      records.value.splice(index, 1);
    })
    .catch(() => {
      $toast.error("Error removing the movie");
    });
}
function showCommentArea(record: RecordType): void {
  record.commentArea = true;
}

function saveComment(record: RecordType): void {
  const data = {
    comment: record.comment,
  };
  axios
    .put(getUrl(`save-comment/${record.id}/`), data)
    .then(() => {
      if (record.comment === "") {
        record.commentArea = false;
      }
    })
    .catch(() => {
      $toast.error("Error saving a comment");
    });
}

function moveToTop(record: RecordType, index: number): void {
  records.value.splice(index, 1);
  records.value.unshift(record);
  saveRecordsOrder();
}

function moveToBottom(record: RecordType, index: number): void {
  records.value.splice(index, 1);
  records.value.push(record);
  saveRecordsOrder();
}

onMounted(async () => {
  // Run all data loading functions in parallel for better performance
  await Promise.all([
    loadRecordsData(),
    loadMyRecords(), // Load user's records if viewing profile and logged in
    loadUserAvatar(), // Load user's avatar if viewing profile
  ]);
});
</script>

<style scoped>
/* Only minimal styles remain - most styles moved to individual components */
</style>
