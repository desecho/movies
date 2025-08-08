import { computed, ref, type Ref } from "vue";
import { cloneDeep } from "lodash";
import type { RecordType } from "../types";
import { listWatchedId } from "../const";

export function useRecordSorting(
  records: Ref<RecordType[]>,
  currentListId: Ref<number>
) {
  const sort = ref("additionDate");

  // Memoized sorting function
  const sortedRecords = computed(() => {
    if (!records.value.length) return [];
    
    const recordsCopy = cloneDeep(records.value);

    switch (sort.value) {
      case "custom":
        return recordsCopy.sort((a, b) => a.order - b.order);
        
      case "releaseDate":
        return recordsCopy.sort((a, b) => 
          b.movie.releaseDateTimestamp - a.movie.releaseDateTimestamp
        );
        
      case "rating":
        if (currentListId.value === listWatchedId) {
          return recordsCopy.sort((a, b) => b.rating - a.rating);
        } else {
          return recordsCopy.sort((a, b) => 
            b.movie.imdbRating - a.movie.imdbRating
          );
        }
        
      default: // additionDate
        return recordsCopy.sort((a, b) => 
          b.additionDate - a.additionDate
        );
    }
  });

  // Pagination utilities
  const getPaginatedRecords = (
    filteredRecords: Ref<RecordType[]>, 
    page: Ref<number>, 
    perPage: number = 50
  ) => {
    const totalPages = computed(() => 
      Math.ceil(filteredRecords.value.length / perPage)
    );

    const paginatedRecords = computed(() => {
      const start = (page.value - 1) * perPage;
      return filteredRecords.value.slice(start, start + perPage);
    });

    return {
      totalPages,
      paginatedRecords,
    };
  };

  return {
    sort,
    sortedRecords,
    getPaginatedRecords,
  };
}