export const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL as string;

// Hardcode list IDs
export const listWatchedId = 1;
export const listToWatchId = 2;

export const starSizeNormal = 35;
export const starSizeMinimal = 15;

// AI Recommendations constants
export const AI_MAX_RECOMMENDATIONS = 10;
export const AI_MIN_RECOMMENDATIONS = 1;
export const AI_MIN_RATING = 0;
export const AI_MAX_RATING = 5;

// Movie genres for AI recommendations
export const MOVIE_GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western",
] as const;
