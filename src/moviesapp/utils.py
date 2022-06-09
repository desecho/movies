from typing import Any, Dict, List, Union

from django.utils.timezone import now

from .exceptions import ProviderNotFoundError
from .models import Movie, Provider, ProviderRecord
from .omdb import get_omdb_movie_data
from .tmdb import get_tmdb_movie_data


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge 2 dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result


def save_watch_data(movie: Movie, watch_data: List[Dict[str, Union[str, int]]]) -> None:
    """Save watch data for a movie."""
    for provider_record in watch_data:
        provider_id: int = provider_record["provider_id"]  # type: ignore
        try:
            provider = Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist as e:
            raise ProviderNotFoundError(f"Provider ID - {provider_id}") from e
        ProviderRecord.objects.create(provider=provider, movie=movie, country=provider_record["country"])
    movie.watch_data_update_date = now()
    movie.save()


def load_movie_data(tmdb_id: int) -> Dict[str, Any]:
    """Load movie data from TMDB and OMDb."""
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    return merge_dicts(movie_data_tmdb, movie_data_omdb)
