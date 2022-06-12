"""Utils."""
from typing import Any, Dict

from .omdb import get_omdb_movie_data
from .tmdb import get_tmdb_movie_data
from .types import OmdbMovieProcessed


def merge_movie_data(movie_data_tmdb: Dict[str, Any], movie_data_omdb: OmdbMovieProcessed) -> Dict[str, Any]:
    """Merge 2 dictionaries."""
    movie_data = movie_data_tmdb.copy()
    movie_data.update(movie_data_omdb)
    return movie_data


def load_movie_data(tmdb_id: int) -> Dict[str, Any]:
    """Load movie data from TMDB and OMDb."""
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    return merge_movie_data(movie_data_tmdb, movie_data_omdb)
