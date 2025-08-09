/**
 * @fileoverview Comprehensive error handling utilities for better user experience
 */

import type { AxiosError } from "axios";

import { $toast } from "../toast";

/**
 * Standard error types that can occur in the application
 */
export enum ErrorType {
    NETWORK = "network",
    AUTHENTICATION = "authentication",
    AUTHORIZATION = "authorization",
    VALIDATION = "validation",
    NOT_FOUND = "not_found",
    SERVER = "server",
    UNKNOWN = "unknown",
}

/**
 * Error severity levels for different handling approaches
 */
export enum ErrorSeverity {
    LOW = "low", // Toast notification
    MEDIUM = "medium", // Toast + console log
    HIGH = "high", // Toast + console error + potential redirect
    CRITICAL = "critical", // Full error boundary + page reload option
}

/**
 * Structured error information
 */
export interface AppError {
    type: ErrorType;
    severity: ErrorSeverity;
    message: string;
    userMessage: string;
    code?: string;
    details?: Record<string, unknown>;
    originalError?: unknown;
    context?: string;
    timestamp: number;
}

/**
 * Error handler configuration
 */
export interface ErrorHandlerConfig {
    showToast?: boolean;
    logToConsole?: boolean;
    reportToService?: boolean;
    context?: string;
    fallbackMessage?: string;
}

/**
 * User-friendly error messages mapped to common error scenarios
 */
const USER_FRIENDLY_MESSAGES: Record<string, string> = {
    // Network errors
    ERR_NETWORK:
        "Unable to connect to server. Please check your internet connection.",
    ERR_CONNECTION_REFUSED:
        "Server is temporarily unavailable. Please try again later.",
    ERR_TIMEOUT: "Request timed out. Please try again.",

    // Authentication errors
    INVALID_CREDENTIALS: "Invalid username or password. Please try again.",
    TOKEN_EXPIRED: "Your session has expired. Please log in again.",
    AUTHENTICATION_REQUIRED: "Please log in to continue.",

    // Authorization errors
    INSUFFICIENT_PERMISSIONS:
        "You don't have permission to perform this action.",
    ACCESS_DENIED:
        "Access denied. Please contact support if you believe this is an error.",

    // Validation errors
    VALIDATION_ERROR: "Please check your input and try again.",
    REQUIRED_FIELD_MISSING: "Please fill in all required fields.",
    INVALID_FORMAT: "Please check the format of your input.",

    // Server errors
    INTERNAL_SERVER_ERROR:
        "Something went wrong on our end. Please try again later.",
    SERVICE_UNAVAILABLE:
        "Service is temporarily unavailable. Please try again later.",
    NOT_FOUND: "The requested resource was not found.",

    // Default messages
    DEFAULT_ERROR: "Something went wrong. Please try again.",
    DEFAULT_NETWORK:
        "Network error. Please check your connection and try again.",
};

/**
 * Determine error type from various error sources
 */
export function determineErrorType(error: unknown): ErrorType {
    if (!error) {
        return ErrorType.UNKNOWN;
    }

    const axiosError = error as AxiosError;
    const status = axiosError.response?.status;
    const code = axiosError.code;

    // Network errors
    if (code === "ERR_NETWORK" || code === "ERR_CONNECTION_REFUSED") {
        return ErrorType.NETWORK;
    }

    // HTTP status code based classification
    if (status) {
        if (status === 401) {
            return ErrorType.AUTHENTICATION;
        }
        if (status === 403) {
            return ErrorType.AUTHORIZATION;
        }
        if (status === 404) {
            return ErrorType.NOT_FOUND;
        }
        if (status >= 400 && status < 500) {
            return ErrorType.VALIDATION;
        }
        if (status >= 500) {
            return ErrorType.SERVER;
        }
    }

    return ErrorType.UNKNOWN;
}

/**
 * Determine error severity based on type and context
 */
export function determineErrorSeverity(
    errorType: ErrorType,
    context?: string,
): ErrorSeverity {
    switch (errorType) {
        case ErrorType.AUTHENTICATION:
            return ErrorSeverity.HIGH;
        case ErrorType.NETWORK:
        case ErrorType.SERVER:
            return ErrorSeverity.MEDIUM;
        case ErrorType.AUTHORIZATION:
            return context === "critical-action"
                ? ErrorSeverity.HIGH
                : ErrorSeverity.MEDIUM;
        case ErrorType.NOT_FOUND:
        case ErrorType.VALIDATION:
            return ErrorSeverity.LOW;
        case ErrorType.UNKNOWN:
        default:
            return ErrorSeverity.MEDIUM;
    }
}

/**
 * Check if a message is suitable for end users (not technical)
 */
function isUserFriendlyMessage(message: string): boolean {
    const technicalIndicators = [
        "stack trace",
        "exception",
        "null pointer",
        "undefined",
        "internal error",
        "database",
        "sql",
        "connection",
        "timeout",
        "traceback",
        "errno",
    ];

    const lowerMessage = message.toLowerCase();
    return !technicalIndicators.some((indicator) =>
        lowerMessage.includes(indicator),
    );
}

/**
 * Extract user-friendly message from error
 */
export function getUserFriendlyMessage(
    error: unknown,
    fallback?: string,
): string {
    const axiosError = error as AxiosError;

    // Try to get specific error message from server response
    const responseData = axiosError.response?.data as {
        detail?: string;
        message?: string;
        error?: string;
        code?: string;
    };

    // Check for specific error codes first
    if (axiosError.code && USER_FRIENDLY_MESSAGES[axiosError.code]) {
        return USER_FRIENDLY_MESSAGES[axiosError.code];
    }

    // Check server response for user-friendly messages
    if (responseData?.detail && isUserFriendlyMessage(responseData.detail)) {
        return responseData.detail;
    }
    if (responseData?.message && isUserFriendlyMessage(responseData.message)) {
        return responseData.message;
    }
    if (responseData?.error && isUserFriendlyMessage(responseData.error)) {
        return responseData.error;
    }

    // Use status-based default messages
    const status = axiosError.response?.status;
    if (status === 401) {
        return USER_FRIENDLY_MESSAGES.INVALID_CREDENTIALS;
    }
    if (status === 403) {
        return USER_FRIENDLY_MESSAGES.ACCESS_DENIED;
    }
    if (status === 404) {
        return USER_FRIENDLY_MESSAGES.NOT_FOUND;
    }
    if (status === 500) {
        return USER_FRIENDLY_MESSAGES.INTERNAL_SERVER_ERROR;
    }
    if (status === 503) {
        return USER_FRIENDLY_MESSAGES.SERVICE_UNAVAILABLE;
    }

    return fallback || USER_FRIENDLY_MESSAGES.DEFAULT_ERROR;
}

/**
 * Create structured AppError from any error source
 */
export function createAppError(
    error: unknown,
    context?: string,
    fallbackMessage?: string,
): AppError {
    const errorType = determineErrorType(error);
    const severity = determineErrorSeverity(errorType, context);
    const userMessage = getUserFriendlyMessage(error, fallbackMessage);

    const axiosError = error as AxiosError;
    const responseData = axiosError.response?.data as { code?: string };

    return {
        type: errorType,
        severity,
        message: axiosError.message || String(error),
        userMessage,
        code: axiosError.code || responseData?.code,
        details: {
            status: axiosError.response?.status,
            url: axiosError.config?.url,
            method: axiosError.config?.method,
        },
        originalError: error,
        context,
        timestamp: Date.now(),
    };
}

/**
 * Main error handler function
 */
export function handleError(
    error: unknown,
    config: ErrorHandlerConfig = {},
): AppError {
    const appError = createAppError(
        error,
        config.context,
        config.fallbackMessage,
    );

    // Default configuration
    const {
        showToast = true,
        logToConsole = true,
        reportToService = false,
    } = config;

    // Console logging based on severity
    if (logToConsole) {
        switch (appError.severity) {
            case ErrorSeverity.CRITICAL:
            case ErrorSeverity.HIGH:
                console.error("[Error Handler]", {
                    message: appError.message,
                    userMessage: appError.userMessage,
                    context: appError.context,
                    details: appError.details,
                    originalError: appError.originalError,
                });
                break;
            case ErrorSeverity.MEDIUM:
                console.warn(
                    "[Error Handler]",
                    appError.userMessage,
                    appError.details,
                );
                break;
            case ErrorSeverity.LOW:
            default:
                console.log("[Error Handler]", appError.userMessage);
        }
    }

    // Toast notification
    if (showToast) {
        switch (appError.severity) {
            case ErrorSeverity.CRITICAL:
                $toast.error(appError.userMessage, { duration: 0 }); // Persistent
                break;
            case ErrorSeverity.HIGH:
                $toast.error(appError.userMessage, { duration: 5000 });
                break;
            case ErrorSeverity.MEDIUM:
                $toast.error(appError.userMessage, { duration: 3000 });
                break;
            case ErrorSeverity.LOW:
            default:
                $toast.error(appError.userMessage, { duration: 2000 });
        }
    }

    // Report to external service (placeholder)
    if (reportToService && appError.severity >= ErrorSeverity.MEDIUM) {
        // TODO: Implement error reporting service integration
        console.log("[Error Reporter] Would report:", appError);
    }

    return appError;
}

/**
 * Specialized handlers for common scenarios
 */
export const errorHandlers = {
    /**
     * Handle authentication errors with automatic redirect
     */
    authentication: (error: unknown, context?: string): AppError => {
        const appError = handleError(error, {
            context: context || "authentication",
        });

        // Redirect to login for auth errors
        if (appError.type === ErrorType.AUTHENTICATION) {
            setTimeout(() => {
                window.location.href = "/login";
            }, 1500);
        }

        return appError;
    },

    /**
     * Handle network errors with retry suggestion
     */
    network: (error: unknown, context?: string): AppError => {
        return handleError(error, {
            context: context || "network",
            fallbackMessage:
                "Network error. Please check your connection and try again.",
        });
    },

    /**
     * Handle API errors with detailed context
     */
    api: (error: unknown, operation: string): AppError => {
        return handleError(error, {
            context: `API: ${operation}`,
            fallbackMessage: `Failed to ${operation}. Please try again.`,
        });
    },

    /**
     * Handle form validation errors
     */
    validation: (error: unknown, formName?: string): AppError => {
        return handleError(error, {
            context: `Form: ${formName || "validation"}`,
            fallbackMessage: "Please check your input and try again.",
        });
    },

    /**
     * Silent error handler (no toast, only logging)
     */
    silent: (error: unknown, context?: string): AppError => {
        return handleError(error, {
            context,
            showToast: false,
            logToConsole: true,
        });
    },
};

/**
 * Error boundary helper for critical errors
 */
export function handleCriticalError(error: unknown, context: string): void {
    const appError = createAppError(error, context);
    appError.severity = ErrorSeverity.CRITICAL;

    console.error("[CRITICAL ERROR]", {
        context,
        error: appError,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
    });

    // Show persistent error message
    $toast.error(
        "A critical error occurred. Please refresh the page or contact support if the problem persists.",
        { duration: 0 },
    );
}
