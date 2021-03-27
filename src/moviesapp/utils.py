# -*- coding: utf-8 -*-

import re
from datetime import datetime

import requests
from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .exceptions import OmdbError, OmdbLimitReached, OmdbRequestError
from .models import Movie
from .tmdb import get_tmdb_movie_data


def load_omdb_movie_data(imdb_id):
    try:
        r = requests.get(f"http://www.omdbapi.com/?i={imdb_id}&apikey={settings.OMDB_KEY}")
    except:  # noqa
        if settings.DEBUG:
            raise
        client.captureException()
        raise OmdbRequestError
    movie_data = r.json()
    response = movie_data["Response"]
    if response == "True":
        for key in movie_data:
            if len(movie_data[key]) > 255:
                movie_data[key] = movie_data[key][:252] + "..."
            if movie_data[key] == "N/A":
                movie_data[key] = None
        return movie_data
    elif response == "False" and movie_data["Error"] == "Request limit reached!":
        raise OmdbLimitReached
    else:
        raise OmdbError(movie_data["Error"], imdb_id)


def join_dicts(dict1, dict2):
    result = dict1.copy()
    result.update(dict2)
    return result


def add_movie_to_db(tmdb_id, update=False):
    """
    Return movie id.

    If update is True, return bool (updated or not).
    """

    def save_movie():
        movie = Movie(**movie_data)
        movie.save()
        return movie.id

    def update_movie():
        movie = Movie.objects.filter(tmdb_id=tmdb_id)
        # Maybe use model_to_dict instead?
        movie_initial_data = movie.values()[0]
        movie.update(**movie_data)
        movie_updated_data = Movie.objects.filter(tmdb_id=tmdb_id).values()[0]
        return movie_initial_data != movie_updated_data

    def get_omdb_movie_data(imdb_id):
        def get_runtime(runtime):
            if runtime is not None:
                try:
                    runtime = datetime.strptime(runtime, "%H h %M min")
                except:  # noqa
                    try:
                        runtime = datetime.strptime(runtime, "%H h")
                    except:  # noqa
                        try:
                            runtime = datetime.strptime(runtime, "%M min")
                        except:  # noqa
                            r = re.match(r"(\d+) min", runtime)
                            minutes = int(r.groups()[0])
                            try:
                                runtime = datetime.strptime("{:02d}:{:02d}".format(*divmod(minutes, 60)), "%H:%M")
                            except:  # noqa
                                if settings.DEBUG:
                                    raise
                                else:
                                    client.captureException()
                                return
                return runtime

        movie_data = load_omdb_movie_data(imdb_id)
        return {
            "writer": movie_data.get("Writer"),
            "director": movie_data.get("Director"),
            "actors": movie_data.get("Actors"),
            "genre": movie_data.get("Genre"),
            "country": movie_data.get("Country"),
            "imdb_rating": movie_data.get("imdbRating"),
            "runtime": get_runtime(movie_data.get("Runtime")),
        }

    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb["imdb_id"])
    movie_data = join_dicts(movie_data_tmdb, movie_data_omdb)
    if update:
        return update_movie()
    return save_movie()
