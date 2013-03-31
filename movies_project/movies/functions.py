from movies.models import Movie, Record, User, ActionRecord
from django.conf import settings
import vkontakte
import urllib2
import json
import tmdb3
from operator import itemgetter

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)


def get_movie_id_from_tmdb_from_imdb_id(id):
    try:
        return tmdb3.Movie.fromIMDB(id).id
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
    'keeps movies only with 3+ rating, removes watched movies'
    # filters only 3+ ratied movies
    records = records.filter(rating__gte=3)
    # removes watched movies
    records = records.exclude(movie__in=user.get_movie_ids())
    return records


def add_movie_to_list(id, list_id, user):
    r = Record.objects.filter(movie_id=id, user=user)
    if r.exists():
        if r[0].list_id != list_id:
            ActionRecord(action_id=2, user=user, movie_id=id, list_id=list_id).save()
            r[0].list_id = list_id
            r[0].save()
    else:
        r = Record(movie_id=id, list_id=list_id, user=user)
        r.save()
        ActionRecord(action_id=1, user=user, movie_id=id, list_id=list_id).save()


def add_to_list_from_db(movie_id, list_id, user):
    def check_if_movie_exists_in_db(id):
        try:
            movie = Movie.objects.get(tmdb_id=id)
            return movie.id
        except:
            return

    def add_movie_to_db(id):
        'returns id of the movie in movies database or error codes -1 or -2'
        def save_movie_to_db(movie):
            m = Movie(**movie)
            m.save()
            return Movie.objects.get(tmdb_id=movie['tmdb_id']).id

        def get_movie_from_imdb(id):
            def process_imdb_data(data):
                if data != 'N/A':
                    return data
            try:
                response = urllib2.urlopen('http://www.imdbapi.com/?i=%s' % id)
            except:
                return
            html = response.read()
            imdb_data = json.loads(html)
            if imdb_data.get('Response') == 'True':
                movie = {'plot': process_imdb_data(imdb_data.get('Plot')),
                         'writer': process_imdb_data(imdb_data.get('Writer')),
                         'director': process_imdb_data(imdb_data.get('Director')),
                         'actors': process_imdb_data(imdb_data.get('Actors')),
                         'genre': process_imdb_data(imdb_data.get('Genre')),
                         'imdb_rating': process_imdb_data(imdb_data.get('imdbRating'))}
                return movie

        def get_movie_from_tmdb(id):
            def get_poster(poster):
                if poster:
                    return poster.filename

            def get_trailers(movie):
                youtube_trailers = []
                for trailer in movie.youtube_trailers:
                    t = {'name': trailer.name, 'source': trailer.source}
                    youtube_trailers.append(t)
                apple_trailers = []
                for trailer in movie.apple_trailers:
                    trailers = []
                    i = 0
                    for size in trailer.sources:
                        tr = {'size': size, 'source': trailer.sources[size].source}
                        trailers.append(tr)
                        i += 1
                    apple_trailers.append({'name': trailer.name, 'sizes': trailers})
                trailers = {'youtube': youtube_trailers, 'quicktime': apple_trailers}
                return trailers
            try:
                result = tmdb3.Movie(id)
            except:
                return
            if not result.releasedate:
                date = None
            else:
                date = result.releasedate
                if result.imdb == 'tt0019387':  # X-files Fight the future hack
                    result.imdb = 'tt0120902'   # -----------
            movie = {
                'tmdb_id': id,
                'imdb_id': result.imdb,
                'release_date': date,
                'title': result.originaltitle,
                'poster': get_poster(result.poster),
                'homepage': result.homepage,
                'trailers': get_trailers(result),
            }
            return movie
        movie_tmdb = get_movie_from_tmdb(id)
        if not movie_tmdb['imdb_id']:
            return -1                                         # returns -1 if there is a problem obtaining data from TMDB
        movie_imdb = get_movie_from_imdb(movie_tmdb['imdb_id'])
        if not movie_imdb:
            return -2                                         # returns -2 if there is a problem obtaining data from OMDB
        movie = dict(movie_tmdb.items() + movie_imdb.items())
        return save_movie_to_db(movie)
    id = check_if_movie_exists_in_db(movie_id)
    if not id:
        id = add_movie_to_db(movie_id)
    if id > 0:
        add_movie_to_list(id, list_id, user)
    else:
        return id


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
                url = settings.NO_POSTER_IMAGE_URL
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
                        'title': result.originaltitle,
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
