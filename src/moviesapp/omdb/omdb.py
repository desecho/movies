"""OMDb."""
import requests
from django.conf import settings
from requests.exceptions import RequestException
from sentry_sdk import capture_exception

from ..types import OmdbMovieProcessed
from .exceptions import OmdbError, OmdbLimitReachedError, OmdbRequestError
from .types import OmdbMovie, OmdbMoviePreprocessed, OmdbMoviePreprocessedKey


def _get_processed_omdb_movie_data(data_raw: OmdbMovie) -> OmdbMovieProcessed:
    """Get processed OMDB movie data."""
    data: OmdbMoviePreprocessed = {
        "Writer": None,
        "Director": None,
        "Actors": None,
        "Genre": None,
        "Country": None,
        "imdbRating": None,
    }
    items: list[tuple[OmdbMoviePreprocessedKey, str]] = [
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
    }


def get_omdb_movie_data(imdb_id: str) -> OmdbMovieProcessed:
    """Get movie data from OMDB."""
    try:
        params = {"apikey": settings.OMDB_KEY, "i": imdb_id}
        response = requests.get(settings.OMDB_BASE_URL, params=params, timeout=settings.REQUESTS_TIMEOUT)
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
