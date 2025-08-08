import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { RecordType } from "../types";

export interface ListViewFilters {
  toRewatch: boolean;
  hideUnreleased: boolean;
  recentReleases: boolean;
}

export interface ListViewState {
  mode: "full" | "minimal" | "gallery";
  sort: "additionDate" | "releaseDate" | "rating" | "custom";
  query: string;
  filters: ListViewFilters;
  page: number;
}

const defaultState: ListViewState = {
  mode: "full",
  sort: "additionDate", 
  query: "",
  filters: {
    toRewatch: false,
    hideUnreleased: false,
    recentReleases: false,
  },
  page: 1,
};

export const useListViewStore = defineStore("listView", () => {
  // State
  const mode = ref<ListViewState["mode"]>(defaultState.mode);
  const sort = ref<ListViewState["sort"]>(defaultState.sort);
  const query = ref(defaultState.query);
  const filters = ref<ListViewFilters>({ ...defaultState.filters });
  const page = ref(defaultState.page);
  
  // Cached computations for performance with TTL
  const filteredRecordsCache = ref<Map<string, { data: RecordType[], timestamp: number }>>(new Map());
  const sortedRecordsCache = ref<Map<string, { data: RecordType[], timestamp: number }>>(new Map());
  
  // Cache TTL in milliseconds (5 minutes)
  const CACHE_TTL = 5 * 60 * 1000;

  // Computed properties
  const currentState = computed<ListViewState>(() => ({
    mode: mode.value,
    sort: sort.value,
    query: query.value,
    filters: { ...filters.value },
    page: page.value,
  }));

  // Cache key generator for filtered results
  const getFilterCacheKey = (
    recordsLength: number,
    listId: number,
    queryStr: string,
    filtersObj: ListViewFilters
  ) => {
    return `${recordsLength}-${listId}-${queryStr}-${JSON.stringify(filtersObj)}`;
  };

  // Cache key generator for sorted results  
  const getSortCacheKey = (
    recordsLength: number,
    listId: number,
    sortType: string
  ) => {
    return `${recordsLength}-${listId}-${sortType}`;
  };

  // Actions
  function setMode(newMode: ListViewState["mode"]) {
    mode.value = newMode;
    persistState();
  }

  function setSort(newSort: ListViewState["sort"]) {
    sort.value = newSort;
    page.value = 1; // Reset to first page when sorting changes
    persistState();
  }

  function setQuery(newQuery: string) {
    query.value = newQuery;
    page.value = 1; // Reset to first page when search changes
    persistState();
  }

  function setFilter(filterName: keyof ListViewFilters, value: boolean) {
    filters.value[filterName] = value;
    page.value = 1; // Reset to first page when filters change
    persistState();
  }

  function setPage(newPage: number) {
    page.value = newPage;
    // Don't persist page state - it should reset on navigation
  }

  function resetFilters() {
    filters.value = { ...defaultState.filters };
    query.value = defaultState.query;
    page.value = 1;
    persistState();
  }

  function clearCache() {
    filteredRecordsCache.value.clear();
    sortedRecordsCache.value.clear();
  }
  
  function getCachedFilteredRecords(key: string): RecordType[] | null {
    const cached = filteredRecordsCache.value.get(key);
    if (!cached) return null;
    
    // Check if cache has expired
    if (Date.now() - cached.timestamp > CACHE_TTL) {
      filteredRecordsCache.value.delete(key);
      return null;
    }
    
    return cached.data;
  }
  
  function setCachedFilteredRecords(key: string, data: RecordType[]) {
    filteredRecordsCache.value.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  function getCachedSortedRecords(key: string): RecordType[] | null {
    const cached = sortedRecordsCache.value.get(key);
    if (!cached) return null;
    
    // Check if cache has expired
    if (Date.now() - cached.timestamp > CACHE_TTL) {
      sortedRecordsCache.value.delete(key);
      return null;
    }
    
    return cached.data;
  }
  
  function setCachedSortedRecords(key: string, data: RecordType[]) {
    sortedRecordsCache.value.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Persist state to localStorage (exclude page)
  function persistState() {
    const stateToSave = {
      mode: mode.value,
      sort: sort.value,
      query: query.value,
      filters: filters.value,
    };
    localStorage.setItem("listViewState", JSON.stringify(stateToSave));
  }

  // Load state from localStorage
  function loadPersistedState() {
    try {
      const saved = localStorage.getItem("listViewState");
      if (saved) {
        const state = JSON.parse(saved);
        mode.value = state.mode || defaultState.mode;
        sort.value = state.sort || defaultState.sort;
        query.value = state.query || defaultState.query;
        filters.value = { ...defaultState.filters, ...state.filters };
        // Don't restore page - always start at page 1
        page.value = 1;
      }
    } catch (error) {
      console.warn("Failed to load persisted ListView state:", error);
      resetToDefault();
    }
  }

  function resetToDefault() {
    mode.value = defaultState.mode;
    sort.value = defaultState.sort;
    query.value = defaultState.query;
    filters.value = { ...defaultState.filters };
    page.value = defaultState.page;
    clearCache();
    localStorage.removeItem("listViewState");
  }

  return {
    // State
    mode,
    sort,
    query,
    filters,
    page,
    currentState,
    
    // Cache
    filteredRecordsCache,
    sortedRecordsCache,
    getFilterCacheKey,
    getSortCacheKey,
    getCachedFilteredRecords,
    setCachedFilteredRecords,
    getCachedSortedRecords,
    setCachedSortedRecords,
    
    // Actions
    setMode,
    setSort,
    setQuery,
    setFilter,
    setPage,
    resetFilters,
    clearCache,
    loadPersistedState,
    resetToDefault,
  };
});