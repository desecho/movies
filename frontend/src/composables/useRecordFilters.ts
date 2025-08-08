import { debounce } from "lodash";
import { computed, ref, type Ref } from "vue";

import type { RecordType } from "../types";

import { listToWatchId, listWatchedId } from "../const";

export function useRecordFilters(
    records: Ref<RecordType[]>,
    currentListId: Ref<number>,
    initialQuery = "",
) {
    const query = ref(initialQuery);
    const debouncedQuery = ref(initialQuery);

    // Debounced search - updates after 300ms of no typing
    const updateDebouncedQuery = debounce((value: string) => {
        debouncedQuery.value = value;
    }, 300);

    // Watch for query changes and debounce them
    const setQuery = (value: string) => {
        query.value = value;
        updateDebouncedQuery(value);
    };

    // Memoized search filter
    const searchMatchesRecord = (
        record: RecordType,
        searchQuery: string,
    ): boolean => {
        if (!searchQuery) {return true;}

        const q = searchQuery.toLowerCase();
        return (
            record.movie.title.toLowerCase().includes(q) ||
            record.movie.titleOriginal.toLowerCase().includes(q) ||
            (record.movie.director &&
                record.movie.director.toLowerCase().includes(q)) ||
            (record.movie.actors &&
                record.movie.actors.toLowerCase().includes(q))
        );
    };

    // Memoized rewatch filter
    const rewatchMatchesRecord = (
        record: RecordType,
        filterEnabled: boolean,
        listId: number,
    ): boolean => {
        if (!filterEnabled || listId !== listWatchedId) {return true;}

        return (
            record.rating === 5 &&
            ((!record.options.ultraHd && !record.options.theatre) ||
                !record.options.original) &&
            !record.options.ignoreRewatch
        );
    };

    // Memoized unreleased filter
    const releasedMatchesRecord = (
        record: RecordType,
        filterEnabled: boolean,
        listId: number,
    ): boolean => {
        if (!filterEnabled || listId !== listToWatchId) {return true;}

        return record.movie.isReleased;
    };

    // Memoized recent releases filter
    const recentReleasesMatchesRecord = (
        record: RecordType,
        filterEnabled: boolean,
        listId: number,
    ): boolean => {
        if (!filterEnabled || listId !== listToWatchId) {return true;}

        if (!record.movie.releaseDate || !record.movie.releaseDateTimestamp) {
            return false;
        }

        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
        const movieReleaseDate = new Date(
            record.movie.releaseDateTimestamp * 1000,
        );

        return movieReleaseDate >= sixMonthsAgo;
    };

    // Main filtered records function - returns raw filtered array for caching
    const getFilteredRecords = (filters: {
        toRewatchFilter: Ref<boolean>;
        hideUnreleasedMovies: Ref<boolean>;
        recentReleasesFilter: Ref<boolean>;
    }) => {
        return computed(() => {
            const searchQuery = debouncedQuery.value.trim();
            const listId = currentListId.value;

            const result = records.value.filter((record) => {
                // List filter - must match current list
                if (record.listId !== listId) {return false;}

                // Apply all filters using memoized functions with null safety
                const toRewatchValue = (typeof filters.toRewatchFilter?.value === 'boolean') 
                    ? filters.toRewatchFilter.value 
                    : (typeof filters.toRewatchFilter === 'boolean') 
                        ? filters.toRewatchFilter 
                        : false;
                        
                const hideUnreleasedValue = (typeof filters.hideUnreleasedMovies?.value === 'boolean') 
                    ? filters.hideUnreleasedMovies.value 
                    : (typeof filters.hideUnreleasedMovies === 'boolean') 
                        ? filters.hideUnreleasedMovies 
                        : false;
                        
                const recentReleasesValue = (typeof filters.recentReleasesFilter?.value === 'boolean') 
                    ? filters.recentReleasesFilter.value 
                    : (typeof filters.recentReleasesFilter === 'boolean') 
                        ? filters.recentReleasesFilter 
                        : false;

                return (
                    searchMatchesRecord(record, searchQuery) &&
                    rewatchMatchesRecord(record, toRewatchValue, listId) &&
                    releasedMatchesRecord(
                        record,
                        hideUnreleasedValue,
                        listId,
                    ) &&
                    recentReleasesMatchesRecord(
                        record,
                        recentReleasesValue,
                        listId,
                    )
                );
            });
            
            return result;
        });
    };
    
    // Direct filter function for external caching (non-reactive)
    const filterRecords = (
        recordsArray: RecordType[],
        searchQuery: string,
        listId: number,
        filters: {
            toRewatch: boolean;
            hideUnreleased: boolean;
            recentReleases: boolean;
        }
    ): RecordType[] => {
        return recordsArray.filter((record) => {
            // List filter - must match current list
            if (record.listId !== listId) {return false;}

            return (
                searchMatchesRecord(record, searchQuery.trim()) &&
                rewatchMatchesRecord(record, filters.toRewatch, listId) &&
                releasedMatchesRecord(record, filters.hideUnreleased, listId) &&
                recentReleasesMatchesRecord(record, filters.recentReleases, listId)
            );
        });
    };

    // Memoized count computations
    const getWatchedCount = () => {
        return computed(() => {
            return records.value.filter(
                (record) => record.listId === listWatchedId,
            ).length;
        });
    };

    const getToWatchCount = () => {
        return computed(() => {
            return records.value.filter(
                (record) => record.listId === listToWatchId,
            ).length;
        });
    };

    return {
        query,
        debouncedQuery,
        setQuery,
        getFilteredRecords,
        filterRecords,
        getWatchedCount,
        getToWatchCount,
    };
}
