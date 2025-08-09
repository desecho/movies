/**
 * @fileoverview Composable for handling async operations with loading states, error handling, and retry logic
 */

import { ref, type Ref } from "vue";

import type { AppError } from "../utils/errorHandling";

import { errorHandlers, handleError } from "../utils/errorHandling";

/**
 * Configuration for async operations
 */
export interface AsyncOperationConfig {
    /** Show loading indicator */
    showLoading?: boolean;
    /** Maximum number of retry attempts */
    maxRetries?: number;
    /** Delay between retries in milliseconds */
    retryDelay?: number;
    /** Context for error reporting */
    context?: string;
    /** Custom error handler */
    errorHandler?: "default" | "silent" | "network" | "api" | "authentication";
    /** Custom success message */
    successMessage?: string;
    /** Whether to show success toast */
    showSuccess?: boolean;
}

/**
 * Result of an async operation
 */
export interface AsyncOperationResult<T> {
    data: T | null;
    error: AppError | null;
    success: boolean;
}

/**
 * Async operation state management
 */
export interface AsyncOperationState {
    isLoading: Ref<boolean>;
    error: Ref<AppError | null>;
    retryCount: Ref<number>;
    isRetrying: Ref<boolean>;
}

/**
 * Composable for managing async operations with comprehensive error handling
 */
export function useAsyncOperation(defaultConfig: AsyncOperationConfig = {}): {
    isLoading: Ref<boolean>;
    error: Ref<AppError | null>;
    retryCount: Ref<number>;
    isRetrying: Ref<boolean>;
    execute: <T>(
        operation: () => Promise<T>,
        config?: AsyncOperationConfig,
    ) => Promise<AsyncOperationResult<T>>;
} {
    const isLoading = ref(false);
    const error = ref<AppError | null>(null);
    const retryCount = ref(0);
    const isRetrying = ref(false);

    const defaultOptions: Required<AsyncOperationConfig> = {
        showLoading: true,
        maxRetries: 3,
        retryDelay: 1000,
        context: "AsyncOperation",
        errorHandler: "default",
        successMessage: "",
        showSuccess: false,
        ...defaultConfig,
    };

    /**
     * Execute an async operation with full error handling and retry logic
     */
    async function execute<T>(
        operation: () => Promise<T>,
        config: AsyncOperationConfig = {},
    ): Promise<AsyncOperationResult<T>> {
        const options = { ...defaultOptions, ...config };

        // Reset state
        if (options.showLoading) {
            isLoading.value = true;
        }
        error.value = null;

        let lastError: unknown;
        let attempt = 0;

        while (attempt <= options.maxRetries) {
            try {
                // eslint-disable-next-line no-await-in-loop
                const result = await operation();

                // Success - reset retry count and return result
                retryCount.value = 0;
                isRetrying.value = false;

                if (options.showLoading) {
                    isLoading.value = false;
                }

                // Show success message if configured
                if (options.showSuccess && options.successMessage) {
                    // Use toast for success (assuming it's available)
                    // eslint-disable-next-line no-await-in-loop
                    const { $toast } = await import("../toast");
                    $toast.success(options.successMessage);
                }

                return {
                    data: result,
                    error: null,
                    success: true,
                };
            } catch (err) {
                lastError = err;
                attempt++;
                retryCount.value = attempt;

                // If we haven't exceeded max retries, wait and try again
                if (attempt <= options.maxRetries) {
                    isRetrying.value = true;

                    console.log(
                        `[AsyncOperation] Retry ${attempt}/${options.maxRetries} after ${options.retryDelay}ms`,
                    );

                    // eslint-disable-next-line no-await-in-loop
                    await new Promise<void>((resolve) => {
                        setTimeout(() => {
                            resolve();
                        }, options.retryDelay);
                    });
                    continue;
                }

                // All retries exhausted - handle the error
                break;
            }
        }

        // Handle the final error
        let appError: AppError;

        switch (options.errorHandler) {
            case "silent":
                appError = errorHandlers.silent(lastError, options.context);
                break;
            case "network":
                appError = errorHandlers.network(lastError, options.context);
                break;
            case "api":
                appError = errorHandlers.api(lastError, options.context);
                break;
            case "authentication":
                appError = errorHandlers.authentication(
                    lastError,
                    options.context,
                );
                break;
            case "default":
            default:
                appError = handleError(lastError, { context: options.context });
        }

        error.value = appError;
        isRetrying.value = false;

        if (options.showLoading) {
            isLoading.value = false;
        }

        return {
            data: null,
            error: appError,
            success: false,
        };
    }

    /**
     * Retry the last failed operation
     */
    async function retry<T>(
        operation: () => Promise<T>,
        config: AsyncOperationConfig = {},
    ): Promise<AsyncOperationResult<T>> {
        console.log("[AsyncOperation] Manual retry triggered");
        retryCount.value = 0; // Reset retry count for manual retry
        return execute(operation, config);
    }

    /**
     * Reset the operation state
     */
    function reset(): void {
        isLoading.value = false;
        error.value = null;
        retryCount.value = 0;
        isRetrying.value = false;
    }

    /**
     * Check if operation can be retried
     */
    function canRetry(): boolean {
        return (
            error.value !== null && retryCount.value < defaultOptions.maxRetries
        );
    }

    return {
        // State
        isLoading,
        error,
        retryCount,
        isRetrying,

        // Methods
        execute,
        retry,
        reset,
        canRetry,

        // Computed helpers
        hasError(): boolean {
            return error.value !== null;
        },
        isIdle(): boolean {
            return (
                !isLoading.value && !isRetrying.value && error.value === null
            );
        },
    };
}

/**
 * Specialized composables for common use cases
 */
export function useApiCall(
    context: string = "API",
): ReturnType<typeof useAsyncOperation> {
    return useAsyncOperation({
        context: `API: ${context}`,
        errorHandler: "api",
        maxRetries: 2,
        retryDelay: 1500,
    });
}

export function useNetworkRequest(
    context: string = "Network",
): ReturnType<typeof useAsyncOperation> {
    return useAsyncOperation({
        context: `Network: ${context}`,
        errorHandler: "network",
        maxRetries: 3,
        retryDelay: 2000,
    });
}

export function useAuthenticatedRequest(
    context: string = "Auth",
): ReturnType<typeof useAsyncOperation> {
    return useAsyncOperation({
        context: `Auth: ${context}`,
        errorHandler: "authentication",
        maxRetries: 1,
        retryDelay: 1000,
    });
}

export function useSilentRequest(
    context: string = "Background",
): ReturnType<typeof useAsyncOperation> {
    return useAsyncOperation({
        context: `Background: ${context}`,
        errorHandler: "silent",
        showLoading: false,
        maxRetries: 2,
        retryDelay: 5000,
    });
}

/**
 * Higher-order function to wrap existing async functions with error handling
 */
export function withErrorHandling<T extends unknown[], R>(
    asyncFn: (...args: T) => Promise<R>,
    config: AsyncOperationConfig = {},
): (...args: T) => Promise<AsyncOperationResult<R>> {
    const operation = useAsyncOperation(config);

    return {
        ...operation,
        async call(...args: T): Promise<AsyncOperationResult<R>> {
            return operation.execute(async () => asyncFn(...args), config);
        },
    };
}
