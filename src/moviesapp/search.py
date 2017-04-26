# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from operator import itemgetter

from babel.dates import format_date
import tmdbsimple
from django.conf import settings

from .models import Record, get_poster_url


def get_tmdb(lang=None):
    tmdbsimple.API_KEY = settings.TMDB_KEY
    tmdbsimple.LANGUAGE = lang
    return tmdbsimple


def get_poster_from_tmdb(poster):
    if poster:
        return poster[1:]


def get_movies_from_tmdb(query, type_, options, user):
    STATUS_CODES = {
        'error': -1,
        'not found': 0,
        'found': 1,
    }

    def set_proper_date(movies):
        def get_date(date):
            if date:
                date = datetime.strptime(date, '%Y-%m-%d')
                if date:
                    return format_date(date, locale=user.language)

        for movie in movies:
            movie['releaseDate'] = get_date(movie['releaseDate'])
        return movies

    def remove_not_popular_movies(movies):
        movies_output = []
        for movie in movies:
            if movie['popularity'] >= settings.MIN_POPULARITY:
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

        def process_person_entries(entries):
            movies = [e for e in entries if e['media_type'] == 'movie']
            for m in movies:
                # popularity is not being provided so we set it the min popularity to be sure it is always shown.
                m['popularity'] = settings.MIN_POPULARITY
            return movies

        query = query.encode('utf-8')
        SEARCH_TYPES_IDS = {
            'movie': 1,
            'actor': 2,
            'director': 3,
        }
        tmdb = get_tmdb(user.language)
        search = tmdb.Search()
        if type_ == SEARCH_TYPES_IDS['movie']:
            movies = search.movie(query=query)['results']
        else:
            persons = search.person(query=query)['results']
            if persons:
                person_id = persons[0]['id']
            else:
                return []
            person = tmdb.People(person_id)
            person.combined_credits()
            if type_ == SEARCH_TYPES_IDS['actor']:
                movies = process_person_entries(person.cast)
            else:
                movies = process_person_entries(person.crew)
                movies = [m for m in movies if m['job'] == 'Director']
        return movies

    output = {}
    movies_data = get_data(query, type_)
    if movies_data == STATUS_CODES['error']:
        output['status'] = STATUS_CODES['error']
        return output
    movies = []
    i = 0
    if movies_data:
        user_movies_tmdb_ids = Record.objects.filter(user=user).values_list('movie__tmdb_id', flat=True)
        # try:
        for movie in movies_data:
            tmdb_id = movie['id']
            i += 1
            if i > settings.MAX_RESULTS:
                break
            if tmdb_id in user_movies_tmdb_ids:
                continue
            movie = {
                'id': tmdb_id,
                'releaseDate': movie['release_date'],
                'popularity': movie['popularity'],
                'title': movie['title'],
                'poster': get_poster_url('small', get_poster_from_tmdb(movie['poster_path'])),
            }
            movies.append(movie)
            # except IndexError:  # strange exception in 'matrix case'? Don't believe it.
            # pass
        if options['popular_only']:
            movies = remove_not_popular_movies(movies)
        if options['sort_by_date']:
            movies = sort_by_date(movies)
        movies = set_proper_date(movies)
        if movies:
            output['status'] = STATUS_CODES['found']
            output['movies'] = movies
        else:
            output['status'] = STATUS_CODES['not found']
    else:
        output['status'] = STATUS_CODES['not found']
    return output
