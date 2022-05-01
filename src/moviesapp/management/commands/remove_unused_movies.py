from typing import Any

from django_tqdm import BaseCommand

from moviesapp.models import Movie


class Command(BaseCommand):
    help = "Removes unused movies"

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        movies = Movie.objects.all()  # pylint: disable=duplicate-code
        tqdm = self.tqdm(total=movies.count())  # pylint: disable=duplicate-code
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            tqdm.set_description(movie_info)
            if not movie.records.exists():
                movie.delete()
                message = f"{movie} removed"
                tqdm.info(message)
            tqdm.update()
