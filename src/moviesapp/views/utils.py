"""Utils for views."""

from datetime import date, datetime
from typing import Optional

from babel.dates import format_date
from django.shortcuts import get_object_or_404

from ..models import Action, ActionRecord, Record, User
from ..tmdb import get_poster_url, get_tmdb_url
from ..types import TmdbMovieListResultProcessed
from ..utils import is_movie_released
from .types import MovieListResult


def add_movie_to_list(movie_id: int, list_id: int, user: User) -> None:
    """Add movie to list."""
    records = user.get_records().filter(movie_id=movie_id)
    if records.exists():
        record = records[0]
        if record.list_id != list_id:
            ActionRecord(action_id=Action.CHANGED_LIST, user=user, movie_id=movie_id, list_id=list_id).save()
            record.list_id = list_id
            record.date = datetime.today()
            record.save()
    else:
        record = Record(movie_id=movie_id, list_id=list_id, user=user)
        record.save()
        ActionRecord(action_id=Action.ADDED_MOVIE, user=user, movie_id=movie_id, list_id=list_id).save()


def get_anothers_account(username: Optional[str]) -> Optional[User]:
    """Get another's account."""
    if username:
        return get_object_or_404(User, username=username)
    return None


def _format_date(date_: Optional[date], lang: str) -> Optional[str]:
    """Format date."""
    if date_:
        return format_date(date_, locale=lang)
    return None


def get_movie_list_result(tmdb_movie: TmdbMovieListResultProcessed, lang: str) -> MovieListResult:
    """Get movie list result from TMDB movie list result processed."""
    poster = tmdb_movie["poster_path"]
    tmdb_id = tmdb_movie["id"]
    release_date = tmdb_movie["release_date"]
    return MovieListResult(
        id=tmdb_id,
        tmdbLink=get_tmdb_url(tmdb_id),
        releaseDate=_format_date(release_date, lang),
        title=tmdb_movie["title"],
        titleOriginal=tmdb_movie["title_original"],
        poster=get_poster_url("normal", poster),
        poster2x=get_poster_url("big", poster),
        isReleased=is_movie_released(release_date),
    )


def filter_out_movies_user_already_has_in_lists(movies: list[MovieListResult], user: User) -> None:
    """Filter out movies user already has in lists."""
    user_movies_tmdb_ids = list(user.get_records().values_list("movie__tmdb_id", flat=True))
    for movie in list(movies):
        if movie["id"] in user_movies_tmdb_ids:
            movies.remove(movie)
