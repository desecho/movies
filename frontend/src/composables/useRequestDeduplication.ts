import { ref } from "vue";

interface RequestCache {
    [key: string]: Promise<unknown>;
}

export function useRequestDeduplication(): {
    deduplicateRequest: <T>(
        key: string,
        requestFn: () => Promise<T>,
    ) => Promise<T>;
    clearCache: () => void;
    isRequestInProgress: (key: string) => boolean;
} {
    const activeRequests = ref<RequestCache>({});

    async function deduplicateRequest<T>(
        key: string,
        requestFn: () => Promise<T>,
    ): Promise<T> {
        // If request is already in progress, return the existing promise
        if (key in activeRequests.value) {
            return activeRequests.value[key] as Promise<T>;
        }

        // Create new request promise
        const requestPromise = requestFn().finally(() => {
            // Clean up the request from cache when it completes
            // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
            delete activeRequests.value[key];
        });

        // Store the promise in cache
        activeRequests.value[key] = requestPromise;

        return requestPromise;
    }

    function clearCache(): void {
        activeRequests.value = {};
    }

    function isRequestInProgress(key: string): boolean {
        return Boolean(activeRequests.value[key]);
    }

    return {
        deduplicateRequest,
        clearCache,
        isRequestInProgress,
    };
}
