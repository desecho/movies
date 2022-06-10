"""OMDb."""
import re
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from django.conf import settings
from requests.exceptions import RequestException
from sentry_sdk import capture_exception


class OmdbLimitReachedError(Exception):
    """OMDb limit reached."""


class OmdbRequestError(Exception):
    """OMDb request error."""


class OmdbError(Exception):
    """OMDb error."""


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


def load_omdb_movie_data(imdb_id: str) -> Dict[str, Any]:
    """Load movie data from OMDB."""
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
        raise OmdbLimitReachedError
    raise OmdbError(movie_data["Error"], imdb_id)


def get_omdb_movie_data(imdb_id: str) -> Dict[str, Any]:
    """Get movie data from OMDB."""
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
