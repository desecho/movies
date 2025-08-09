/**
 * @fileoverview Common type utilities for safe type conversion and validation
 */

/**
 * Safely parse a value as a number with fallback
 */
export function parseNumber(value: unknown, fallback = 0): number {
    if (typeof value === "number" && !isNaN(value)) {
        return value;
    }

    if (typeof value === "string") {
        const parsed = Number(value);
        return isNaN(parsed) ? fallback : parsed;
    }

    return fallback;
}

/**
 * Safely parse a value as a string with fallback
 */
export function parseString(value: unknown, fallback = ""): string {
    if (typeof value === "string") {
        return value;
    }

    if (value !== null && value !== undefined) {
        if (typeof value === "object") {
            // Handle objects safely
            if (Array.isArray(value)) {
                return value.join(",");
            }
            // For other objects, return a safe default
            return "[object]";
        }
        if (typeof value === "number" || typeof value === "boolean") {
            return String(value);
        }
        // For any other type, return the fallback
        return fallback;
    }

    return fallback;
}

/**
 * Safely parse a value as a boolean with fallback
 */
export function parseBoolean(value: unknown, fallback = false): boolean {
    if (typeof value === "boolean") {
        return value;
    }

    if (typeof value === "string") {
        const lower = value.toLowerCase();
        return lower === "true" || lower === "1" || lower === "yes";
    }

    if (typeof value === "number") {
        return value !== 0;
    }

    return fallback;
}

/**
 * Type guard to check if a value is a non-empty string
 */
export function isNonEmptyString(value: unknown): value is string {
    return typeof value === "string" && value.length > 0;
}

/**
 * Type guard to check if a value is a valid number
 */
export function isValidNumber(value: unknown): value is number {
    return typeof value === "number" && !isNaN(value) && isFinite(value);
}

/**
 * Safely extract query parameter as number
 */
export function getQueryParamAsNumber(
    param: string | string[] | undefined,
    fallback = 0,
): number {
    if (Array.isArray(param)) {
        return parseNumber(param[0], fallback);
    }
    return parseNumber(param, fallback);
}

/**
 * Safely extract query parameter as string
 */
export function getQueryParamAsString(
    param: string | string[] | undefined,
    fallback = "",
): string {
    if (Array.isArray(param)) {
        return parseString(param[0], fallback);
    }
    return parseString(param, fallback);
}

/**
 * Check if a token string is valid (non-empty and reasonable length)
 */
export function isValidToken(token: unknown): token is string {
    return isNonEmptyString(token) && token.length > 10;
}

/**
 * Safe array type guard
 */
export function isArray<T>(value: unknown): value is T[] {
    return Array.isArray(value);
}

/**
 * Check if an object has a specific property with type checking
 */
export function hasProperty<
    T extends object,
    K extends string | number | symbol,
>(obj: T, prop: K): obj is T & Record<K, unknown> {
    return obj && typeof obj === "object" && prop in obj;
}

/**
 * Type-safe object property getter with fallback
 */
export function getProperty<T, K extends keyof T>(
    obj: T,
    key: K,
    fallback: T[K],
): T[K] {
    if (obj && typeof obj === "object" && key in obj) {
        const value = obj[key];
        return value === undefined ? fallback : value;
    }
    return fallback;
}
