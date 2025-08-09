import axios from "axios";

import type { AxiosError, AxiosRequestHeaders } from "axios";

import { router } from "./router";
import { useAuthStore } from "./stores/auth";
import { isValidToken } from "./types/common";
import { handleError } from "./utils/errorHandling";

// Keep track of the active interceptors so we can eject them
let responseInterceptorId: number | null = null;
let requestInterceptorId: number | null = null;

// Track token refresh state
let isRefreshingToken = false;

/**
 * Handle 401 authentication errors with automatic token refresh
 */
async function handleAuthenticationError(error: AxiosError): Promise<unknown> {
    const currentAuth = useAuthStore();

    if (!currentAuth.user.isLoggedIn) {
        // User is not logged in, redirect to login
        void router.push("/login");
        throw error;
    }

    const errorData = error.response?.data as {
        code?: string;
        detail?: string;
    };

    // Check if this is a token validation error that can be refreshed
    const isTokenError =
        errorData?.code === "token_not_valid" ||
        errorData?.detail === "Given token not valid for any token type";

    if (!isTokenError) {
        // Not a token error, handle as regular auth error
        handleError(error, {
            context: "Authentication Error",
            showToast: false, // Let the component handle auth errors
        });
        throw error;
    }

    // Handle token refresh with request queuing to prevent multiple refresh attempts
    if (isRefreshingToken) {
        // If already refreshing, wait for it to complete then retry
        try {
            await new Promise((resolve) => {
                function checkRefresh(): void {
                    if (isRefreshingToken) {
                        setTimeout(checkRefresh, 100);
                    } else {
                        resolve(undefined);
                    }
                }
                checkRefresh();
            });

            // Retry the original request
            if (error.config) {
                return axios.request(error.config);
            }
        } catch (refreshError) {
            console.error(
                "[Auth] Error while waiting for token refresh:",
                refreshError,
            );
            throw refreshError;
        }
    }

    // Start token refresh process
    if (!isRefreshingToken) {
        isRefreshingToken = true;
        try {
            await currentAuth.refreshToken();

            // Retry the original request with the new token
            if (error.config) {
                return axios.request(error.config);
            }

            throw error;
        } catch (refreshError) {
            // Token refresh failed, redirect to login
            console.error("[Auth] Token refresh failed:", refreshError);
            currentAuth.logout();
            void router.push("/login");

            throw refreshError;
        } finally {
            // eslint-disable-next-line require-atomic-updates
            isRefreshingToken = false;
        }
    }

    throw error;
}

export function initAxios(): void {
    const headers: AxiosRequestHeaders = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    };

    const auth = useAuthStore();
    if (auth.user.isLoggedIn && isValidToken(auth.user.accessToken)) {
        headers.Authorization = `Bearer ${auth.user.accessToken}`;
    }

    axios.defaults.headers.common = headers;

    // Eject previously registered interceptors to avoid leaks and stale closures
    if (responseInterceptorId !== null) {
        axios.interceptors.response.eject(responseInterceptorId);
        responseInterceptorId = null;
    }
    if (requestInterceptorId !== null) {
        axios.interceptors.request.eject(requestInterceptorId);
        requestInterceptorId = null;
    }

    // Request interceptor for logging and request deduplication
    requestInterceptorId = axios.interceptors.request.use(
        (config) => {
            // Add request ID for tracking
            config.metadata = {
                startTime: Date.now(),
                requestId: Math.random().toString(36).substring(7),
            };

            // Log outgoing requests in development
            if (import.meta.env.DEV) {
                console.log(
                    `[HTTP Request] ${config.method?.toUpperCase()} ${config.url}`,
                );
            }

            return config;
        },
        (error) => {
            console.error("[HTTP Request Error]", error);
            throw new Error(
                error instanceof Error ? error.message : String(error),
            );
        },
    );

    responseInterceptorId = axios.interceptors.response.use(
        (response) => {
            // Log successful requests in development
            if (import.meta.env.DEV) {
                const metadata = response.config.metadata as
                    | { startTime?: number }
                    | undefined;
                const duration = metadata?.startTime
                    ? Date.now() - metadata.startTime
                    : 0;
                console.log(
                    `[HTTP Response] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`,
                );
            }
            return response;
        },
        async (error: AxiosError) => {
            // Log error responses in development
            if (import.meta.env.DEV) {
                const metadata = error.config?.metadata as
                    | { startTime?: number }
                    | undefined;
                const duration = metadata?.startTime
                    ? Date.now() - metadata.startTime
                    : 0;
                console.error(
                    `[HTTP Error] ${error.response?.status} ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
                    error.response?.data,
                );
            }

            // Handle authentication errors with token refresh
            if (error.response?.status === 401) {
                return handleAuthenticationError(error);
            }

            // Handle network errors
            if (
                error.code === "ERR_NETWORK" ||
                error.code === "ERR_CONNECTION_REFUSED"
            ) {
                handleError(error, {
                    context: "Network Error",
                    showToast: false, // Let individual components handle network errors
                });
            }

            // Handle timeout errors
            if (
                error.code === "ECONNABORTED" ||
                error.message.includes("timeout")
            ) {
                handleError(error, {
                    context: "Request Timeout",
                    showToast: false,
                });
            }

            throw error;
        },
    );
}
