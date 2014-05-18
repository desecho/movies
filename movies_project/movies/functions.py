from movies.models import Movie, Record, User, ActionRecord
from django.conf import settings
import vkontakte
import urllib2
import json
import tmdb3
from operator import itemgetter
from datetime import datetime

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)
tmdb3.set_locale(settings.LANGUAGE_CODE, settings.LANGUAGE_CODE)

def get_tmdb_id(imdb_id):
    try:
        return tmdb3.Movie.fromIMDB(imdb_id).id
    except:
        return


def get_friends(user):
    if user.is_vk_user():
        vk = vkontakte.API(settings.VK_APP_ID, settings.VK_APP_SECRET)
        friends = vk.friends.get(uid=user.username)
        friends = [str(x) for x in friends]
        friends = User.objects.filter(username__in=friends).order_by('first_name')
    else:
        friends = None
    return friends


def filter_movies_for_recommendation(records, user):
    'Keeps movies only with 3+ rating, removes watched movies'
    # filters only 3+ ratied movies
    records = records.filter(rating__gte=3)
    # removes watched movies
    records = records.exclude(movie__in=user.get_movie_ids())
    return records

def load_omdb_movie_data(imdb_id):
    try:
        response = urllib2.urlopen('http://www.omdbapi.com/?i=%s' % imdb_id)
    except:
        return
    html = response.read()
    movie_data = json.loads(html)
    if movie_data.get('Response') == 'True':
        for key in movie_data:
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


def add_to_list_from_db(tmdb_id, list_id, user):
    '''Returns error code on error or None on success'
       Returns -1 if there is a problem with obtaining data from TMDB
       Returns -2 if there is a problem with obtaining data from OMDB'''

    def get_movie_id(tmdb_id):
        'Return movie id or None if movie is not found'
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.id
        except:
            return

    def add_movie_to_db(tmdb_id):
        'returns movie id or error codes -1 or -2'

        def save_movie_to_db(movie_data):
            movie = Movie(**movie_data)
            movie.save()
            return Movie.objects.get(tmdb_id=tmdb_id).id

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
                'plot': movie_data.get('Plot'),
                'writer': movie_data.get('Writer'),
                'director': movie_data.get('Director'),
                'actors': movie_data.get('Actors'),
                'genre': movie_data.get('Genre'),
                'imdb_rating': movie_data.get('imdbRating'),
                'runtime': get_runtime(movie_data.get('Runtime'))}

        def get_tmdb_movie_data(tmdb_id):
            def get_release_date(release_date):
                if release_date:
                    return release_date

            def process_hacks(movie_data):
                # X-files Fight the future hack
                if movie_data.imdb == 'tt0019387':
                    movie_data.imdb = 'tt0120902'
                return movie_data

            def get_poster(poster):
                if poster:
                    return poster.filename

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

            try:
                movie_data = tmdb3.Movie(tmdb_id)
            except:
                return
            if movie_data.imdb:
                movie_data = process_hacks(movie_data)
                return {
                    'tmdb_id': tmdb_id,
                    'imdb_id': movie_data.imdb,
                    'release_date': get_release_date(movie_data.releasedate),
                    'title': movie_data.originaltitle,
                    'poster': get_poster(movie_data.poster),
                    'homepage': movie_data.homepage,
                    'trailers': get_trailers(movie_data),
                    'title_ru': movie_data.title,
                    'overview': movie_data.overview,
                }
        movie_data_tmdb = get_tmdb_movie_data(tmdb_id)
        if movie_data_tmdb is None:
            return -1
        movie_data_omdb = get_omdb_movie_data(movie_data_tmdb['imdb_id'])
        if movie_data_omdb is None:
            return -2
        return save_movie_to_db(dict(movie_data_tmdb.items() + movie_data_omdb.items()))

    movie_id = get_movie_id(tmdb_id)
    if movie_id is None:
        movie_id = add_movie_to_db(tmdb_id)
    # movie_id can become negative and reflect the errors
    if movie_id > 0:
        add_movie_to_list(movie_id, list_id, user)
    else:
        return movie_id


def get_movies_from_tmdb(query, type, options, user):
        def set_proper_date(movies):
            def format_date(date):
                if date:
                    return date.strftime('%d.%m.%y')
            m = []
            for movie in movies:
                movie['release_date'] = format_date(movie['release_date'])
                m.append(movie)
            return movies

        # def sortByPopularity(movies):
        #     movies = sorted(movies, key=itemgetter('popularity'), reverse=True)
        #     for movie in movies:
        #         del movie['popularity']
        #     return movies

        def remove_not_popular_movies(movies):
            m = []
            for movie in movies:
                if movie['popularity'] > settings.MIN_POPULARITY:
                    del movie['popularity']
                    m.append(movie)
            if not m:                  # keep initial movie list if all are unpopular
                m = movies
            return m

        def sort_by_date(movies):
            movies_with_date = []
            movies_without_date = []
            for movie in movies:
                if movie['release_date']:
                    movies_with_date.append(movie)
                else:
                    movies_without_date.append(movie)
            if not movies_with_date and not movies_without_date:      # These two lines - to check if no movies are left because of low popularity
                movies_with_date = movies                             # ---
            movies_with_date = sorted(movies_with_date, key=itemgetter('release_date'), reverse=True)
            movies = movies_with_date + movies_without_date
            return movies

        def get_posterUrl(poster):
            if poster:
                url = settings.POSTER_BASE_URL + settings.POSTER_SIZE_SMALL + '/' + poster.filename
            else:
                url = settings.NO_POSTER_SMALL_IMAGE_URL
            return url

        def get_data(query, type):
            query = query.encode('utf-8')
            '''Types - 1 - movie, 2 - actor, 3 - director
               for actor, director search - the first is used.'''
            if type == 1:
                try:
                    movies = tmdb3.searchMovie(query)
                except:
                    return -1
            else:
                try:
                    result = tmdb3.searchPerson(query)
                except:
                    return -1
                movies = []
                if len(result):
                    person = result[0]
                    if type == 2:
                        movies = person.roles
                    else:
                        for m in person.crew:
                            if m.job == 'Director':
                                movies.append(m)
            return movies

        output = {}

        results = get_data(query, type)
        if results == -1:
            output['status'] = -1
            return output
        movies = []
        i = 0
        if len(results):
            try:
                for result in results:
                    i += 1
                    if i > settings.MAX_RESULTS:
                        break
                    if Record.objects.filter(movie__tmdb_id=result.id, user=user).exists():
                        continue
                    movie = {
                        'id': result.id,
                        'release_date': result.releasedate,
                        'popularity': result.popularity,                    # for popularity sorting
                        # 2DO create an option for original titles
                        #'title': result.originaltitle,
                        'title': result.title,
                        'poster': get_posterUrl(result.poster),
                    }
                    movies.append(movie)
            except IndexError:                                              # strange exception in 'matrix case'
                pass
            if options['popular_only']:
                movies = remove_not_popular_movies(movies)
            if options['sort_by_date']:
                movies = sort_by_date(movies)
            #movies = sortByPopularity(movies)

            movies = set_proper_date(movies)
            if len(movies):
                output['status'] = 1
                output['movies'] = movies
            else:
                output['status'] = 0
        else:
                output['status'] = 0
        return output
