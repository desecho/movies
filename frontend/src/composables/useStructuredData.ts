import { useHead } from "@vueuse/head";
import { computed, unref } from "vue";

import type { ComputedRef, MaybeRef } from "vue";

export interface MovieStructuredData {
    title: string;
    year?: number;
    rating?: number;
    genre?: string[];
    director?: string;
    cast?: string[];
    plot?: string;
    poster?: string;
    runtime?: number;
    datePublished?: string;
    contentRating?: string;
}

export interface PersonStructuredData {
    name: string;
    jobTitle?: string;
    image?: string;
    description?: string;
    sameAs?: string[];
}

export interface OrganizationStructuredData {
    name: string;
    description: string;
    url: string;
    logo: string;
    sameAs: string[];
}

export function useMovieStructuredData(movie: MaybeRef<MovieStructuredData>): {
    structuredData: ComputedRef<Record<string, unknown>>;
} {
    const movieData = computed(() => unref(movie));

    const structuredData = computed(() => {
        const m = movieData.value;

        const schema: Record<string, unknown> = {
            "@context": "https://schema.org",
            "@type": "Movie",
            name: m.title,
            ...(m.plot && { description: m.plot }),
            ...(m.year && { dateCreated: m.year.toString() }),
            ...(m.datePublished && { datePublished: m.datePublished }),
            ...(m.runtime && { duration: `PT${m.runtime}M` }),
            ...(m.contentRating && { contentRating: m.contentRating }),
            ...(m.poster && {
                image: {
                    "@type": "ImageObject",
                    url: m.poster,
                },
            }),
            ...(m.genre && m.genre.length > 0 && { genre: m.genre }),
            ...(m.director && {
                director: {
                    "@type": "Person",
                    name: m.director,
                },
            }),
            ...(m.cast &&
                m.cast.length > 0 && {
                    actor: m.cast.map((actor) => ({
                        "@type": "Person",
                        name: actor,
                    })),
                }),
            ...(m.rating && {
                aggregateRating: {
                    "@type": "AggregateRating",
                    ratingValue: m.rating,
                    ratingCount: 1,
                    bestRating: 10,
                    worstRating: 1,
                },
            }),
        };

        return schema;
    });

    useHead({
        script: [
            {
                type: "application/ld+json",
                children: JSON.stringify(structuredData.value),
            },
        ],
    });

    return { structuredData };
}

export function usePersonStructuredData(
    person: MaybeRef<PersonStructuredData>,
): {
    structuredData: ComputedRef<Record<string, unknown>>;
} {
    const personData = computed(() => unref(person));

    const structuredData = computed(() => {
        const p = personData.value;

        return {
            "@context": "https://schema.org",
            "@type": "Person",
            name: p.name,
            ...(p.jobTitle && { jobTitle: p.jobTitle }),
            ...(p.image && {
                image: {
                    "@type": "ImageObject",
                    url: p.image,
                },
            }),
            ...(p.description && { description: p.description }),
            ...(p.sameAs && p.sameAs.length > 0 && { sameAs: p.sameAs }),
        };
    });

    useHead({
        script: [
            {
                type: "application/ld+json",
                children: JSON.stringify(structuredData.value),
            },
        ],
    });

    return { structuredData };
}

export function useOrganizationStructuredData(
    org: MaybeRef<OrganizationStructuredData>,
): {
    structuredData: ComputedRef<Record<string, unknown>>;
} {
    const orgData = computed(() => unref(org));

    const structuredData = computed(() => {
        const o = orgData.value;

        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            name: o.name,
            description: o.description,
            url: o.url,
            logo: {
                "@type": "ImageObject",
                url: o.logo,
            },
            sameAs: o.sameAs,
        };
    });

    useHead({
        script: [
            {
                type: "application/ld+json",
                children: JSON.stringify(structuredData.value),
            },
        ],
    });

    return { structuredData };
}

export function useBreadcrumbStructuredData(
    breadcrumbs: MaybeRef<Array<{ name: string; url: string }>>,
): {
    structuredData: ComputedRef<Record<string, unknown>>;
} {
    const breadcrumbData = computed(() => unref(breadcrumbs));

    const structuredData = computed(() => ({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: breadcrumbData.value.map((item, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: item.name,
            item: item.url.startsWith("http")
                ? item.url
                : `${window?.location?.origin || ""}${item.url}`,
        })),
    }));

    useHead({
        script: [
            {
                type: "application/ld+json",
                children: JSON.stringify(structuredData.value),
            },
        ],
    });

    return { structuredData };
}

export interface MovieListItem {
    title: string;
    year?: number;
    genre?: string[];
    director?: string;
    poster?: string;
    rating?: number;
    url?: string;
}

export interface MovieListStructuredData {
    name: string;
    description: string;
    numberOfItems: number;
    movies: MovieListItem[];
    author?: {
        name: string;
        url?: string;
        image?: string;
    };
    url?: string;
    dateCreated?: string;
    dateModified?: string;
}

export function useMovieListStructuredData(
    listData: MaybeRef<MovieListStructuredData>,
): {
    structuredData: ComputedRef<Record<string, unknown>>;
} {
    const movieListData = computed(() => unref(listData));

    const structuredData = computed(() => {
        const data = movieListData.value;

        const schema: Record<string, unknown> = {
            "@context": "https://schema.org",
            "@type": ["ItemList", "CreativeWork"],
            name: data.name,
            description: data.description,
            numberOfItems: data.numberOfItems,
            ...(data.url && { url: data.url }),
            ...(data.dateCreated && { dateCreated: data.dateCreated }),
            ...(data.dateModified && { dateModified: data.dateModified }),
            ...(data.author && {
                author: {
                    "@type": "Person",
                    name: data.author.name,
                    ...(data.author.url && { url: data.author.url }),
                    ...(data.author.image && {
                        image: {
                            "@type": "ImageObject",
                            url: data.author.image,
                        },
                    }),
                },
            }),
            itemListElement: data.movies.map((movie, index) => ({
                "@type": "ListItem",
                position: index + 1,
                item: {
                    "@type": "Movie",
                    name: movie.title,
                    ...(movie.year && { dateCreated: movie.year.toString() }),
                    ...(movie.genre &&
                        movie.genre.length > 0 && { genre: movie.genre }),
                    ...(movie.director && {
                        director: {
                            "@type": "Person",
                            name: movie.director,
                        },
                    }),
                    ...(movie.poster && {
                        image: {
                            "@type": "ImageObject",
                            url: movie.poster,
                        },
                    }),
                    ...(movie.rating && {
                        aggregateRating: {
                            "@type": "AggregateRating",
                            ratingValue: movie.rating,
                            ratingCount: 1,
                            bestRating: 10,
                            worstRating: 1,
                        },
                    }),
                    ...(movie.url && { url: movie.url }),
                },
            })),
        };

        return schema;
    });

    useHead({
        script: [
            {
                type: "application/ld+json",
                children: JSON.stringify(structuredData.value),
            },
        ],
    });

    return { structuredData };
}
