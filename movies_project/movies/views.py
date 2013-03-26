# -*- coding: utf8 -*-

import json
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
from movies.functions import (get_friends, filter_movies_for_recommendation,
                              add_movie_to_list, add_to_list_from_db)

import logging
logger = logging.getLogger('movies.test')
#logger.debug(options)

def logout_view(request):
    logout(request)
    return redirect('/login/')

@ensure_csrf_cookie       # CSRF thing for vk
@render_to('search.html')
@login_required
def search(request):
    return {}

@render_to('recommendation.html')
@login_required
def recommendation(request):
    def get_recommendations_from_friends():
        # exclude own records and include only friends' records
        records = Record.objects.exclude(user=request.user).filter(user__in=friends)
        # order records by user rating and by imdb rating
        records = records.order_by('-rating', '-movie__imdb_rating')
        return filter_movies_for_recommendation(records, request.user, settings.MAX_RECOMMENDATIONS)

    friends = get_friends(request.user)
    if friends:
        records = get_recommendations_from_friends()
    else:
        records = None
    return {'records': records}


@render_to('list.html')
@login_required
def list(request, list, username=None):
    def initialize_session_values():
        if 'sort' not in request.session:
            request.session['sort'] = 'addition_date'
        if 'recommendation' not in request.session:
            request.session['recommendation'] = False
        if 'mode' not in request.session:
            request.session['mode'] = 'full'

    def get_list_data(records):
        list_data = {}
        for record in records:
            list_data[record.pk] = request.user.get_list_id_from_movie_id(record.movie.pk)
        return list_data

    def sort_records(records, sort):
        if sort == 'release_date':
            records = records.order_by('-movie__release_date')
        elif sort == 'rating':
            records = records.order_by('-rating', '-movie__release_date')
        else:
            records = records.order_by('-pk')
        return records

    def get_records():
        'gets records for certain user and list'
        if username:
            user = anothers_account
        else:
            user = request.user
        return Record.objects.filter(list__key_name=list, user=user)

    def get_anothers_account():
        "returns User if it's another's acccount and False if it's not"
        if username:
            anothers_account = User.objects.get(username=username)
        else:
            anothers_account = False
        return anothers_account

    initialize_session_values()
    anothers_account = get_anothers_account()
    records = get_records()
    records = sort_records(records, request.session['sort'])

    if username and request.session['recommendation']:
        records = filter_movies_for_recommendation(records, request.user)

    if username:
        list_data = get_list_data(records)
    else:
        list_data = None

    return {'records': records,
            'list_id': List.objects.get(key_name=list).id,
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
    def get_movies_from_tmdb(query, type, options):
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
            output = get_movies_from_tmdb(query, type, options)
            return output

@ajax_request
def ajax_add_to_list_from_db(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            if add_to_list_from_db(POST.get('movie_id'), POST.get('list_id'), request.user):
                return {'status': id}
    return HttpResponse()


def ajax_add_to_list(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            movie_id = POST.get('movie_id')
            list_id = POST.get('list_id')
            add_movie_to_list(movie_id, list_id, request.user)
    return HttpResponse()
