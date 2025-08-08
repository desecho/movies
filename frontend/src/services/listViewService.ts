/**
 * @fileoverview Service layer for ListView operations
 * 
 * Provides a service-based architecture with dependency injection for:
 * - Centralized business logic
 * - Better testability through dependency injection
 * - Separation of concerns between UI and business logic
 * - Consistent error handling and logging
 */

import { computed, type Ref } from 'vue';
import type { RecordType } from '../types';
import type { ListViewFilters, SortType, ViewMode } from '../types/listView';
import { useListViewFiltering } from '../composables/useListViewFiltering';
import { useListViewSorting } from '../composables/useListViewSorting';
import { useListViewPagination } from '../composables/useListViewPagination';

/**
 * Interface for ListView service dependencies
 */
export interface IListViewDependencies {
  records: Ref<RecordType[]>;
  currentListId: Ref<number>;
  searchQuery: Ref<string>;
  filters: Ref<ListViewFilters>;
  sortType: Ref<SortType>;
  currentPage: Ref<number>;
}

/**
 * Interface for ListView service operations
 */
export interface IListViewService {
  getFilteredRecords(): Ref<RecordType[]>;
  getSortedRecords(): Ref<RecordType[]>;
  getPaginatedRecords(): Ref<RecordType[]>;
  getTotalPages(): Ref<number>;
  getRecordCounts(): {
    watchedCount: Ref<number>;
    toWatchCount: Ref<number>;
    filteredCount: Ref<number>;
  };
}

/**
 * Configuration for ListView service
 */
export interface ListViewServiceConfig {
  itemsPerPage?: number;
  enableCaching?: boolean;
  logErrors?: boolean;
}

/**
 * ListView Service implementation
 * 
 * Centralizes all ListView business logic and provides a clean API
 * for components to interact with. Uses dependency injection for
 * better testability and modularity.
 */
export class ListViewService implements IListViewService {
  private dependencies: IListViewDependencies;
  private config: ListViewServiceConfig;
  private filteringService: ReturnType<typeof useListViewFiltering>;
  private sortingService: ReturnType<typeof useListViewSorting>;
  private paginationService: ReturnType<typeof useListViewPagination>;

  constructor(
    dependencies: IListViewDependencies, 
    config: ListViewServiceConfig = {}
  ) {
    this.dependencies = dependencies;
    this.config = {
      itemsPerPage: 50,
      enableCaching: true,
      logErrors: true,
      ...config
    };

    // Initialize services with dependencies
    this.filteringService = useListViewFiltering(
      dependencies.records,
      dependencies.currentListId,
      dependencies.searchQuery,
      dependencies.filters
    );

    this.sortingService = useListViewSorting(
      this.filteringService.filteredRecords,
      dependencies.sortType,
      dependencies.currentListId
    );

    this.paginationService = useListViewPagination(
      this.sortingService.sortedRecords,
      dependencies.currentPage,
      this.config.itemsPerPage
    );

    if (this.config.logErrors) {
      this.setupErrorLogging();
    }
  }

  /**
   * Get filtered records based on current filters
   */
  getFilteredRecords() {
    return this.filteringService.filteredRecords;
  }

  /**
   * Get sorted and filtered records
   */
  getSortedRecords() {
    return this.sortingService.sortedRecords;
  }

  /**
   * Get paginated records (filtered, sorted, and paginated)
   */
  getPaginatedRecords() {
    return this.paginationService.paginatedRecords;
  }

  /**
   * Get total pages for pagination
   */
  getTotalPages() {
    return this.paginationService.totalPages;
  }

  /**
   * Get various record counts for UI display
   */
  getRecordCounts() {
    const { records } = this.dependencies;
    
    return {
      watchedCount: computed(() => {
        return records.value?.filter(record => record.listId === 1).length || 0;
      }),
      toWatchCount: computed(() => {
        return records.value?.filter(record => record.listId === 2).length || 0;
      }),
      filteredCount: computed(() => {
        return this.filteringService.filteredRecords.value?.length || 0;
      })
    };
  }

  /**
   * Get pagination information for UI components
   */
  getPaginationInfo() {
    return this.paginationService.paginationInfo;
  }

  /**
   * Get navigation helpers for pagination
   */
  getNavigationHelpers() {
    return {
      canGoToFirstPage: this.paginationService.canGoToFirstPage,
      canGoToPreviousPage: this.paginationService.canGoToPreviousPage,
      canGoToNextPage: this.paginationService.canGoToNextPage,
      canGoToLastPage: this.paginationService.canGoToLastPage
    };
  }

  /**
   * Clear all caches (useful for data refresh)
   */
  clearCaches() {
    this.paginationService.clearCache();
    if (this.config.logErrors) {
      console.log('ListView service caches cleared');
    }
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<ListViewServiceConfig>) {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get current service configuration
   */
  getConfig(): Readonly<ListViewServiceConfig> {
    return { ...this.config };
  }

  /**
   * Setup error logging for development and debugging
   */
  private setupErrorLogging() {
    // This could be extended to integrate with external logging services
    const originalError = console.error;
    const originalWarn = console.warn;

    console.error = (...args) => {
      if (args[0]?.includes?.('ListView') || args[0]?.includes?.('filteredRecords')) {
        originalError('🔴 ListView Service Error:', ...args);
      } else {
        originalError(...args);
      }
    };

    console.warn = (...args) => {
      if (args[0]?.includes?.('ListView') || args[0]?.includes?.('record')) {
        originalWarn('🟡 ListView Service Warning:', ...args);
      } else {
        originalWarn(...args);
      }
    };
  }
}

/**
 * Factory function to create ListView service with default configuration
 */
export function createListViewService(
  dependencies: IListViewDependencies,
  config?: ListViewServiceConfig
): ListViewService {
  return new ListViewService(dependencies, config);
}

/**
 * Factory function to create ListView service with testing configuration
 */
export function createListViewServiceForTesting(
  dependencies: IListViewDependencies
): ListViewService {
  return new ListViewService(dependencies, {
    itemsPerPage: 10, // Smaller for testing
    enableCaching: false, // Disable caching for predictable tests
    logErrors: false // Disable logging in tests
  });
}