"""Utils."""
from typing import Any, Dict

from .omdb import get_omdb_movie_data
from .tmdb import get_tmdb_movie_data


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge 2 dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result


def load_movie_data(tmdb_id: int) -> Dict[str, Any]:
    """Load movie data from TMDB and OMDb."""
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    return merge_dicts(movie_data_tmdb, movie_data_omdb)
