/**
 * @fileoverview Composable for ListView sorting logic
 * 
 * Provides sorting functionality for ListView records including:
 * - Addition date sorting (default)
 * - Release date sorting
 * - Rating sorting (user rating for watched, IMDB for to-watch)
 * - Custom drag-and-drop ordering
 * - Comprehensive error handling and type safety
 */

import { computed, type Ref } from 'vue';
import type { RecordType } from '../types';
import type { SortType } from '../types/listView';
import { sortCompareFunctions } from '../utils/movieUtils';

/**
 * Composable for sorting ListView records
 * @param filteredRecords - Pre-filtered records to sort
 * @param sortType - Current sort type
 * @param currentListId - Current list ID for context-specific sorting
 * @returns Computed array of sorted records
 */
export function useListViewSorting(
  filteredRecords: Ref<RecordType[]>,
  sortType: Ref<SortType>,
  currentListId: Ref<number>
) {
  // Use shared utility functions for sorting
  const sortByCustomOrder = (records: RecordType[]): RecordType[] => {
    return [...records].sort(sortCompareFunctions.byCustomOrder);
  };

  const sortByReleaseDate = (records: RecordType[]): RecordType[] => {
    return [...records].sort(sortCompareFunctions.byReleaseDate);
  };

  const sortByRating = (records: RecordType[], listId: number): RecordType[] => {
    const sortFn = listId === 1 
      ? sortCompareFunctions.byUserRating 
      : sortCompareFunctions.byImdbRating;
    return [...records].sort(sortFn);
  };

  const sortByAdditionDate = (records: RecordType[]): RecordType[] => {
    return [...records].sort(sortCompareFunctions.byAdditionDate);
  };

  /**
   * Main sorted records computation
   */
  const sortedRecords = computed(() => {
    try {
      if (!filteredRecords.value || !Array.isArray(filteredRecords.value) || filteredRecords.value.length === 0) {
        return [];
      }

      // Create a copy to avoid mutating the original array
      const recordsCopy = [...filteredRecords.value];
      const currentSort = sortType.value;
      const listId = currentListId.value;

      switch (currentSort) {
        case 'custom':
          return sortByCustomOrder(recordsCopy);
        case 'releaseDate':
          return sortByReleaseDate(recordsCopy);
        case 'rating':
          return sortByRating(recordsCopy, listId);
        case 'additionDate':
        default:
          return sortByAdditionDate(recordsCopy);
      }
    } catch (error) {
      console.error('Error in sortedRecords computation:', error);
      return filteredRecords.value || [];
    }
  });

  return {
    sortedRecords,
    // Export individual sorting functions for testing
    sortByCustomOrder,
    sortByReleaseDate,
    sortByRating,
    sortByAdditionDate
  };
}