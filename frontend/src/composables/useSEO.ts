import { useHead } from "@vueuse/head";
import { computed, unref } from "vue";

import type { ComputedRef, MaybeRef } from "vue";

export interface SEOData {
    title?: string;
    description?: string;
    keywords?: string[];
    image?: string;
    url?: string;
    type?: "website" | "article" | "profile";
    author?: string;
    publishedTime?: string;
    modifiedTime?: string;
}

export interface MovieSEO {
    title: string;
    year?: number;
    rating?: number;
    genre?: string[];
    director?: string;
    cast?: string[];
    plot?: string;
    poster?: string;
    runtime?: number;
}

export interface UserProfileSEO {
    username: string;
    displayName?: string;
    bio?: string;
    avatar?: string;
    moviesWatched?: number;
    followersCount?: number;
}

export function useSEO(data: MaybeRef<SEOData>): {
    pageTitle: ComputedRef<string>;
    pageDescription: ComputedRef<string>;
    fullUrl: ComputedRef<string>;
    imageUrl: ComputedRef<string>;
} {
    const seoData = computed(() => unref(data));

    const baseUrl = computed(() => {
        if (typeof window !== "undefined") {
            return window.location.origin;
        }
        return "https://moviemunch.app"; // Fallback for SSR
    });

    const fullUrl = computed(() => {
        const url = seoData.value.url || "";
        return url.startsWith("http") ? url : `${baseUrl.value}${url}`;
    });

    const pageTitle = computed(() => {
        const title = seoData.value.title;
        return title
            ? `${title} | MovieMunch`
            : "MovieMunch - Track Movies, Discover More";
    });

    const pageDescription = computed(
        () =>
            seoData.value.description ||
            "Track what you watch. Discover what to watch next. Join the MovieMunch community for personalized movie recommendations.",
    );

    const keywordsString = computed(() => {
        const baseKeywords = [
            "movies",
            "film",
            "cinema",
            "watch",
            "tracking",
            "recommendations",
        ];
        const customKeywords = seoData.value.keywords || [];
        return [...baseKeywords, ...customKeywords].join(", ");
    });

    const imageUrl = computed(() => {
        const image = seoData.value.image;
        if (!image) {
            return `${baseUrl.value}/img/logo.png`;
        }
        return image.startsWith("http") ? image : `${baseUrl.value}${image}`;
    });

    useHead({
        title: pageTitle,
        meta: [
            { name: "description", content: pageDescription },
            { name: "keywords", content: keywordsString },
            { name: "author", content: seoData.value.author || "MovieMunch" },

            // Open Graph
            { property: "og:type", content: seoData.value.type || "website" },
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

            // Additional meta tags
            { name: "robots", content: "index, follow" },
            {
                name: "viewport",
                content: "width=device-width, initial-scale=1",
            },
            {
                "http-equiv": "Content-Type",
                content: "text/html; charset=UTF-8",
            },
        ],
        link: [
            { rel: "canonical", href: fullUrl },
            { rel: "icon", type: "image/png", href: "/favicon.png" },
        ],
        // Add structured data if provided
        ...(seoData.value.publishedTime && {
            meta: [
                {
                    property: "article:published_time",
                    content: seoData.value.publishedTime,
                },
                ...(seoData.value.modifiedTime
                    ? [
                          {
                              property: "article:modified_time",
                              content: seoData.value.modifiedTime,
                          },
                      ]
                    : []),
            ],
        }),
    });

    return {
        pageTitle,
        pageDescription,
        fullUrl,
        imageUrl,
    };
}

export function useMovieSEO(movie: MaybeRef<MovieSEO>): {
    pageTitle: ComputedRef<string>;
    pageDescription: ComputedRef<string>;
    fullUrl: ComputedRef<string>;
    imageUrl: ComputedRef<string>;
} {
    const movieData = computed(() => unref(movie));

    const seoData = computed<SEOData>(() => {
        const m = movieData.value;
        const yearText = m.year ? ` (${m.year})` : "";
        const ratingText = m.rating ? ` - ${m.rating}/10` : "";

        return {
            title: `${m.title}${yearText}`,
            description:
                m.plot ||
                `Watch ${m.title}${yearText} on MovieMunch. ${m.director ? `Directed by ${m.director}. ` : ""}${m.genre?.length ? `Genres: ${m.genre.join(", ")}. ` : ""}${ratingText}`,
            keywords: [
                m.title.toLowerCase(),
                ...(m.genre || []),
                ...(m.director ? [m.director] : []),
                ...(m.cast?.slice(0, 3) || []),
                ...(m.year ? [m.year.toString()] : []),
            ],
            image: m.poster,
            type: "article",
            author: m.director,
        };
    });

    return useSEO(seoData);
}

export function useUserProfileSEO(user: MaybeRef<UserProfileSEO>): {
    pageTitle: ComputedRef<string>;
    pageDescription: ComputedRef<string>;
    fullUrl: ComputedRef<string>;
    imageUrl: ComputedRef<string>;
} {
    const userData = computed(() => unref(user));

    const seoData = computed<SEOData>(() => {
        const u = userData.value;
        const statsText = u.moviesWatched
            ? ` - ${u.moviesWatched} movies watched`
            : "";
        const followersText = u.followersCount
            ? `, ${u.followersCount} followers`
            : "";

        return {
            title: u.displayName || `@${u.username}`,
            description:
                u.bio ||
                `${u.displayName || `@${u.username}`}'s movie profile on MovieMunch${statsText}${followersText}. Discover their movie taste and get personalized recommendations.`,
            keywords: [
                u.username,
                ...(u.displayName ? [u.displayName] : []),
                "movie profile",
                "film enthusiast",
                "movie recommendations",
            ],
            image: u.avatar,
            type: "profile",
            url: `/users/${u.username}`,
        };
    });

    return useSEO(seoData);
}
