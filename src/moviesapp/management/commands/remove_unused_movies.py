"""Remove unused movies."""

from typing import Any

from django_tqdm import BaseCommand

from moviesapp.models import Movie


class Command(BaseCommand):
    """Remove unused movies."""

    help = "Remove unused movies"

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        """Execute command."""
        movies = Movie.objects.all()  # pylint: disable=duplicate-code
        tqdm = self.tqdm(total=movies.count(), unit="movie")  # pylint: disable=duplicate-code
        last_movie = movies.last()  # pylint: disable=duplicate-code
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                if not movie.records.exists():
                    movie.delete()
                    message = f"{movie} removed"
                    tqdm.info(message)
                tqdm.update()
