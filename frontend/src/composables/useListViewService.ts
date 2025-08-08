/**
 * @fileoverview Composable wrapper for ListView service
 *
 * Provides a Vue 3 composable interface for the ListView service,
 * making it easy to use in components with proper dependency injection.
 */

import type { RecordType } from "../types";
import type { ComputedRef } from "vue";


import {
    createListViewService,
    type IListViewDependencies,
    type IListViewService,
    type ListViewServiceConfig,
} from "../services/listViewService";

/**
 * Composable for using ListView service
 *
 * @param dependencies - Required dependencies for the service
 * @param config - Optional configuration for the service
 * @returns ListView service instance and reactive data
 */
export function useListViewService(
    dependencies: IListViewDependencies,
    config?: ListViewServiceConfig,
): {
    [key: string]: unknown;
    filteredRecords: ComputedRef<RecordType[]>;
    sortedRecords: ComputedRef<RecordType[]>;
    paginatedRecords: ComputedRef<RecordType[]>;
    totalPages: ComputedRef<number>;
    paginationInfo: ComputedRef<unknown>;
    clearCaches: () => void;
    updateConfig: (newConfig: Partial<ListViewServiceConfig>) => void;
    getConfig: () => ListViewServiceConfig;
    service: IListViewService;
} {
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
    function clearCaches(): void {
        service.clearCaches();
    }
    function updateConfig(newConfig: Partial<ListViewServiceConfig>): void {
        service.updateConfig(newConfig);
    }
    function getConfig(): ListViewServiceConfig {
        return service.getConfig();
    }

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
        service,
    };
}
