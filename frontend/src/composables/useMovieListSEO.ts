import { useHead } from "@vueuse/head";
import { computed, unref } from "vue";

import type { RecordType } from "../types";
import type { ComputedRef, MaybeRef } from "vue";

export interface MovieListSEOData {
    listType: "watched" | "to-watch" | "custom";
    username?: string;
    displayName?: string;
    isPublic?: boolean;
    movies: RecordType[];
    totalCount: number;
    userAvatar?: string;
    listDescription?: string;
}

export function useMovieListSEO(data: MaybeRef<MovieListSEOData>): {
    pageTitle: ComputedRef<string>;
    pageDescription: ComputedRef<string>;
    fullUrl: ComputedRef<string>;
    imageUrl: ComputedRef<string>;
} {
    const listData = computed(() => unref(data));

    const baseUrl = computed(() => {
        if (typeof window !== "undefined") {
            return window.location.origin;
        }
        return "https://moviemunch.org";
    });

    const listTypeDisplay = computed(() => {
        const type = listData.value.listType;
        switch (type) {
            case "watched":
                return "Watched Movies";
            case "to-watch":
                return "Watchlist";
            case "custom":
                return "Movie Collection";
            default:
                return "Movie List";
        }
    });

    const fullUrl = computed(() => {
        const d = listData.value;
        if (d.username) {
            const listPath = d.listType === "watched" ? "watched" : "to-watch";
            return `${baseUrl.value}/users/${d.username}/list/${listPath}`;
        }
        return `${baseUrl.value}/list`;
    });

    const pageTitle = computed(() => {
        const d = listData.value;
        const userDisplay =
            d.displayName || (d.username ? `@${d.username}` : "");

        if (d.username && userDisplay) {
            return `${userDisplay}'s ${listTypeDisplay.value} (${d.totalCount} movies) | MovieMunch`;
        }

        return `My ${listTypeDisplay.value} (${d.totalCount} movies) | MovieMunch`;
    });

    const pageDescription = computed(() => {
        const d = listData.value;
        const userDisplay =
            d.displayName || (d.username ? `@${d.username}` : "");

        // Get top movie titles for description
        const topMovies = d.movies
            .slice(0, 5)
            .map((movie) => movie.movie.title)
            .filter(Boolean);

        const moviesText =
            topMovies.length > 0
                ? `Including ${topMovies.slice(0, 3).join(", ")}${topMovies.length > 3 ? " and more" : ""}.`
                : "";

        const baseDesc =
            d.listDescription ||
            `Discover ${d.totalCount} movies in ${userDisplay ? `${userDisplay}'s` : "this"} ${listTypeDisplay.value.toLowerCase()}. ${moviesText}`;

        const actionText =
            d.listType === "watched"
                ? "See what they've watched and get personalized movie recommendations."
                : "Explore their watchlist and find your next great movie to watch.";

        return `${baseDesc} ${d.isPublic && d.username ? actionText : "Track movies, discover more on MovieMunch."}`;
    });

    const keywordsComputed = computed(() => {
        const d = listData.value;
        const baseKeywords = [
            "movie list",
            "film collection",
            d.listType === "watched" ? "watched movies" : "watchlist",
            d.listType === "watched" ? "movie diary" : "movies to watch",
            "movie recommendations",
            "film tracker",
        ];

        // Add movie titles as keywords
        const movieKeywords = d.movies
            .slice(0, 10)
            .map((movie) => movie.movie.title?.toLowerCase())
            .filter(Boolean);

        // Add user-specific keywords
        const userKeywords = d.username
            ? [`${d.username} movies`, `${d.username} ${d.listType}`]
            : [];

        // Add genre keywords from movies
        const genreKeywords = [
            ...new Set(
                d.movies
                    .map((movie) => movie.movie.genre)
                    .filter((genre): genre is string => Boolean(genre))
                    .flatMap((genre) => genre.split(", "))
                    .slice(0, 5),
            ),
        ];

        return [
            ...baseKeywords,
            ...movieKeywords.filter((keyword): keyword is string =>
                Boolean(keyword),
            ),
            ...userKeywords,
            ...genreKeywords,
        ].join(", ");
    });

    const imageUrl = computed(() => {
        const d = listData.value;

        // Use user avatar if available
        if (d.userAvatar && typeof d.userAvatar === "string") {
            return d.userAvatar.startsWith("http")
                ? d.userAvatar
                : `${baseUrl.value}${d.userAvatar}`;
        }

        // Use first movie poster if available
        const firstMovieWithPoster = d.movies.find(
            (movie) => movie.movie.posterPath,
        );
        if (firstMovieWithPoster?.movie.posterPath) {
            return `https://image.tmdb.org/t/p/w500${firstMovieWithPoster.movie.posterPath}`;
        }

        // Fallback to MovieMunch logo
        return `${baseUrl.value}/img/logo.png`;
    });

    useHead({
        title: pageTitle,
        meta: [
            { name: "description", content: pageDescription },
            { name: "keywords", content: keywordsComputed },
            {
                name: "author",
                content:
                    listData.value.displayName ||
                    listData.value.username ||
                    "MovieMunch",
            },

            // Open Graph
            { property: "og:type", content: "website" },
            { property: "og:title", content: pageTitle },
            { property: "og:description", content: pageDescription },
            { property: "og:image", content: imageUrl },
            { property: "og:url", content: fullUrl },
            { property: "og:site_name", content: "MovieMunch" },

            // Twitter Card
            { name: "twitter:card", content: "summary_large_image" },
            { name: "twitter:title", content: pageTitle },
            { name: "twitter:description", content: pageDescription },
            { name: "twitter:image", content: imageUrl },
            { name: "twitter:site", content: "@MovieMunch" },

            // List-specific meta tags
            {
                name: "robots",
                content: listData.value.isPublic
                    ? "index, follow"
                    : "noindex, nofollow",
            },
            { property: "article:section", content: "Movies" },
            { property: "article:tag", content: listTypeDisplay },
            { name: "theme-color", content: "#667eea" },
        ],
        link: [{ rel: "canonical", href: fullUrl }],
    });

    return {
        pageTitle,
        pageDescription,
        fullUrl,
        imageUrl,
    };
}
