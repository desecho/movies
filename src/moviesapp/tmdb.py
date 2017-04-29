# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from operator import itemgetter

import tmdbsimple
from babel.dates import format_date
from django.conf import settings

from .exceptions import MovieNotInDb
from .models import get_poster_url


def get_tmdb(lang=None):
    tmdbsimple.API_KEY = settings.TMDB_KEY
    tmdbsimple.LANGUAGE = lang
    return tmdbsimple


def get_poster_from_tmdb(poster):
    if poster:
        return poster[1:]


def get_movies_from_tmdb(query, type_, options, user, lang):
    def set_proper_date(movies):
        def get_date(date):
            if date:
                date = datetime.strptime(date, '%Y-%m-%d')
                if date:
                    return format_date(date, locale=lang)

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
        """For actor, director search - the first is used."""

        def process_person_entries(entries):
            movies = [e for e in entries if e['media_type'] == 'movie']
            for m in movies:
                # popularity is not being provided so we set it the min popularity to be sure it is always shown.
                m['popularity'] = settings.MIN_POPULARITY
            return movies

        query = query.encode('utf-8')
        tmdb = get_tmdb(lang)
        search = tmdb.Search()
        if type_ == 'movie':
            movies = search.movie(query=query)['results']
        else:
            persons = search.person(query=query)['results']
            if persons:
                person_id = persons[0]['id']
            else:
                return []
            person = tmdb.People(person_id)
            person.combined_credits()
            if type_ == 'actor':
                movies = process_person_entries(person.cast)
            else:
                movies = process_person_entries(person.crew)
                movies = [m for m in movies if m['job'] == 'Director']
        return movies

    output = {}
    movies_data = get_data(query, type_)
    movies = []
    i = 0
    if movies_data:
        user_movies_tmdb_ids = user.get_records().values_list('movie__tmdb_id', flat=True)
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
        if options['popular_only']:
            movies = remove_not_popular_movies(movies)
        if options['sort_by_date']:
            movies = sort_by_date(movies)
        movies = set_proper_date(movies)
        if movies:
            output['movies'] = movies
            output['status'] = 'success'
        else:
            output['status'] = 'not_found'
    else:
        output['status'] = 'not_found'
    return output


def get_tmdb_movie_data(tmdb_id):
    def get_release_date(release_date):
        if release_date:
            return release_date

    def get_trailers(movie_data):
        youtube_trailers = []
        trailers = movie_data.videos()['results']
        for trailer in trailers:
            if trailer['site'] == 'YouTube':
                t = {'name': trailer['name'], 'source': trailer['key']}
                youtube_trailers.append(t)
            else:
                raise Exception(trailer['site'])
        return {'youtube': youtube_trailers, 'quicktime': []}

    def get_movie_data(tmdb_id, lang):
        tmdb = get_tmdb(lang=lang)
        return tmdb.Movies(tmdb_id)

    movie_data_en = get_movie_data(tmdb_id, 'en')
    movie_info_en = movie_data_en.info()
    # We have to get all info in english first before we switch to russian or everything breaks.
    trailers_en = get_trailers(movie_data_en)
    movie_data_ru = get_movie_data(tmdb_id, 'ru')
    movie_info_ru = movie_data_ru.info()
    trailers_ru = get_trailers(movie_data_ru)
    imdb_id = movie_info_en['imdb_id']
    if imdb_id:
        return {
            'tmdb_id': tmdb_id,
            'imdb_id': imdb_id,
            'release_date': get_release_date(movie_info_en['release_date']),
            'title_original': movie_info_en['original_title'],
            'poster_ru': get_poster_from_tmdb(movie_info_ru['poster_path']),
            'poster_en': get_poster_from_tmdb(movie_info_en['poster_path']),
            'homepage': movie_info_en['homepage'],
            'trailers_en': trailers_en,
            'trailers_ru': trailers_ru,
            'title_en': movie_info_en['title'],
            'title_ru': movie_info_ru['title'],
            'description_en': movie_info_en['overview'],
            'description_ru': movie_info_ru['overview'],
        }
    else:
        raise MovieNotInDb(tmdb_id)
