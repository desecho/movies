"""TMDB."""
from collections import abc
from datetime import date, datetime
from operator import itemgetter
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
import tmdbsimple as tmdb
from babel.dates import format_date
from django.conf import settings
from sentry_sdk import capture_exception
from tmdbsimple import Movies

from .exceptions import TrailerSiteNotFoundError
from .types import ProvidersTmdb, WatchData, WatchDataCountryTmdb, WatchDataRecord, WatchDataTmdb

tmdb.API_KEY = settings.TMDB_KEY


class TmdbNoImdbIdError(Exception):
    """TMDB no IMDb ID error."""


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


def _get_poster_from_tmdb(poster: str) -> Optional[str]:
    """Get poster from TMDB."""
    if poster:
        return poster[1:]
    return None


def _get_date(date_str: str, lang: str) -> Optional[str]:
    """Get date."""
    if date_str:
        date_ = datetime.strptime(date_str, "%Y-%m-%d")
        if date_:
            date_str = format_date(date_, locale=lang)
            return date_str
    return None


def _set_proper_date(movies: List[Dict[str, Any]], lang: str) -> List[Dict[str, Any]]:
    """Set proper date."""
    for movie in movies:
        movie["releaseDate"] = _get_date(movie["releaseDate"], lang)
    return movies


def _is_popular_movie(popularity: float) -> bool:
    """Return True if movie is popular."""
    return popularity >= settings.MIN_POPULARITY


def _sort_by_date(movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort movies by date."""
    movies_with_date = []
    movies_without_date = []
    for movie in movies:
        if movie["releaseDate"]:
            movies_with_date.append(movie)
        else:
            movies_without_date.append(movie)
    movies_with_date = sorted(movies_with_date, key=itemgetter("releaseDate"), reverse=True)
    movies = movies_with_date + movies_without_date
    return movies


def _get_data(query_str: str, search_type: str, lang: str) -> List[Dict[str, Any]]:
    """
    Get data.

    For actor, director search - the first person found is used.
    """

    def filter_movies_only(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [e for e in entries if e["media_type"] == "movie"]

    query = query_str.encode("utf-8")
    params = {"query": query, "language": lang, "include_adult": settings.INCLUDE_ADULT}
    search = tmdb.Search()
    if search_type == "movie":
        movies: List[Dict[str, Any]] = search.movie(**params)["results"]
    else:
        persons: List[Dict[str, Any]] = search.person(**params)["results"]
        # We only select the first found actor/director.
        if persons:
            person_id = persons[0]["id"]
        else:
            return []
        person = tmdb.People(person_id)
        person.combined_credits(language=lang)
        if search_type == "actor":
            movies = filter_movies_only(person.cast)
        else:
            movies = filter_movies_only(person.crew)
            movies = [m for m in movies if m["job"] == "Director"]
    return movies


def get_movies_from_tmdb(query: str, search_type: str, options: Dict[str, bool], lang: str) -> List[Dict[str, Any]]:
    """Get movies from TMDB."""
    movies_data = _get_data(query, search_type, lang)
    movies = []
    if movies_data:
        for movie in movies_data:
            poster = _get_poster_from_tmdb(movie["poster_path"])
            # Skip unpopular movies if this option is enabled.
            if search_type == "movie" and options["popularOnly"] and not _is_popular_movie(movie["popularity"]):
                continue
            tmdb_id = movie["id"]
            movie = {
                "id": tmdb_id,
                "tmdbLink": get_tmdb_url(tmdb_id),
                "elementId": f"movie{tmdb_id}",
                "releaseDate": movie.get("release_date"),
                "title": movie["title"],
                "poster": get_poster_url("small", poster),
                "poster2x": get_poster_url("normal", poster),
            }
            movies.append(movie)
        if options["sortByDate"]:
            movies = _sort_by_date(movies)
        movies = _set_proper_date(movies, lang)
        return movies
    return []


def _is_valid_trailer_site(site: str) -> bool:
    """Return True if trailer site is valid."""
    return site in settings.TRAILER_SITES.keys()


def _get_trailers(tmdb_movie: Movies, lang: str) -> List[Dict[str, str]]:
    """Get trailers."""
    trailers = []
    for video in tmdb_movie.videos(language=lang)["results"]:
        if video["type"] == "Trailer":
            site = video["site"]
            try:
                if not _is_valid_trailer_site(site):
                    raise TrailerSiteNotFoundError(f"Site - {site}")
            except TrailerSiteNotFoundError as e:
                if settings.DEBUG:
                    raise
                capture_exception(e)
                continue
            trailer = {"name": video["name"], "key": video["key"], "site": site}
            trailers.append(trailer)
    return trailers


def get_watch_data(tmdb_id: int) -> WatchData:
    """Get watch data."""
    watch_data: WatchData = []
    results: WatchDataTmdb = tmdb.Movies(tmdb_id).watch_providers()["results"]
    items: abc.ItemsView[str, WatchDataCountryTmdb] = results.items()  # type: ignore
    for country, data in items:
        if country in settings.PROVIDERS_SUPPORTED_COUNTRIES and "flatrate" in data:
            for provider in data["flatrate"]:
                record: WatchDataRecord = {"country": country, "provider_id": provider["provider_id"]}
                watch_data.append(record)
    return watch_data


def _get_release_date(release_date_str: str) -> Optional[date]:
    """Get release date."""
    if release_date_str:
        return datetime.strptime(release_date_str, "%Y-%m-%d").date()
    return None


def get_tmdb_movie_data(tmdb_id: int) -> Dict[str, Any]:
    """Get TMDB movie data."""
    tmdb_movie = tmdb.Movies(tmdb_id)
    movie_info_en = tmdb_movie.info(language=settings.LANGUAGE_EN)
    imdb_id = movie_info_en["imdb_id"]
    # Fail early if the IMDb ID is not found.
    if not imdb_id:
        raise TmdbNoImdbIdError(tmdb_id)
    release_date = _get_release_date(movie_info_en["release_date"])
    movie_info_ru = tmdb_movie.info(language=settings.LANGUAGE_RU)
    return {
        "tmdb_id": tmdb_id,
        "imdb_id": imdb_id,
        "release_date": release_date,
        "title_original": movie_info_en["original_title"],
        "poster_ru": _get_poster_from_tmdb(movie_info_ru["poster_path"]),
        "poster_en": _get_poster_from_tmdb(movie_info_en["poster_path"]),
        "homepage": movie_info_en["homepage"],
        "trailers_en": _get_trailers(tmdb_movie, lang=settings.LANGUAGE_EN),
        "trailers_ru": _get_trailers(tmdb_movie, lang=settings.LANGUAGE_RU),
        "title_en": movie_info_en["title"],
        "title_ru": movie_info_ru["title"],
        "description_en": movie_info_en["overview"],
        "description_ru": movie_info_ru["overview"],
    }


def get_tmdb_providers() -> ProvidersTmdb:
    """
    Get TMDB providers.

    The functionality is not supported by tmdbsimple so we have to use the API directly.
    """
    params = {"api_key": settings.TMDB_KEY}
    response = requests.get(urljoin(settings.TMDB_API_BASE_URL, "watch/providers/movie"), params=params)
    providers: ProvidersTmdb = response.json()["results"]
    return providers
