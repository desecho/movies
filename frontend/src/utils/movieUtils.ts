/**
 * @fileoverview Shared utility functions for movie operations
 *
 * Provides reusable functions for:
 * - Movie data validation
 * - Date handling and validation
 * - Text search utilities
 * - Rating calculations
 * - Type guards and validation
 */

import type { RecordType } from "../types";

/**
 * Type guard to validate RecordType structure
 */
export function isValidRecord(record: unknown): record is RecordType {
    return (
        record &&
        typeof record === "object" &&
        record !== null &&
        "movie" in record &&
        "listId" in record &&
        "id" in record &&
        typeof (record as RecordType).listId === "number" &&
        typeof (record as RecordType).movie?.title === "string" &&
        (record as RecordType).id !== undefined
    );
}

/**
 * Type guard to validate movie structure within a record
 */
export function hasValidMovie(record: RecordType): boolean {
    return (
        record.movie &&
        typeof record.movie.title === "string" &&
        typeof record.movie.titleOriginal === "string"
    );
}

/**
 * Safe number extraction with fallback
 */
export function safeNumber(value: unknown, fallback = 0): number {
    return typeof value === "number" && !isNaN(value) ? value : fallback;
}

/**
 * Safe string extraction with fallback
 */
export function safeString(value: unknown, fallback = ""): string {
    return typeof value === "string" ? value : fallback;
}

/**
 * Safe boolean extraction with fallback
 */
export function safeBoolean(value: unknown, fallback = false): boolean {
    return typeof value === "boolean" ? value : fallback;
}

/**
 * Create a normalized search string from movie data
 */
export function createSearchString(record: RecordType): string {
    if (!hasValidMovie(record)) {
        return "";
    }

    const parts = [
        safeString(record.movie.title),
        safeString(record.movie.titleOriginal),
        safeString(record.movie.director),
        safeString(record.movie.actors),
    ];

    return parts.filter(Boolean).join(" ").toLowerCase();
}

/**
 * Check if a search query matches a record
 */
export function matchesSearchQuery(record: RecordType, query: string): boolean {
    if (!query.trim()) {
        return true;
    }
    if (!hasValidMovie(record)) {
        return false;
    }

    const searchString = createSearchString(record);
    const normalizedQuery = query.toLowerCase().trim();

    return searchString.includes(normalizedQuery);
}

/**
 * Validate and create Date object from timestamp
 */
export function createDateFromTimestamp(timestamp: unknown): Date | null {
    const ts = safeNumber(timestamp, 0);
    if (ts <= 0) {
        return null;
    }

    try {
        const date = new Date(ts * 1000);
        return isNaN(date.getTime()) ? null : date;
    } catch {
        return null;
    }
}

/**
 * Check if a date is within the last N months
 */
export function isRecentRelease(timestamp: unknown, monthsBack = 6): boolean {
    const releaseDate = createDateFromTimestamp(timestamp);
    if (!releaseDate) {
        return false;
    }

    const cutoffDate = new Date();
    cutoffDate.setMonth(cutoffDate.getMonth() - monthsBack);

    return releaseDate >= cutoffDate;
}

/**
 * Get user rating or fallback to 0
 */
export function getUserRating(record: RecordType): number {
    return safeNumber(record.rating, 0);
}

/**
 * Get IMDB rating or fallback to 0
 */
export function getImdbRating(record: RecordType): number {
    return safeNumber(record.movie?.imdbRating, 0);
}

/**
 * Get custom order or fallback to 0
 */
export function getCustomOrder(record: RecordType): number {
    return safeNumber(record.order, 0);
}

/**
 * Get addition date timestamp or fallback to 0
 */
export function getAdditionDate(record: RecordType): number {
    return safeNumber(record.additionDate, 0);
}

/**
 * Get release date timestamp or fallback to 0
 */
export function getReleaseDate(record: RecordType): number {
    return safeNumber(record.movie?.releaseDateTimestamp, 0);
}

/**
 * Check if movie is released
 */
export function isMovieReleased(record: RecordType): boolean {
    return safeBoolean(record.movie?.isReleased, false);
}

/**
 * Check if record has valid options structure
 */
export function hasValidOptions(record: RecordType): boolean {
    return record.options && typeof record.options === "object";
}

/**
 * Check if record matches rewatch criteria
 * - Rating is 5 stars
 * - Either not in ultra HD/theatre OR not original version
 * - Not marked to ignore rewatch
 */
export function matchesRewatchCriteria(record: RecordType): boolean {
    if (!hasValidOptions(record)) {
        return false;
    }

    const rating = getUserRating(record);
    const options = record.options;

    return (
        rating === 5 &&
        ((!options.ultraHd && !options.theatre) || !options.original) &&
        !options.ignoreRewatch
    );
}

/**
 * Sorting comparison functions
 */
export const sortCompareFunctions = {
    /**
     * Compare by addition date (descending)
     */
    byAdditionDate(a: RecordType, b: RecordType): number {
        return getAdditionDate(b) - getAdditionDate(a);
    },

    /**
     * Compare by release date (descending)
     */
    byReleaseDate(a: RecordType, b: RecordType): number {
        return getReleaseDate(b) - getReleaseDate(a);
    },

    /**
     * Compare by user rating (descending)
     */
    byUserRating(a: RecordType, b: RecordType): number {
        return getUserRating(b) - getUserRating(a);
    },

    /**
     * Compare by IMDB rating (descending)
     */
    byImdbRating(a: RecordType, b: RecordType): number {
        return getImdbRating(b) - getImdbRating(a);
    },

    /**
     * Compare by custom order (ascending)
     */
    byCustomOrder(a: RecordType, b: RecordType): number {
        return getCustomOrder(a) - getCustomOrder(b);
    },
};

/**
 * Filter predicate functions
 */
export const filterPredicates = {
    /**
     * Filter by list ID
     */
    byListId:
        (listId: number) =>
        (record: RecordType): boolean => {
            return record.listId === listId;
        },

    /**
     * Filter by search query
     */
    bySearchQuery:
        (query: string) =>
        (record: RecordType): boolean => {
            return matchesSearchQuery(record, query);
        },

    /**
     * Filter for rewatch candidates (watched list only)
     */
    forRewatch:
        (listId: number) =>
        (record: RecordType): boolean => {
            return listId !== 1 || matchesRewatchCriteria(record);
        },

    /**
     * Filter out unreleased movies (to-watch list only)
     */
    hideUnreleased:
        (listId: number) =>
        (record: RecordType): boolean => {
            return listId !== 2 || isMovieReleased(record);
        },

    /**
     * Filter for recent releases (to-watch list only)
     */
    recentReleases:
        (listId: number, monthsBack = 6) =>
        (record: RecordType): boolean => {
            return (
                listId !== 2 ||
                isRecentRelease(record.movie?.releaseDateTimestamp, monthsBack)
            );
        },
};
