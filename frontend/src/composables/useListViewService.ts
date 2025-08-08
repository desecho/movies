/**
 * @fileoverview Composable wrapper for ListView service
 * 
 * Provides a Vue 3 composable interface for the ListView service,
 * making it easy to use in components with proper dependency injection.
 */

import { type Ref } from 'vue';
import type { RecordType } from '../types';
import type { ListViewFilters, SortType } from '../types/listView';
import { 
  createListViewService, 
  type IListViewDependencies, 
  type ListViewServiceConfig 
} from '../services/listViewService';

/**
 * Composable for using ListView service
 * 
 * @param dependencies - Required dependencies for the service
 * @param config - Optional configuration for the service
 * @returns ListView service instance and reactive data
 */
export function useListViewService(
  dependencies: IListViewDependencies,
  config?: ListViewServiceConfig
) {
  // Create service instance
  const service = createListViewService(dependencies, config);

  // Get reactive data from service
  const filteredRecords = service.getFilteredRecords();
  const sortedRecords = service.getSortedRecords();
  const paginatedRecords = service.getPaginatedRecords();
  const totalPages = service.getTotalPages();
  const recordCounts = service.getRecordCounts();
  const paginationInfo = service.getPaginationInfo();
  const navigationHelpers = service.getNavigationHelpers();

  // Service methods
  const clearCaches = () => service.clearCaches();
  const updateConfig = (newConfig: Partial<ListViewServiceConfig>) => 
    service.updateConfig(newConfig);
  const getConfig = () => service.getConfig();

  return {
    // Reactive data
    filteredRecords,
    sortedRecords,
    paginatedRecords,
    totalPages,
    ...recordCounts,
    paginationInfo,
    ...navigationHelpers,
    
    // Service methods
    clearCaches,
    updateConfig,
    getConfig,
    
    // Service instance for advanced usage
    service
  };
}