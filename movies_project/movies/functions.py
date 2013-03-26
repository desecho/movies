from movies.models import Movie, Record, User
from django.conf import settings
import vkontakte
import urllib2
import json
import tmdb3

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)


def get_movie_id_from_tmdb_from_imdb_id(id):
    try:
        return tmdb3.Movie.fromIMDB(id).id
    except:
        return


def get_friends(user):
    # ???
    # def intersect(list1, list2):
    #     return list(set(list1) & set(list2))
    def intersect(list1, list2):
        return [x for x in list1 if x in list2]

    def get_all_vk_ids():
        vk_ids = []
        for user in User.objects.all():
            if user.is_vk_user():
                vk_ids.append(int(user.username))
        return vk_ids

    def get_user_list_from_usernames(usernames):
        users = []
        for username in usernames:
            users.append(User.objects.get(username=username))
        return users

    vk = vkontakte.API(settings.VK_APP_ID, settings.VK_APP_SECRET)
    if user.is_vk_user():
        all_friends = vk.friends.get(uid=user.username)
        registered_vk_users = get_all_vk_ids()
        friends = intersect(all_friends, registered_vk_users)
        friends = get_user_list_from_usernames(friends)
    else:
        friends = None
    return friends

def filter_movies_for_recommendation(records, user, limit=settings.MAX_RECOMMENDATIONS_IN_LIST):
    'keeps movies only with 3+ rating, removes watched movies, removes duplicated records and limits the results'
    def filter_watched_movies(records):
        def filter_duplicated_movies_and_limit(records):
            records_output = []
            movies = []
            for record in records:
                if record.movie.pk not in movies:
                    records_output.append(record)
                    if len(records_output) == limit:
                        break
                    movies.append(record.movie.pk)
            return records_output
        # removes watched movies
        records = records.exclude(movie__in=user.get_movie_ids())
        records = filter_duplicated_movies_and_limit(records)
        return records
    # filters only 3+ ratied movies
    records = records.filter(rating__gte=3)
    records = filter_watched_movies(records)
    return records

def add_movie_to_list(id, list_id, user_id):
    try:
        r = Record.objects.get(movie_id=id, user_id=user_id)
        if r.list_id != list_id:
            r.list_id = list_id
            r.save()
    except:
        r = Record(movie_id=id, list_id=list_id, user_id=user_id)
        r.save()

def add_to_list_from_db(movie_id, list_id, user_id):
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
                'release_date'  : date,
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
        add_movie_to_list(id, list_id, user_id)
    else:
        return id
