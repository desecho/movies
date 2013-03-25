# -*- coding: utf8 -*-

import json
import tmdb3
import vkontakte
from operator import itemgetter
import urllib2
from django.utils.http import urlquote
from django.http import HttpResponse
from django.shortcuts import redirect
from movies.models import Movie, Record, List, User
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)


def logout_view(request):
    logout(request)
    return redirect('/login/')

@ensure_csrf_cookie       # CSRF thing for vk
@render_to('search.html')
@login_required
def search(request):
    return {}

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
    def filter_watched_movies(records):
        records_output = []
        movies_watched = user.get_movie_ids()
        for record in records:
            if record.movie.pk not in movies_watched:
                records_output.append(record)
                if len(records_output) == limit:
                    break
        return records_output

    records = records.filter(rating__gte=3)  # get only normal, good and excellent ratied movies
    records = filter_watched_movies(records)
    return records


@render_to('recommendation.html')
@login_required
def recommendation(request):
    friends = get_friends(request.user)
    if friends:
        records = Record.objects.exclude(user=request.user).filter(user__in=friends)
        records = records.order_by('-rating', '-movie__imdb_rating')
        records = filter_movies_for_recommendation(records, request.user, settings.MAX_RECOMMENDATIONS)
    else:
        records = None
    return {'records': records}


@render_to('list.html')
@login_required
def list(request, list, username=None):
    sort = request.session.get('sort', 'release_date')
    recommendation = request.session.get('recommendation', False)
    if username:
        user = User.objects.get(username=username)
        anothers_account = user
    else:
        user = request.user
        anothers_account = False
    records = Record.objects.filter(list__key_name=list, user=user)

    if sort == 'release_date':
        records = records.order_by('-movie__release_date')
    elif sort == 'rating':
        records = records.order_by('-rating', '-movie__release_date')
    else:
        records = records.order_by('-pk')

    if username and recommendation:
        records = filter_movies_for_recommendation(records, request.user)

    if username:
        list_data = {}
        for record in records:
            list_data[record.pk] = request.user.get_list_id_from_movie_id(record.movie.pk)
    else:
        list_data = None
    return {'records': records,
            'list_id': List.objects.get(key_name=list).id,
            'mode': request.session.get('mode', 'full'),
            'sort': sort,
            'recommendation': recommendation,
            'anothers_account': anothers_account,
            'list_data': json.dumps(list_data)}


@render_to('people.html')
@login_required
def people(request):
    return {'users': User.objects.all()}


@render_to('people.html')
@login_required
def friends(request):
    friends = get_friends(request.user)
    return {'users': friends}


def ajax_apply_settings(request):
    if request.is_ajax() and request.method == 'POST':
            POST = request.POST
            if 'settings' in POST:
                settings = json.loads(POST.get('settings'))
                for setting in settings:
                    request.session[setting] = settings[setting]
    return HttpResponse()


def ajax_remove_record(request):
    if request.is_ajax() and request.method == 'POST':
            POST = request.POST
            if 'id' in POST:
                id = POST.get('id')
                Record.objects.get(pk=id, user_id=request.user.id).delete()
    return HttpResponse()


def ajax_save_comment(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'id' in POST and 'comment' in POST:
            id = POST.get('id')
            comment = POST.get('comment')
            r = Record.objects.get(pk=id, user_id=request.user.id)
            if r.comment != comment:
                r.comment = comment
                r.save()
    return HttpResponse()


def ajax_change_rating(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'id' in POST and 'rating' in POST:
            id = POST.get('id')
            rating = POST.get('rating')
            r = Record.objects.get(pk=id, user_id=request.user.id)
            r.rating = rating
            r.save()
    return HttpResponse()


@ajax_request
def ajax_download(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'query' in POST:
            filter = urlquote(u'Íàéòè')
            query = urlquote(POST.get('query'))
            url = 'http://2torrents.org/search/listjson?filters[title]=%s&filter=%s&sort=seeders&type=desc' % (query, filter)
            html = urllib2.urlopen(url).read()
            html = html.replace('"items": {"list":[,{','"items": {"list":[{')
            return {'data': html}


@ajax_request
def ajax_search_movie(request):
    def getMoviesFromTmdb(query, type, options):
        output = {}

        def setProperDate(movies):
            def formatDate(date):
                if date:
                    return date.strftime('%d.%m.%y')
            m = []
            for movie in movies:
                movie['release_date'] = formatDate(movie['release_date'])
                m.append(movie)
            return movies

        # def sortByPopularity(movies):
        #     movies = sorted(movies, key=itemgetter('popularity'), reverse=True)
        #     for movie in movies:
        #         del movie['popularity']
        #     return movies
        def removeNotPopularMovies(movies):
            m = []
            for movie in movies:
                if movie['popularity'] > settings.MIN_POPULARITY:
                    del movie['popularity']
                    m.append(movie)
            if not m:                  # keep initial movie list if all are unpopular
                m = movies
            return m

        def sortByDate(movies):
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

        def getPosterUrl(poster):
            if poster:
                url = settings.POSTER_BASE_URL + settings.POSTER_SIZE_SMALL + '/' + poster.filename
            else:
                url = settings.NO_POSTER_IMAGE_URL
            return url

        def getData(query, type):
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

        results = getData(query, type)
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
                    movie = {
                        'id': result.id,
                        'release_date': result.releasedate,
                        'popularity': result.popularity,                    # for popularity sorting
                        'title': result.originaltitle,
                        'poster': getPosterUrl(result.poster),
                    }
                    movies.append(movie)
            except IndexError:                                              # strange exception in 'matrix case'
                pass
            if options['popular_only']:
                movies = removeNotPopularMovies(movies)
            if options['sort_by_date']:
                movies = sortByDate(movies)
            #movies = sortByPopularity(movies)

            movies = setProperDate(movies)
            output['status'] = 1
            output['movies'] = movies
        else:
            output['status'] = 0
        return output
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'query' in POST and 'type' in POST and 'options[popular_only]' in POST and 'options[sort_by_date]' in POST:
            query = POST.get('query')
            type = int(POST.get('type'))
            options = {'popular_only': int(POST.get('options[popular_only]')), 'sort_by_date': int(POST.get('options[sort_by_date]'))}
            output = getMoviesFromTmdb(query, type, options)
            return output


def addMovieToList(id, list_id, user_id):
    #used by ajax_add_to_list_from_tmdb and ajax_add_to_list
    try:
        r = Record.objects.get(movie_id=id, user_id=user_id)
        if r.list_id != list_id:
            r.list_id = list_id
            r.save()
    except:
        r = Record(movie_id=id, list_id=list_id, user_id=user_id)
        r.save()


@ajax_request
def ajax_add_to_list_from_tmdb(request):
    def checkIfMovieExistsInDb(id):
        try:
            movie = Movie.objects.get(tmdb_id=id)
            return movie.id
        except:
            return

    def addMovieToDb(id):
        def saveMovieToDb(movie):
            m = Movie(**movie)
            m.save()
            return Movie.objects.get(tmdb_id=movie['tmdb_id']).id

        def getMovieFromImdb(id):
            def processImdbData(data):
                if data != 'N/A':
                    return data
            try:
                response = urllib2.urlopen('http://www.imdbapi.com/?i=%s' % id)
            except:
                return
            html = response.read()
            imdb_data = json.loads(html)
            if imdb_data.get('Response') == 'True':
                movie = {'plot': processImdbData(imdb_data.get('Plot')),
                         'writer': processImdbData(imdb_data.get('Writer')),
                         'director': processImdbData(imdb_data.get('Director')),
                         'actors': processImdbData(imdb_data.get('Actors')),
                         'genre': processImdbData(imdb_data.get('Genre')),
                         'imdb_rating': processImdbData(imdb_data.get('imdbRating'))}
                return movie

        def getMovieFromTmdb(id):
            def getPoster(poster):
                if poster:
                    return poster.filename

            def getTrailers(movie):
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
                'poster': getPoster(result.poster),
                'homepage': result.homepage,
                'trailers': getTrailers(result),
            }
            return movie
        movie_tmdb = getMovieFromTmdb(id)
        if not movie_tmdb['imdb_id']:
            return -1                                         # return -1 if the IMDB id is not found
        movie_imdb = getMovieFromImdb(movie_tmdb['imdb_id'])
        if not movie_imdb:
            return -2                                         # return -2 if there is a problem obtaining data from OMDB
        movie = dict(movie_tmdb.items() + movie_imdb.items())
        return saveMovieToDb(movie)

    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            movie_id = POST.get('movie_id')
            list_id = POST.get('list_id')
            id = checkIfMovieExistsInDb(movie_id)
            if not id:
                id = addMovieToDb(movie_id)
            if id > 0:
                addMovieToList(id, list_id, request.user.id)
            else:
                return {'status': id}
    return HttpResponse()


def ajax_add_to_list(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            movie_id = POST.get('movie_id')
            list_id = POST.get('list_id')
            addMovieToList(movie_id, list_id, request.user.id)
    return HttpResponse()
