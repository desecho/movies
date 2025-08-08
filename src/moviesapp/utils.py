"""Utils."""

from datetime import date
from typing import TYPE_CHECKING, Optional
from urllib.parse import quote

from .omdb import get_omdb_movie_data
from .tmdb import get_tmdb_movie_data
from .types import MovieTmdbOmdb, OmdbMovieProcessed, TmdbMovieProcessed

if TYPE_CHECKING:
    from .models import Record


def merge_movie_data(movie_data_tmdb: TmdbMovieProcessed, movie_data_omdb: OmdbMovieProcessed) -> MovieTmdbOmdb:
    """Merge movie data from TMDB and OMDb together."""
    # Merge movie data explicitly to make type checking work
    return {
        "tmdb_id": movie_data_tmdb["tmdb_id"],
        "imdb_id": movie_data_tmdb["imdb_id"],
        "release_date": movie_data_tmdb["release_date"],
        "title_original": movie_data_tmdb["title_original"],
        "poster": movie_data_tmdb["poster"],
        "homepage": movie_data_tmdb["homepage"],
        "trailers": movie_data_tmdb["trailers"],
        "title": movie_data_tmdb["title"],
        "overview": movie_data_tmdb["overview"],
        "runtime": movie_data_tmdb["runtime"],
        "writer": movie_data_omdb["writer"],
        "director": movie_data_omdb["director"],
        "actors": movie_data_omdb["actors"],
        "genre": movie_data_omdb["genre"],
        "country": movie_data_omdb["country"],
        "imdb_rating": movie_data_omdb["imdb_rating"],
    }


def load_movie_data(tmdb_id: int) -> MovieTmdbOmdb:
    """Load movie data from TMDB and OMDb."""
    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    return merge_movie_data(movie_data_tmdb, movie_data_omdb)


def is_movie_released(release_date: Optional[date]) -> bool:
    """Return True if the movie is released."""
    return release_date is not None and release_date <= date.today()


def generate_social_share_text(record: "Record") -> str:
    """Generate social media share text for a movie record."""
    movie = record.movie

    # Extract year from release date
    year = ""
    if movie.release_date:
        year = f" ({movie.release_date.year})"

    # Build base text with movie title and rating
    share_text = f"Just watched {movie.title}{year} and rated it {record.rating}/5 stars!"

    # Add comment if exists
    if record.comment.strip():
        share_text += f"\n{record.comment}"

    # Create clean hashtag from movie title (remove special characters, spaces)
    clean_title = "".join(c for c in movie.title if c.isalnum())

    # Add hashtags
    share_text += f"\n#Movies #MovieReview #{clean_title}"

    return share_text


def generate_x_share_url(record: "Record") -> str:
    """Generate X (Twitter) share URL for a movie record."""
    share_text = generate_social_share_text(record)
    encoded_text = quote(share_text)
    return f"https://twitter.com/intent/tweet?text={encoded_text}"
