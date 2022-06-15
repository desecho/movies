"""OMDb."""
import re
from datetime import datetime
from typing import List, Optional, Tuple

import requests
from django.conf import settings
from requests.exceptions import RequestException
from sentry_sdk import capture_exception

from ..types import OmdbMovieProcessed
from .exceptions import OmdbError, OmdbLimitReachedError, OmdbRequestError
from .types import OmdbMovie, OmdbMoviePreprocessed, OmdbMoviePreprocessedKey


def _get_runtime(runtime_str: Optional[str]) -> Optional[datetime]:
    """Get runtime."""
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


def _get_processed_omdb_movie_data(data_raw: OmdbMovie) -> OmdbMovieProcessed:
    """Get processed OMDB movie data."""
    data: OmdbMoviePreprocessed = {
        "Writer": None,
        "Director": None,
        "Actors": None,
        "Genre": None,
        "Country": None,
        "imdbRating": None,
        "Runtime": None,
    }
    items: List[Tuple[OmdbMoviePreprocessedKey, str]] = [
        (key, value) for (key, value) in data_raw.items() if key in data and value != "N/A"  # type: ignore
    ]
    for key, value in items:
        if len(value) > 255:
            data[key] = value[:252] + "..."
        data[key] = value
    return {
        "writer": data["Writer"],
        "director": data["Director"],
        "actors": data["Actors"],
        "genre": data["Genre"],
        "country": data["Country"],
        "imdb_rating": data["imdbRating"],
        "runtime": _get_runtime(data["Runtime"]),
    }


def get_omdb_movie_data(imdb_id: str) -> OmdbMovieProcessed:
    """Get movie data from OMDB."""
    try:
        params = {"apikey": settings.OMDB_KEY, "i": imdb_id}
        response = requests.get(settings.OMDB_BASE_URL, params=params)
    except RequestException as e:
        if settings.DEBUG:
            raise
        capture_exception(e)
        raise OmdbRequestError from e
    movie_data: OmdbMovie = response.json()
    movie_data_response: str = movie_data["Response"]
    if movie_data_response == "True":
        return _get_processed_omdb_movie_data(movie_data)
    error = movie_data["Error"]
    if error == "Request limit reached!":
        raise OmdbLimitReachedError
    raise OmdbError(error, imdb_id)
