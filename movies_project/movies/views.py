# -*- coding: utf8 -*-

import json
import tmdb3
from operator import itemgetter
import urllib2
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from movies.models import Movie, Record, List, User
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings


tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def search(request):
    return render_to_response('search.html')


@render_to('list.html')
@login_required
def list(request, list, username=None):
    if username:
        user_id = User.objects.get(username=username).id
    else:
        user_id = request.user.id
    records = Record.objects.filter(list__key_name=list, user_id=user_id)
    return {'records': records,
            'list_id': List.objects.get(key_name=list).id,
            'list_name': List.objects.get(key_name=list),
            'mode': request.session.get('mode', 'full'),
            'anothers_account': username,
            'number_of_movies': len(records)}


@render_to('people.html')
@login_required
def people(request):
    users = User.objects.all()
    users_new = []
    for user in users:
        u = {'username': user.username,
             'number_of_watched': Record.objects.filter(list_id=1, user=user).count(),
             'number_of_want_to_watch': Record.objects.filter(list_id=2, user=user).count()}
        users_new.append(u)
    return {'users': users_new}


def ajax_apply_setting(request):
    if request.is_ajax() and request.method == 'POST':
            POST = request.POST
            if 'mode' in POST:
                mode = POST.get('mode')
                request.session['mode'] = mode
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
def ajax_search_movie(request):
    def getMoviesFromTmdb(query, type, options):
        output = {}

        def setProperDate(movies):
            def formatDate(date):
                if date:
                    return date.strftime("%d.%m.%y")
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
            '''Types - 1 - movie, 2 - actor, 3 - director'''
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
            except IndexError:                                              # strange exception in "matrix case"
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
                response = urllib2.urlopen("http://www.imdbapi.com/?i=%s" % id)
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
            return -1                                         # return -1 if no imdb ID
        movie_imdb = getMovieFromImdb(movie_tmdb['imdb_id'])
        if not movie_imdb:
            return -2                                         # return -2 if couldn't retreve imdb ID
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
