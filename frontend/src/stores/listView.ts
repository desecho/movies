/**
 * @fileoverview Pinia store for ListView state management
 *
 * This store manages the state for ListView components including:
 * - View mode (full, minimal, gallery, compact)
 * - Sorting preferences (additionDate, releaseDate, rating, custom)
 * - Search query and filters
 * - Pagination state
 * - TTL-based caching for performance optimization
 * - State persistence to localStorage
 */

import { defineStore } from "pinia";
import { computed, ref } from "vue";

import type { RecordType } from "../types";
import type {
    ListViewFilters,
    ListViewState,
    SortType,
    ViewMode,
} from "../types/listView";

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
    const mode = ref<ViewMode>(defaultState.mode);
    const sort = ref<SortType>(defaultState.sort);
    const query = ref(defaultState.query);
    const filters = ref<ListViewFilters>({ ...defaultState.filters });
    const page = ref(defaultState.page);

    // Cached computations for performance with TTL
    const filteredRecordsCache = ref<
        Map<string, { data: RecordType[]; timestamp: number }>
    >(new Map());
    const sortedRecordsCache = ref<
        Map<string, { data: RecordType[]; timestamp: number }>
    >(new Map());

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
    function getFilterCacheKey(
        recordsLength: number,
        listId: number,
        queryStr: string,
        filtersObj: ListViewFilters,
    ): string {
        return `${recordsLength}-${listId}-${queryStr}-${JSON.stringify(filtersObj)}`;
    }

    // Cache key generator for sorted results
    function getSortCacheKey(
        recordsLength: number,
        listId: number,
        sortType: string,
    ): string {
        return `${recordsLength}-${listId}-${sortType}`;
    }

    // Persist state to localStorage (exclude page)
    function persistState(): void {
        const stateToSave = {
            mode: mode.value,
            sort: sort.value,
            query: query.value,
            filters: filters.value,
        };
        localStorage.setItem("listViewState", JSON.stringify(stateToSave));
    }

    function clearCache(): void {
        filteredRecordsCache.value.clear();
        sortedRecordsCache.value.clear();
    }

    function resetToDefault(): void {
        mode.value = defaultState.mode;
        sort.value = defaultState.sort;
        query.value = defaultState.query;
        filters.value = { ...defaultState.filters };
        page.value = defaultState.page;
        clearCache();
        localStorage.removeItem("listViewState");
    }

    // Actions
    /**
     * Sets the current view mode and persists to localStorage
     * @param newMode - The new view mode to set
     */
    function setMode(newMode: ViewMode): void {
        mode.value = newMode;
        persistState();
    }

    /**
     * Sets the current sort type, resets to page 1, and persists to localStorage
     * @param newSort - The new sort type to set
     */
    function setSort(newSort: SortType): void {
        sort.value = newSort;
        page.value = 1; // Reset to first page when sorting changes
        persistState();
    }

    /**
     * Sets the search query, resets to page 1, and persists to localStorage
     * @param newQuery - The search query string
     */
    function setQuery(newQuery: string): void {
        query.value = newQuery;
        page.value = 1; // Reset to first page when search changes
        persistState();
    }

    /**
     * Sets a specific filter value, resets to page 1, and persists to localStorage
     * @param filterName - The name of the filter to update
     * @param value - The new boolean value for the filter
     */
    function setFilter(
        filterName: keyof ListViewFilters,
        value: boolean,
    ): void {
        filters.value[filterName] = value;
        page.value = 1; // Reset to first page when filters change
        persistState();
    }

    /**
     * Sets the current page number (not persisted to localStorage)
     * @param newPage - The page number to set (1-based)
     */
    function setPage(newPage: number): void {
        page.value = newPage;
        // Don't persist page state - it should reset on navigation
    }

    function resetFilters(): void {
        filters.value = { ...defaultState.filters };
        query.value = defaultState.query;
        page.value = 1;
        persistState();
    }

    function getCachedFilteredRecords(key: string): RecordType[] | null {
        const cached = filteredRecordsCache.value.get(key);
        if (!cached) {
            return null;
        }

        // Check if cache has expired
        if (Date.now() - cached.timestamp > CACHE_TTL) {
            filteredRecordsCache.value.delete(key);
            return null;
        }

        return cached.data;
    }

    function setCachedFilteredRecords(key: string, data: RecordType[]): void {
        filteredRecordsCache.value.set(key, {
            data,
            timestamp: Date.now(),
        });
    }

    function getCachedSortedRecords(key: string): RecordType[] | null {
        const cached = sortedRecordsCache.value.get(key);
        if (!cached) {
            return null;
        }

        // Check if cache has expired
        if (Date.now() - cached.timestamp > CACHE_TTL) {
            sortedRecordsCache.value.delete(key);
            return null;
        }

        return cached.data;
    }

    function setCachedSortedRecords(key: string, data: RecordType[]): void {
        sortedRecordsCache.value.set(key, {
            data,
            timestamp: Date.now(),
        });
    }

    // Load state from localStorage
    function loadPersistedState(): void {
        try {
            const saved = localStorage.getItem("listViewState");
            if (saved) {
                const state = JSON.parse(saved) as {
                    mode?: ViewMode;
                    sort?: SortType;
                    query?: string;
                    filters?: Partial<ListViewFilters>;
                };
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
