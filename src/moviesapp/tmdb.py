# -*- coding: utf-8 -*-

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


def get_movies_from_tmdb(query, search_type, options, user, lang):
    def set_proper_date(movies):
        def get_date(date):
            if date:
                date = datetime.strptime(date, '%Y-%m-%d')
                if date:
                    return format_date(date, locale=lang)

        for movie in movies:
            movie['releaseDate'] = get_date(movie['releaseDate'])
        return movies

    def is_popular_movie(movie):
        return movie['popularity'] >= settings.MIN_POPULARITY

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

    def get_data(query, search_type):
        """
        Get data.

        For actor, director search - the first is used.
        """

        def filter_movies_only(entries):
            return [e for e in entries if e['media_type'] == 'movie']

        query = query.encode('utf-8')
        tmdb = get_tmdb(lang)
        search = tmdb.Search()
        if search_type == 'movie':
            movies = search.movie(query=query)['results']
        else:
            persons = search.person(query=query)['results']
            # We only select the first found actor/director.
            if persons:
                person_id = persons[0]['id']
            else:
                return []
            person = tmdb.People(person_id)
            person.combined_credits()
            if search_type == 'actor':
                movies = filter_movies_only(person.cast)
            else:
                movies = filter_movies_only(person.crew)
                movies = [m for m in movies if m['job'] == 'Director']
        return movies

    movies_data = get_data(query, search_type)
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
            poster = get_poster_from_tmdb(movie['poster_path'])
            # Skip unpopular movies if this option is enabled.
            if search_type == 'movie' and options['popularOnly'] and not is_popular_movie(movie):
                continue

            movie = {
                'id': tmdb_id,
                'elementId': f'movie{tmdb_id}',
                'releaseDate': movie['release_date'],
                'title': movie['title'],
                'poster': get_poster_url('small', poster),
                'poster2x': get_poster_url('normal', poster),
            }
            movies.append(movie)
        if options['sortByDate']:
            movies = sort_by_date(movies)
        movies = set_proper_date(movies)
        return movies
    else:
        return []


def get_tmdb_movie_data(tmdb_id):
    def get_release_date(release_date):
        if release_date:
            return release_date

    def get_trailers(movie_data):
        trailers = []
        for trailer in movie_data.videos()['results']:
            t = {'name': trailer['name'], 'source': trailer['key']}
            trailers.append(t)
        return trailers

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
