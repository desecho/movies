# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re
import urllib2
from datetime import datetime

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .models import ActionRecord, Movie, Record
from .search import get_poster_from_tmdb, get_tmdb


def load_omdb_movie_data(imdb_id):
    try:
        response = urllib2.urlopen('http://www.omdbapi.com/?i=%s' % imdb_id)
    except:
        if settings.DEBUG:
            raise
        else:
            client.captureException()
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
            ActionRecord(action_id=2, user=user, movie_id=movie_id, list_id=list_id).save()
            record.list_id = list_id
            record.date = datetime.today()
            record.save()
    else:
        record = Record(movie_id=movie_id, list_id=list_id, user=user)
        record.save()
        ActionRecord(action_id=1, user=user, movie_id=movie_id, list_id=list_id).save()


def add_movie_to_db(tmdb_id, update=False):
    """
    Return movie id or error code -1 or -2.
    If update is True, return either error code or bool (updated or not)
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
                    runtime = datetime.strptime(runtime, '%H h %M min')
                except:
                    try:
                        runtime = datetime.strptime(runtime, '%H h')
                    except:
                        try:
                            runtime = datetime.strptime(runtime, '%M min')
                        except:
                            r = re.match(r'(\d+) min', '110 min')
                            minutes = int(r.groups()[0])
                            try:
                                runtime = datetime.strptime('{:02d}:{:02d}'.format(*divmod(minutes, 60)), '%H:%M')
                            except:
                                if settings.DEBUG:
                                    raise
                                else:
                                    client.captureException()
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

        # def get_trailers(movie_data):
        #     youtube_trailers = []
        #     for trailer in movie_data.youtube_trailers:
        #         t = {'name': trailer.name, 'source': trailer.source}
        #         youtube_trailers.append(t)
        #     apple_trailers = []
        #     for trailer in movie_data.apple_trailers:
        #         trailers = []
        #         i = 0
        #         for size in trailer.sources:
        #             tr = {'size': size, 'source': trailer.sources[size].source}
        #             trailers.append(tr)
        #             i += 1
        #         apple_trailers.append({'name': trailer.name, 'sizes': trailers})
        #     return {'youtube': youtube_trailers, 'quicktime': apple_trailers}

        def get_movie_data(tmdb_id, lang):
            tmdb = get_tmdb(lang=lang)
            try:
                movie_data = tmdb.Movies(tmdb_id).info()
                return movie_data
            except:
                if settings.DEBUG:
                    raise
                else:
                    client.captureException()
                return

        movie_data_en = get_movie_data(tmdb_id, 'en')
        if movie_data_en is None:
            return None

        movie_data_ru = get_movie_data(tmdb_id, 'ru')
        if movie_data_ru is None:
            return None

        imdb_id = movie_data_en['imdb_id']
        if imdb_id:
            return {
                'tmdb_id': tmdb_id,
                'imdb_id': imdb_id,
                'release_date': get_release_date(movie_data_en['release_date']),
                'title_original': movie_data_en['original_title'],
                'poster_ru': get_poster_from_tmdb(movie_data_ru['poster_path']),
                'poster_en': get_poster_from_tmdb(movie_data_en['poster_path']),
                'homepage': movie_data_en['homepage'],
                # 'trailers': get_trailers(movie_data_en), TODO Fix trailers
                'trailers': {'youtube': [], 'quicktime': []},
                'title_en': movie_data_en['title'],
                'title_ru': movie_data_ru['title'],
                'description_en': movie_data_en['overview'],
                'description_ru': movie_data_ru['overview'],
            }

    movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
    if movie_data_tmdb is None:
        return -1
    movie_data_omdb = get_omdb_movie_data(movie_data_tmdb['imdb_id'])
    if movie_data_omdb is None:
        return -2
    movie_data = dict(movie_data_tmdb.items() + movie_data_omdb.items())
    if update:
        return update_movie()
    return save_movie()


def add_to_list_from_db(tmdb_id, list_id, user):
    """Return error code on error or None on success'
       Return -1 if there is a problem with obtaining data from TMDB
       Return -2 if there is a problem with obtaining data from OMDB"""

    def get_movie_id(tmdb_id):
        """Return movie id or None if movie is not found."""
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.id
        except Movie.DoesNotExist:
            return

    movie_id = get_movie_id(tmdb_id)
    if movie_id is None:
        movie_id = add_movie_to_db(tmdb_id)
    # movie_id can become negative and reflect the errors
    if movie_id > 0:
        add_movie_to_list(movie_id, list_id, user)
    else:
        return movie_id
