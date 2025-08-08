/**
 * @fileoverview Composable for ListView pagination logic
 * 
 * Provides pagination functionality including:
 * - Page calculation and bounds validation
 * - Memoized record slicing for performance
 * - Error handling for edge cases
 * - Configurable items per page
 */

import { computed, ref, type Ref } from 'vue';
import type { RecordType } from '../types';

/**
 * Composable for paginating ListView records
 * @param sortedRecords - Pre-sorted records to paginate
 * @param currentPage - Current page number (1-based)
 * @param itemsPerPage - Number of items per page (default: 50)
 * @returns Pagination utilities and paginated records
 */
export function useListViewPagination(
  sortedRecords: Ref<RecordType[]>,
  currentPage: Ref<number>,
  itemsPerPage = 50
) {
  /**
   * Performance optimization: Cache pagination results to avoid unnecessary recalculations
   */
  let lastPageValue = 0;
  let lastRecordsLength = 0;
  let cachedPaginatedRecords: RecordType[] = [];

  /**
   * Calculate total pages with error handling
   */
  const totalPages = computed(() => {
    try {
      const recordsLength = sortedRecords.value?.length || 0;
      if (recordsLength === 0) return 1;
      const pages = Math.ceil(recordsLength / itemsPerPage);
      return pages > 0 ? pages : 1;
    } catch (error) {
      console.warn('Error calculating total pages:', error);
      return 1;
    }
  });

  /**
   * Validate and clamp page number to valid range
   */
  const validatedPage = computed(() => {
    const page = currentPage.value || 1;
    const total = totalPages.value;
    return Math.max(1, Math.min(page, total));
  });

  /**
   * Get paginated records with memoization for performance
   */
  const paginatedRecords = computed(() => {
    try {
      const currentRecords = sortedRecords.value || [];
      const page = validatedPage.value;
      
      // Use cache if page and records haven't changed
      if (page === lastPageValue && currentRecords.length === lastRecordsLength) {
        return cachedPaginatedRecords;
      }
      
      // Validate pagination bounds
      const start = Math.max(0, (page - 1) * itemsPerPage);
      const end = Math.min(currentRecords.length, start + itemsPerPage);
      const result = currentRecords.slice(start, end);
      
      // Update cache
      lastPageValue = page;
      lastRecordsLength = currentRecords.length;
      cachedPaginatedRecords = result;
      
      return result;
    } catch (error) {
      console.error('Error in paginatedRecords computation:', error);
      return cachedPaginatedRecords || [];
    }
  });

  /**
   * Pagination info for UI components
   */
  const paginationInfo = computed(() => ({
    currentPage: validatedPage.value,
    totalPages: totalPages.value,
    totalItems: sortedRecords.value?.length || 0,
    itemsPerPage,
    startItem: Math.max(1, (validatedPage.value - 1) * itemsPerPage + 1),
    endItem: Math.min(
      sortedRecords.value?.length || 0,
      validatedPage.value * itemsPerPage
    )
  }));

  /**
   * Navigation helpers
   */
  const canGoToFirstPage = computed(() => validatedPage.value > 1);
  const canGoToPreviousPage = computed(() => validatedPage.value > 1);
  const canGoToNextPage = computed(() => validatedPage.value < totalPages.value);
  const canGoToLastPage = computed(() => validatedPage.value < totalPages.value);

  /**
   * Clear pagination cache (useful when records change significantly)
   */
  const clearCache = () => {
    lastPageValue = 0;
    lastRecordsLength = 0;
    cachedPaginatedRecords = [];
  };

  return {
    // Computed properties
    totalPages,
    validatedPage,
    paginatedRecords,
    paginationInfo,
    
    // Navigation helpers
    canGoToFirstPage,
    canGoToPreviousPage, 
    canGoToNextPage,
    canGoToLastPage,
    
    // Utilities
    clearCache
  };
}