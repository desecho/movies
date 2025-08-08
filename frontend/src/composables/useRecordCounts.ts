/**
 * @fileoverview Composable for record count calculations
 * 
 * Provides reusable count calculations for ListView records:
 * - Total watched movies
 * - Total to-watch movies 
 * - Filtered/displayed records
 * - Performance optimized with null safety
 */

import { computed, type Ref } from 'vue';
import type { RecordType } from '../types';

/**
 * Composable for calculating various record counts
 * @param records - Reactive array of all records
 * @param filteredRecords - Optional pre-filtered records for display count
 * @returns Object with computed count properties
 */
export function useRecordCounts(
  records: Ref<RecordType[]>,
  filteredRecords?: Ref<RecordType[]>
) {
  /**
   * Count of movies in watched list (listId: 1)
   */
  const watchedCount = computed(() => {
    if (!records.value || !Array.isArray(records.value)) return 0;
    return records.value.filter(record => record.listId === 1).length;
  });

  /**
   * Count of movies in to-watch list (listId: 2)
   */
  const toWatchCount = computed(() => {
    if (!records.value || !Array.isArray(records.value)) return 0;
    return records.value.filter(record => record.listId === 2).length;
  });

  /**
   * Total count of all records
   */
  const totalCount = computed(() => {
    if (!records.value || !Array.isArray(records.value)) return 0;
    return records.value.length;
  });

  /**
   * Count of currently filtered/displayed records
   */
  const filteredCount = computed(() => {
    if (!filteredRecords?.value || !Array.isArray(filteredRecords.value)) return 0;
    return filteredRecords.value.length;
  });

  /**
   * Count records by specific list ID
   * @param listId - The list ID to count
   */
  const getCountByListId = (listId: number) => computed(() => {
    if (!records.value || !Array.isArray(records.value)) return 0;
    return records.value.filter(record => record.listId === listId).length;
  });

  /**
   * Count records matching a predicate function
   * @param predicate - Function to test each record
   */
  const getCountByPredicate = (predicate: (record: RecordType) => boolean) => computed(() => {
    if (!records.value || !Array.isArray(records.value)) return 0;
    return records.value.filter(predicate).length;
  });

  return {
    watchedCount,
    toWatchCount,
    totalCount,
    filteredCount,
    getCountByListId,
    getCountByPredicate
  };
}