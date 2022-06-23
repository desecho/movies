"""TMDB."""

from collections import abc
from datetime import date, datetime, time, timedelta
from typing import List, Optional
from urllib.parse import urljoin

import requests
import tmdbsimple as tmdb
from django.conf import settings
from sentry_sdk import capture_exception

from ..exceptions import TrailerSiteNotFoundError
from ..types import SearchType, TmdbMovieProcessed, TmdbMovieSearchResultProcessed, TmdbTrailer, WatchDataRecord
from .exceptions import TmdbNoImdbIdError
from .types import (
    TmdbCast,
    TmdbCombinedCredits,
    TmdbCrew,
    TmdbMovie,
    TmdbMovieSearchResult,
    TmdbPerson,
    TmdbProvider,
    TmdbWatchData,
    TmdbWatchDataCountry,
)

tmdb.API_KEY = settings.TMDB_KEY


def get_tmdb_url(tmdb_id: int) -> str:
    """Get TMDB URL."""
    return f"{settings.TMDB_MOVIE_BASE_URL}{tmdb_id}/"


def get_poster_url(size: str, poster: Optional[str]) -> Optional[str]:
    """Get poster URL."""
    if size == "small":
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == "normal":
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == "big":
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = settings.NO_POSTER_BIG_IMAGE_URL
    if poster is not None:
        return settings.POSTER_BASE_URL + poster_size + "/" + poster
    return no_image_url


def _remove_trailing_slash_from_tmdb_poster(poster: Optional[str]) -> Optional[str]:
    """Remove trailing slash from TMDB poster."""
    if poster:
        return poster[1:]
    return None


def _filter_movies_only(entries: List[TmdbCast] | List[TmdbCrew]) -> List[TmdbCast | TmdbCrew]:
    return [e for e in entries if e.get("media_type") == "movie"]


def _get_date(date_str: Optional[str]) -> Optional[date]:
    """Get date."""
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None


def _get_processed_movie_data(
    entries: List[TmdbCast] | List[TmdbCrew] | List[TmdbMovieSearchResult],
) -> List[TmdbMovieSearchResultProcessed]:
    """Return processed movie data."""
    movies: List[TmdbMovieSearchResultProcessed] = []
    for entry in entries:
        movie: TmdbMovieSearchResultProcessed = {
            "poster_path": _remove_trailing_slash_from_tmdb_poster(entry.get("poster_path")),
            "popularity": entry.get("popularity", 0),
            "id": entry["id"],
            "release_date": _get_date(entry.get("release_date")),
            "title": entry["title"],
        }
        movies.append(movie)
    return movies


def search_movies(query_str: str, search_type: SearchType, lang: str) -> List[TmdbMovieSearchResultProcessed]:
    """
    Search Movies.

    Searches for movies based on the query string.
    For actor, director search - the first person found is used.
    """
    query = query_str.encode("utf-8")
    params = {"query": query, "language": lang, "include_adult": settings.INCLUDE_ADULT}
    search = tmdb.Search()
    if search_type == "movie":
        movies: List[TmdbMovieSearchResult] = search.movie(**params)["results"]
        movies_processed = _get_processed_movie_data(movies)
    else:  # search_type == "actor" or "director"
        persons: List[TmdbPerson] = search.person(**params)["results"]
        # We only select the first found actor/director.
        if persons:
            person_id = persons[0]["id"]
        else:
            return []
        person = tmdb.People(person_id)
        combined_credits: TmdbCombinedCredits = person.combined_credits(language=lang)
        if search_type == "actor":
            cast_entries: List[TmdbCast] = _filter_movies_only(combined_credits["cast"])  # type: ignore
            movies_processed = _get_processed_movie_data(cast_entries)
        else:  # search_type == "director"
            crew_entries: List[TmdbCrew] = _filter_movies_only(combined_credits["crew"])  # type: ignore
            crew_entries = [e for e in crew_entries if e["job"] == "Director"]
            movies_processed = _get_processed_movie_data(crew_entries)
    return movies_processed


def _is_valid_trailer_site(site: str) -> bool:
    """Return True if trailer site is valid."""
    return site in settings.TRAILER_SITES.keys()


def _get_trailers(tmdb_movie: tmdb.Movies, lang: str) -> List[TmdbTrailer]:
    """Get trailers."""
    trailers = []
    for video in tmdb_movie.videos(language=lang)["results"]:
        if video.get("type") == "Trailer":
            site = video["site"]
            try:
                if not _is_valid_trailer_site(site):
                    raise TrailerSiteNotFoundError(f"Site - {site}")
            except TrailerSiteNotFoundError as e:
                if settings.DEBUG:
                    raise
                capture_exception(e)
                continue
            trailer: TmdbTrailer = {"name": video.get("name", "Trailer"), "key": video["key"], "site": site}
            trailers.append(trailer)
    return trailers


def get_watch_data(tmdb_id: int) -> List[WatchDataRecord]:
    """Get watch data."""
    watch_data: List[WatchDataRecord] = []
    results: TmdbWatchData = tmdb.Movies(tmdb_id).watch_providers()["results"]
    items: abc.ItemsView[str, TmdbWatchDataCountry] = results.items()  # type: ignore
    for country, data in items:
        if country in settings.PROVIDERS_SUPPORTED_COUNTRIES and "flatrate" in data:
            for provider in data["flatrate"]:
                record: WatchDataRecord = {"country": country, "provider_id": provider["provider_id"]}
                watch_data.append(record)
    return watch_data


def _get_movie_data(tmdb_movie: tmdb.Movies, lang: str) -> TmdbMovie:
    """Get movie data."""
    movie: TmdbMovie = tmdb_movie.info(language=lang)
    return movie


def _get_time_from_min(minutes: Optional[int]) -> Optional[time]:
    if minutes:
        return (datetime(1900, 1, 1) + timedelta(minutes=minutes)).time()
    return None


def get_tmdb_movie_data(tmdb_id: int) -> TmdbMovieProcessed:
    """Get TMDB movie data."""
    tmdb_movie = tmdb.Movies(tmdb_id)
    movie_info_en = _get_movie_data(tmdb_movie, lang=settings.LANGUAGE_EN)
    imdb_id = movie_info_en.get("imdb_id")
    # Fail early if the IMDb ID is not found.
    if not imdb_id:
        raise TmdbNoImdbIdError(tmdb_id)
    release_date = _get_date(movie_info_en.get("release_date"))
    movie_info_ru = _get_movie_data(tmdb_movie, lang=settings.LANGUAGE_RU)
    return {
        "tmdb_id": tmdb_id,
        "imdb_id": imdb_id,
        "release_date": release_date,
        "title_original": movie_info_en["original_title"],
        "poster_ru": _remove_trailing_slash_from_tmdb_poster(movie_info_ru.get("poster_path")),
        "poster_en": _remove_trailing_slash_from_tmdb_poster(movie_info_en.get("poster_path")),
        "homepage": movie_info_en.get("homepage"),
        "trailers_en": _get_trailers(tmdb_movie, lang=settings.LANGUAGE_EN),
        "trailers_ru": _get_trailers(tmdb_movie, lang=settings.LANGUAGE_RU),
        "title_en": movie_info_en["title"],
        "title_ru": movie_info_ru["title"],
        "overview_en": movie_info_en.get("overview"),
        "overview_ru": movie_info_ru.get("overview"),
        "runtime": _get_time_from_min(movie_info_en.get("runtime")),
    }


def get_tmdb_providers() -> List[TmdbProvider]:
    """
    Get TMDB providers.

    The functionality is not supported by tmdbsimple so we have to use the API directly.
    """
    params = {"api_key": settings.TMDB_KEY}
    response = requests.get(urljoin(settings.TMDB_API_BASE_URL, "watch/providers/movie"), params=params)
    providers: List[TmdbProvider] = response.json()["results"]
    return providers
