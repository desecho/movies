from typing import Any

from django_tqdm import BaseCommand

from moviesapp.models import Movie
from moviesapp.omdb import load_omdb_movie_data


class Command(BaseCommand):
    help = "Updates the IMDb ratings"

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        movies = Movie.objects.all()
        tqdm = self.tqdm(total=movies.count())
        last_movie = movies.last()
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                movie_data = load_omdb_movie_data(movie.imdb_id)
                new_rating = movie_data.get("imdbRating")
                if new_rating != str(movie.imdb_rating):
                    movie.imdb_rating = new_rating
                    movie.save()
                    message = f"{movie} - rating updated"
                    tqdm.info(message)
                tqdm.update()
