"""TMDB."""

from collections import abc
from datetime import date, datetime, time, timedelta
from typing import Optional
from urllib.parse import urljoin

import requests
import tmdbsimple as tmdb
from django.conf import settings
from sentry_sdk import capture_exception

from ..exceptions import TrailerSiteNotFoundError
from ..types import SearchType, TmdbMovieListResultProcessed, TmdbMovieProcessed, TmdbTrailer, WatchDataRecord
from ..validation import validate_language
from .exceptions import TmdbInvalidSearchTypeError, TmdbNoImdbIdError
from .types import (
    TmdbCast,
    TmdbCombinedCredits,
    TmdbCrew,
    TmdbMovie,
    TmdbMovieListResult,
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
    else:  # size == "big":
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


def _filter_movies_only(entries: list[TmdbCast] | list[TmdbCrew]) -> list[TmdbCast | TmdbCrew]:
    return [e for e in entries if e.get("media_type") == "movie"]


def _get_date(date_str: Optional[str]) -> Optional[date]:
    """Get date."""
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None


def _get_processed_movie_data(
    entries: list[TmdbCast] | list[TmdbCrew] | list[TmdbMovieListResult],
) -> list[TmdbMovieListResultProcessed]:
    """Return processed movie data."""
    movies: list[TmdbMovieListResultProcessed] = []
    for entry in entries:
        movie: TmdbMovieListResultProcessed = {
            "poster_path": _remove_trailing_slash_from_tmdb_poster(entry.get("poster_path")),
            "popularity": entry.get("popularity", 0),
            "id": entry["id"],
            "release_date": _get_date(entry.get("release_date")),
            "title": entry["title"],
            "title_original": entry["original_title"],
        }
        movies.append(movie)
    return movies


def search_movies(query_str: str, search_type: SearchType, lang: str) -> list[TmdbMovieListResultProcessed]:
    """
    Search Movies.

    Searches for movies based on the query string.
    For actor, director search - the first person found is used.
    """
    SEARCH_TYPES = ["movie", "actor", "director"]
    if search_type not in SEARCH_TYPES:
        raise TmdbInvalidSearchTypeError(search_type)

    validate_language(lang)

    query = query_str.encode("utf-8")
    params = {"query": query, "language": lang, "include_adult": settings.INCLUDE_ADULT}
    search = tmdb.Search()
    if search_type == "movie":
        movies: list[TmdbMovieListResult] = search.movie(**params)["results"]
        return _get_processed_movie_data(movies)

    # search_type == "actor" or "director"
    persons: list[TmdbPerson] = search.person(**params)["results"]
    # We only select the first found actor/director.
    if persons:
        person_id = persons[0]["id"]
    else:
        return []
    person = tmdb.People(person_id)
    combined_credits: TmdbCombinedCredits = person.combined_credits(language=lang)
    if search_type == "actor":
        cast_entries: list[TmdbCast] = _filter_movies_only(combined_credits["cast"])  # type: ignore
        movies_processed = _get_processed_movie_data(cast_entries)
    else:  # search_type == "director"
        crew_entries: list[TmdbCrew] = _filter_movies_only(combined_credits["crew"])  # type: ignore
        crew_entries = [e for e in crew_entries if e["job"] == "Director"]
        movies_processed = _get_processed_movie_data(crew_entries)
    return movies_processed


def _is_valid_trailer_site(site: str) -> bool:
    """Return True if trailer site is valid."""
    return site in settings.TRAILER_SITES.keys()


def _get_trailers(tmdb_movie: tmdb.Movies, lang: str) -> list[TmdbTrailer]:
    """Get trailers."""
    trailers = []
    videos = tmdb_movie.videos(language=lang)
    for video in videos["results"]:
        if video.get("type") == "Trailer":
            site = video["site"]
            try:
                if not _is_valid_trailer_site(site):
                    raise TrailerSiteNotFoundError(f"Site - {site}")
            except TrailerSiteNotFoundError as e:
                if settings.DEBUG:  # pragma: no cover
                    raise
                capture_exception(e)
                continue
            trailer: TmdbTrailer = {"name": video.get("name", "Trailer"), "key": video["key"], "site": site}
            trailers.append(trailer)
    return trailers


def get_watch_data(tmdb_id: int) -> list[WatchDataRecord]:
    """Get watch data."""
    watch_data: list[WatchDataRecord] = []
    results: TmdbWatchData = tmdb.Movies(tmdb_id).watch_providers()["results"]
    items: abc.ItemsView[str, TmdbWatchDataCountry] = results.items()  # type: ignore
    for country, data in items:
        if country in settings.PROVIDERS_SUPPORTED_COUNTRIES and "flatrate" in data:
            for provider in data["flatrate"]:
                record = WatchDataRecord(country=country, provider_id=provider["provider_id"])
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
    # movie_info_ru = _get_movie_data(tmdb_movie, lang=settings.LANGUAGE_RU)
    return {
        "tmdb_id": tmdb_id,
        "imdb_id": imdb_id,
        "release_date": release_date,
        "title_original": movie_info_en["original_title"],
        "poster": _remove_trailing_slash_from_tmdb_poster(movie_info_en.get("poster_path")),
        "homepage": movie_info_en.get("homepage"),
        "trailers": _get_trailers(tmdb_movie, lang=settings.LANGUAGE_EN),
        "title": movie_info_en["title"],
        "overview": movie_info_en.get("overview"),
        "runtime": _get_time_from_min(movie_info_en.get("runtime")),
    }


def get_tmdb_providers() -> list[TmdbProvider]:
    """
    Get TMDB providers.

    The functionality is not supported by tmdbsimple so we have to use the API directly.
    """
    params = {"api_key": settings.TMDB_KEY}
    response = requests.get(
        urljoin(settings.TMDB_API_BASE_URL, "watch/providers/movie"), params=params, timeout=settings.REQUESTS_TIMEOUT
    )
    providers: list[TmdbProvider] = response.json()["results"]
    return providers


def get_trending() -> list[TmdbMovieListResultProcessed]:
    """Get trending movies."""
    tmdb_rending = tmdb.Trending(media_type="movie", time_window="week")
    return _get_processed_movie_data(tmdb_rending.info()["results"])
