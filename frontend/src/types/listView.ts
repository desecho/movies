/**
 * ListView-specific types for mode, sorting, and filtering.
 * This module provides comprehensive type definitions for the ListView system,
 * including view modes, sorting options, filters, and component prop interfaces.
 *
 * @fileoverview Type definitions for ListView components and state management
 */

/**
 * Available view modes for displaying movie records
 */
export type ViewMode =
    /** Full detailed view with all movie information */
    | "full"
    /** Compact view with essential information only */
    | "minimal"
    /** Grid-based visual layout showing posters */
    | "gallery"
    /** Reduced size full view */
    | "compact";

/**
 * Available sorting methods for movie records
 */
export type SortType =
    /** Sort by when the movie was added to the list */
    | "additionDate"
    /** Sort by movie release date */
    | "releaseDate"
    /** Sort by user rating (watched) or IMDB rating (to-watch) */
    | "rating"
    /** Custom drag-and-drop ordering */
    | "custom";

/**
 * Filter options for refining the displayed movie list
 */
export interface ListViewFilters {
    /** Show only movies marked for rewatching (watched list only) */
    toRewatch: boolean;
    /** Hide movies that haven't been released yet (to-watch list only) */
    hideUnreleased: boolean;
    /** Show only movies released in the last 6 months (to-watch list only) */
    recentReleases: boolean;
}

/**
 * Complete state representation for ListView functionality
 */
export interface ListViewState {
    /** Current view mode */
    mode: ViewMode;
    /** Current sorting method */
    sort: SortType;
    /** Search query string */
    query: string;
    /** Active filter settings */
    filters: ListViewFilters;
    /** Current page number (1-based) */
    page: number;
}

/**
 * Props for components that need list context information
 */
export interface ListContextProps {
    /** ID of the current list (1 = watched, 2 = to-watch) */
    currentListId: number;
    /** Whether viewing another user's profile */
    isProfileView: boolean;
}

/**
 * Props for components that handle view mode selection
 */
export interface ViewModeProps {
    /** Current view mode */
    mode: ViewMode;
}

/**
 * Props for components that handle sorting functionality
 */
export interface SortProps {
    /** Current sort type */
    sort: SortType;
}
