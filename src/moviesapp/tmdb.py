from datetime import datetime
from operator import itemgetter
from typing import Any, Dict, List, Optional, Union

import tmdbsimple
from babel.dates import format_date
from django.conf import settings
from tmdbsimple import Movies

from .exceptions import MovieNotInDb
from .models import User, UserAnonymous, get_poster_url


def _get_tmdb(lang: str) -> tmdbsimple:
    tmdbsimple.API_KEY = settings.TMDB_KEY
    tmdbsimple.LANGUAGE = lang
    return tmdbsimple


def _get_poster_from_tmdb(poster: str) -> Optional[str]:
    if poster:
        return poster[1:]
    return None


def _get_date(date_str: str, lang: str) -> Optional[str]:
    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date:
            date_str = format_date(date, locale=lang)
            return date_str
    return None


def _set_proper_date(movies: List[Dict[str, Any]], lang: str) -> List[Dict[str, Any]]:
    for movie in movies:
        movie["releaseDate"] = _get_date(movie["releaseDate"], lang)
    return movies


def _is_popular_movie(popularity: float) -> bool:
    return popularity >= settings.MIN_POPULARITY


def _sort_by_date(movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    For actor, director search - the first is used.
    """

    def filter_movies_only(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [e for e in entries if e["media_type"] == "movie"]

    query = query_str.encode("utf-8")
    tmdb = _get_tmdb(lang)
    search = tmdb.Search()
    if search_type == "movie":
        movies: List[Dict[str, Any]] = search.movie(query=query)["results"]
    else:
        persons: List[Dict[str, Any]] = search.person(query=query)["results"]
        # We only select the first found actor/director.
        if persons:
            person_id = persons[0]["id"]
        else:
            return []
        person = tmdb.People(person_id)
        person.combined_credits()
        if search_type == "actor":
            movies = filter_movies_only(person.cast)
        else:
            movies = filter_movies_only(person.crew)
            movies = [m for m in movies if m["job"] == "Director"]
    return movies


def get_movies_from_tmdb(
    query: str, search_type: str, options: Dict[str, bool], user: Union[User, UserAnonymous], lang: str
) -> List[Dict[str, Any]]:
    movies_data = _get_data(query, search_type, lang)
    movies = []
    i = 0
    if movies_data:
        user_movies_tmdb_ids = list(user.get_records().values_list("movie__tmdb_id", flat=True))
        for movie in movies_data:
            tmdb_id = movie["id"]
            i += 1
            if i > settings.MAX_RESULTS:
                break
            if tmdb_id in user_movies_tmdb_ids:
                continue
            poster = _get_poster_from_tmdb(movie["poster_path"])
            # Skip unpopular movies if this option is enabled.
            if search_type == "movie" and options["popularOnly"] and not _is_popular_movie(movie["popularity"]):
                continue

            movie = {
                "id": tmdb_id,
                "tmdbLink": f"{settings.TMDB_MOVIE_BASE_URL}{tmdb_id}",
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


def get_tmdb_movie_data(tmdb_id: int) -> Dict[str, Any]:
    def get_trailers(movie_data: Movies) -> List[Dict[str, str]]:
        trailers = []
        for trailer in movie_data.videos()["results"]:
            trailer_ = {"name": trailer["name"], "source": trailer["key"]}
            trailers.append(trailer_)
        return trailers

    def get_movie_data(tmdb_id: int, lang: str) -> Movies:
        tmdb = _get_tmdb(lang)
        return tmdb.Movies(tmdb_id)

    movie_data_en = get_movie_data(tmdb_id, "en")
    movie_info_en = movie_data_en.info()
    # We have to get all info in english first before we switch to russian or everything breaks.
    trailers_en = get_trailers(movie_data_en)
    movie_data_ru = get_movie_data(tmdb_id, "ru")
    movie_info_ru = movie_data_ru.info()
    trailers_ru = get_trailers(movie_data_ru)
    imdb_id = movie_info_en["imdb_id"]
    release_date = movie_info_en["release_date"] if movie_info_en["release_date"] else None
    if imdb_id:
        return {
            "tmdb_id": tmdb_id,
            "imdb_id": imdb_id,
            "release_date": release_date,
            "title_original": movie_info_en["original_title"],
            "poster_ru": _get_poster_from_tmdb(movie_info_ru["poster_path"]),
            "poster_en": _get_poster_from_tmdb(movie_info_en["poster_path"]),
            "homepage": movie_info_en["homepage"],
            "trailers_en": trailers_en,
            "trailers_ru": trailers_ru,
            "title_en": movie_info_en["title"],
            "title_ru": movie_info_ru["title"],
            "description_en": movie_info_en["overview"],
            "description_ru": movie_info_ru["overview"],
        }
    raise MovieNotInDb(tmdb_id)
