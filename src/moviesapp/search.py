# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import itemgetter

import tmdb3
from django.conf import settings
from raven.contrib.django.raven_compat.models import client

from .models import Record, get_poster_url


def init_tmdb():
    tmdb3.set_key(settings.TMDB_KEY)
    tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)
    tmdb3.set_locale(*settings.LOCALES[settings.LANGUAGE_CODE])
    return tmdb3


tmdb = init_tmdb()


def get_poster_from_tmdb(poster):
    if poster:
        return poster.filename


def get_movies_from_tmdb(query, type_, options, user):
    STATUS_CODES = {
        'error': -1,
        'not found': 0,
        'found': 1,
    }

    def set_proper_date(movies):
        def format_date(date):
            if date:
                return date.strftime('%d.%m.%y')

        for movie in movies:
            movie['releaseDate'] = format_date(movie['releaseDate'])
        return movies

    # def sortByPopularity(movies):
    #     movies = sorted(movies, key=itemgetter('popularity'), reverse=True)
    #     for movie in movies:
    #         del movie['popularity']
    #     return movies

    def remove_not_popular_movies(movies):
        movies_output = []
        for movie in movies:
            if movie['popularity'] > settings.MIN_POPULARITY:
                del movie['popularity']  # remove unnesessary data
                movies_output.append(movie)
        if not movies_output:  # keep initial movie list if all are unpopular
            movies_output = movies
        return movies_output

    def sort_by_date(movies):
        movies_with_date = []
        movies_without_date = []
        for movie in movies:
            if movie['releaseDate']:
                movies_with_date.append(movie)
            else:
                movies_without_date.append(movie)
        movies_with_date = sorted(movies_with_date, key=itemgetter('releaseDate'), reverse=True)
        movies = movies_with_date + movies_without_date
        return movies

    def get_data(query, type_):
        'For actor, director search - the first is used.'
        tmdb.set_locale(*settings.LOCALES[user.language])
        query = query.encode('utf-8')
        SEARCH_TYPES_IDS = {
            'movie': 1,
            'actor': 2,
            'director': 3,
        }
        if type_ == SEARCH_TYPES_IDS['movie']:
            try:
                movies = tmdb.searchMovie(query)
            except:
                if settings.DEBUG:
                    raise
                else:
                    client.captureException()
                return -1
        else:
            try:
                result = tmdb.searchPerson(query)
            except:
                if settings.DEBUG:
                    raise
                else:
                    client.captureException()
                return -1
            movies = []
            if result:
                person = result[0]
                if type_ == SEARCH_TYPES_IDS['actor']:
                    movies = person.roles
                else:
                    for movie in person.crew:
                        if movie.job == 'Director':
                            movies.append(movie)
        return movies

    output = {}
    movies_data = get_data(query, type_)
    if movies_data == STATUS_CODES['error']:
        output['status'] = STATUS_CODES['error']
        return output
    movies = []
    i = 0

    if movies_data:
        try:
            for movie in movies_data:
                i += 1
                if i > settings.MAX_RESULTS:
                    break
                # ignore movie if imdb not found
                if Record.objects.filter(movie__tmdb_id=movie.id, user=user).exists() or not movie.imdb:
                    continue

                movie = {
                    'id': movie.id,
                    'releaseDate': movie.releasedate,
                    'popularity': movie.popularity,
                    'title': movie.title,
                    'poster': get_poster_url('small', get_poster_from_tmdb(movie.poster)),
                }
                movies.append(movie)
        except IndexError:  # strange exception in 'matrix case' TODO look into that
            pass
        if options['popular_only']:
            movies = remove_not_popular_movies(movies)
        if options['sort_by_date']:
            movies = sort_by_date(movies)
        # movies = sortByPopularity(movies)

        movies = set_proper_date(movies)
        if movies:
            output['status'] = STATUS_CODES['found']
            output['movies'] = movies
        else:
            output['status'] = STATUS_CODES['not found']
    else:
        output['status'] = STATUS_CODES['not found']
    return output
