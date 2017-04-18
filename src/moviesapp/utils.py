# coding: utf-8
from __future__ import unicode_literals

import json
import urllib2
from datetime import datetime

import tmdb3
from django.conf import settings

from .models import ActionRecord, Movie, Record


def init_tmdb():
    tmdb3.set_key(settings.TMDB_KEY)
    tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)
    tmdb3.set_locale(*settings.LOCALES[settings.LANGUAGE_CODE])
    return tmdb3


def get_poster_from_tmdb(poster):
    if poster:
        return poster.filename


def load_omdb_movie_data(imdb_id):
    try:
        response = urllib2.urlopen('http://www.omdbapi.com/?i=%s' % imdb_id)
    except:
        return
    movie_data = json.loads(response.read())
    if movie_data.get('Response') == 'True':
        for key in movie_data:
            if len(movie_data[key]) > 255:
                movie_data[key] = movie_data[key][:252] + '...'
            if movie_data[key] == 'N/A':
                movie_data[key] = None
        return movie_data


def add_movie_to_list(movie_id, list_id, user):
    record = Record.objects.filter(movie_id=movie_id, user=user)
    if record.exists():
        record = record[0]
        if record.list_id != list_id:
            ActionRecord(action_id=2, user=user,
                         movie_id=movie_id, list_id=list_id).save()
            record.list_id = list_id
            record.date = datetime.today()
            record.save()
    else:
        record = Record(movie_id=movie_id, list_id=list_id, user=user)
        record.save()
        ActionRecord(action_id=1, user=user,
                     movie_id=movie_id, list_id=list_id).save()


def add_movie_to_db(tmdb_id, refresh=False):
    """Return movie id or error codes -1 or -2."""

    def save_movie_to_db(movie_data):
        if refresh:
            movie = Movie.objects.filter(tmdb_id=tmdb_id)
            movie.update(**movie_data)
            movie = movie[0]
        else:
            movie = Movie(**movie_data)
            movie.save()
        return movie.id

    def get_omdb_movie_data(imdb_id):
        def get_runtime(runtime):
            if runtime is not None:
                try:
                    runtime = datetime.strptime(runtime, '%H h %M min')
                except:
                    try:
                        runtime = datetime.strptime(runtime, '%H h')
                    except:
                        try:
                            runtime = datetime.strptime(runtime, '%M min')
                        except:
                            return
                return runtime

        movie_data = load_omdb_movie_data(imdb_id)
        return {
            'writer': movie_data.get('Writer'),
            'director': movie_data.get('Director'),
            'actors': movie_data.get('Actors'),
            'genre': movie_data.get('Genre'),
            'country': movie_data.get('Country'),
            'imdb_rating': movie_data.get('imdbRating'),
            'runtime': get_runtime(movie_data.get('Runtime'))}

    def get_tmdb_movie_data(tmdb_id):
        def get_release_date(release_date):
            if release_date:
                return release_date

        def get_trailers(movie_data):
            youtube_trailers = []
            for trailer in movie_data.youtube_trailers:
                t = {'name': trailer.name, 'source': trailer.source}
                youtube_trailers.append(t)
            apple_trailers = []
            for trailer in movie_data.apple_trailers:
                trailers = []
                i = 0
                for size in trailer.sources:
                    tr = {'size': size, 'source': trailer.sources[size].source}
                    trailers.append(tr)
                    i += 1
                apple_trailers.append({'name': trailer.name, 'sizes': trailers})
            return {'youtube': youtube_trailers, 'quicktime': apple_trailers}

        def get_movie_data(tmdb_id, lang):
            tmdb.set_locale(*settings.LOCALES[lang])
            try:
                movie_data = tmdb.Movie(tmdb_id)
                movie_data.imdb  # any request to trigger a request
                return movie_data
            except Exception:
                return

        movie_data_en = get_movie_data(tmdb_id, 'en')
        if movie_data_en is None:
            return None

        movie_data_ru = get_movie_data(tmdb_id, 'ru')
        if movie_data_ru is None:
            return None

        if movie_data_en.imdb:
            return {
                'tmdb_id': tmdb_id,
                'imdb_id': movie_data_en.imdb,
                'release_date': get_release_date(movie_data_en.releasedate),
                'title_original': movie_data_en.originaltitle,
                'poster_ru': get_poster_from_tmdb(movie_data_ru.poster),
                'poster_en': get_poster_from_tmdb(movie_data_en.poster),
                'homepage': movie_data_en.homepage,
                'trailers': get_trailers(movie_data_en),
                'title_en': movie_data_en.title,
                'title_ru': movie_data_ru.title,
                'description_en': movie_data_en.overview,
                'description_ru': movie_data_ru.overview,
            }

    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    if movie_data_tmdb is None:
        return -1
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb['imdb_id'])
    if movie_data_omdb is None:
        return -2
    return save_movie_to_db(dict(movie_data_tmdb.items() + movie_data_omdb.items()))


def add_to_list_from_db(tmdb_id, list_id, user):
    """Return error code on error or None on success'
       Return -1 if there is a problem with obtaining data from TMDB
       Return -2 if there is a problem with obtaining data from OMDB"""

    def get_movie_id(tmdb_id):
        """Return movie id or None if movie is not found."""
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.id
        except:
            return

    movie_id = get_movie_id(tmdb_id)
    if movie_id is None:
        movie_id = add_movie_to_db(tmdb_id)
    # movie_id can become negative and reflect the errors
    if movie_id > 0:
        add_movie_to_list(movie_id, list_id, user)
    else:
        return movie_id


tmdb = init_tmdb()
