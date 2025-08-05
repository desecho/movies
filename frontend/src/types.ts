export interface JWTDecoded {
    token_type: string;
    exp: number;
    iat: number;
    jti: string;
    user_id: number;
}

export interface MoviePreview {
    id: number;
    tmdbLink: string;
    releaseDate: string;
    title: string;
    titleOriginal: string;
    poster: string;
    poster2x: string;
    isReleased: boolean;
    hidden: boolean;
}

export interface AddToListFromDbResponseData {
    status: string;
}

export interface Trailer {
    url: string;
    name: string;
}

export interface Movie {
    id: number;
    title: string;
    titleOriginal: string;
    isReleased: boolean;
    posterNormal: string;
    posterBig: string;
    posterSmall: string;
    imdbRating: number;
    releaseDate: string;
    releaseDateTimestamp: number;
    country: string;
    director: string;
    writer: string;
    genre: string;
    actors: string;
    overview: string;
    homepage: string;
    runtime: string;
    imdbUrl: string;
    tmdbUrl: string;
    trailers: Trailer[];
    hasPoster: boolean;
}

export interface Provider {
    logo: string;
    name: string;
}

export interface ProviderRecord {
    tmdbWatchUrl: string;
    provider: Provider;
}

export interface RecordOptions {
    original: boolean;
    extended: boolean;
    theatre: boolean;
    hd: boolean;
    fullHd: boolean;
    ultraHd: boolean;
    ignoreRewatch: boolean;
}

export interface RecordType {
    id: number;
    order: number;
    comment: string;
    commentArea: boolean;
    rating: number;
    providerRecords: ProviderRecord[];
    movie: Movie;
    options: RecordOptions;
    listId: number;
    additionDate: number;
    ratingOriginal: number;
}

export interface SortData {
    id: number;
    order: number;
}

export interface AuthProps {
    userId: number;
    timestamp: number;
    signature: string;
}
