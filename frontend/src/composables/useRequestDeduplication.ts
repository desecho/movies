import { ref } from "vue";

interface RequestCache {
  [key: string]: Promise<any>;
}

export function useRequestDeduplication() {
  const activeRequests = ref<RequestCache>({});

  const deduplicateRequest = async <T>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> => {
    // If request is already in progress, return the existing promise
    if (activeRequests.value[key]) {
      return activeRequests.value[key];
    }

    // Create new request promise
    const requestPromise = requestFn().finally(() => {
      // Clean up the request from cache when it completes
      delete activeRequests.value[key];
    });

    // Store the promise in cache
    activeRequests.value[key] = requestPromise;

    return requestPromise;
  };

  const clearCache = () => {
    activeRequests.value = {};
  };

  const isRequestInProgress = (key: string): boolean => {
    return !!activeRequests.value[key];
  };

  return {
    deduplicateRequest,
    clearCache,
    isRequestInProgress,
  };
}