import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.exceptions import RequestException
from sentry_sdk import capture_exception

from .exceptions import OmdbError, OmdbLimitReached, OmdbRequestError
from .models import Movie
from .tmdb import get_tmdb_movie_data


def load_omdb_movie_data(imdb_id: str) -> Dict[str, Any]:
    try:
        params = {"apikey": settings.OMDB_KEY, "i": imdb_id}
        response = requests.get(settings.OMDB_BASE_URL, params=params)
    except RequestException as e:
        if settings.DEBUG:
            raise
        capture_exception(e)
        raise OmdbRequestError from e
    movie_data: Dict[str, Any] = response.json()
    response_: str = movie_data["Response"]
    if response_ == "True":
        for key in movie_data:
            if len(movie_data[key]) > 255:
                movie_data[key] = movie_data[key][:252] + "..."
            if movie_data[key] == "N/A":
                movie_data[key] = None
        return movie_data
    if response_ == "False" and movie_data["Error"] == "Request limit reached!":
        raise OmdbLimitReached
    raise OmdbError(movie_data["Error"], imdb_id)


def join_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    result = dict1.copy()
    result.update(dict2)
    return result


def _save_movie(movie_data: Dict[str, Any]) -> int:
    movie = Movie(**movie_data)
    movie.save()
    return movie.pk


def _update_movie(tmdb_id: int, movie_data: Dict[str, Any]) -> bool:
    movie = Movie.objects.filter(tmdb_id=tmdb_id)
    # Maybe use model_to_dict instead?
    movie_initial_data = movie.values()[0]
    movie.update(**movie_data)
    movie_updated_data = Movie.objects.filter(tmdb_id=tmdb_id).values()[0]
    result: bool = movie_initial_data != movie_updated_data
    return result


def _get_runtime(runtime_str: Optional[str]) -> Optional[datetime]:
    if runtime_str is not None:
        try:
            runtime = datetime.strptime(runtime_str, "%H h %M min")
        except ValueError:
            try:
                runtime = datetime.strptime(runtime_str, "%H h")
            except ValueError:
                try:
                    runtime = datetime.strptime(runtime_str, "%M min")
                except ValueError:
                    r = re.match(r"(\d+) min", runtime_str)
                    if r:
                        minutes = int(r.groups()[0])
                        hours, minutes = divmod(minutes, 60)
                        try:
                            runtime = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M")
                        except ValueError as e:
                            if settings.DEBUG:
                                raise
                            capture_exception(e)
                            return None
        return runtime
    return None


def _get_omdb_movie_data(imdb_id: str) -> Dict[str, Any]:
    movie_data = load_omdb_movie_data(imdb_id)
    return {
        "writer": movie_data.get("Writer"),
        "director": movie_data.get("Director"),
        "actors": movie_data.get("Actors"),
        "genre": movie_data.get("Genre"),
        "country": movie_data.get("Country"),
        "imdb_rating": movie_data.get("imdbRating"),
        "runtime": _get_runtime(movie_data.get("Runtime")),
    }


def add_movie_to_db(tmdb_id: int, update: bool = False) -> (int | bool):
    """
    Return movie id.

    If update is True, return bool (updated or not).
    """
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = _get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    movie_data = join_dicts(movie_data_tmdb, movie_data_omdb)
    if update:
        return _update_movie(tmdb_id, movie_data)
    return _save_movie(movie_data)


def get_providers() -> List[Dict[str, Union[str, int]]]:
    params = {"api_key": settings.TMDB_KEY}
    response = requests.get(urljoin(settings.TMDB_API_BASE_URL, "watch/providers/movie"), params=params)
    providers: List[Dict[str, Union[str, int]]] = response.json()["results"]
    return providers
