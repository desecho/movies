"""Utils."""

from .omdb import get_omdb_movie_data
from .tmdb import get_tmdb_movie_data
from .types import MovieTmdbOmdb, OmdbMovieProcessed, TmdbMovieProcessed


def merge_movie_data(movie_data_tmdb: TmdbMovieProcessed, movie_data_omdb: OmdbMovieProcessed) -> MovieTmdbOmdb:
    """Merge movie data from TMDB and OMDb together."""
    # Merge movie data explicitly to make type checking work
    return {
        "tmdb_id": movie_data_tmdb["tmdb_id"],
        "imdb_id": movie_data_tmdb["imdb_id"],
        "release_date": movie_data_tmdb["release_date"],
        "title_original": movie_data_tmdb["title_original"],
        "poster_ru": movie_data_tmdb["poster_ru"],
        "poster_en": movie_data_tmdb["poster_en"],
        "homepage": movie_data_tmdb["homepage"],
        "trailers_en": movie_data_tmdb["trailers_en"],
        "trailers_ru": movie_data_tmdb["trailers_ru"],
        "title_en": movie_data_tmdb["title_en"],
        "title_ru": movie_data_tmdb["title_ru"],
        "description_en": movie_data_tmdb["description_en"],
        "description_ru": movie_data_tmdb["description_ru"],
        "writer": movie_data_omdb["writer"],
        "director": movie_data_omdb["director"],
        "actors": movie_data_omdb["actors"],
        "genre": movie_data_omdb["genre"],
        "country": movie_data_omdb["country"],
        "imdb_rating": movie_data_omdb["imdb_rating"],
        "runtime": movie_data_omdb["runtime"],
    }


def load_movie_data(tmdb_id: int) -> MovieTmdbOmdb:
    """Load movie data from TMDB and OMDb."""
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    return merge_movie_data(movie_data_tmdb, movie_data_omdb)
