# -*- coding: utf8 -*-
from __future__ import unicode_literals

# from django.views.decorators.cache import cache_page
import tempfile
import os
import json
import vkontakte
# import logging
import urllib2
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

# from django.utils.http import urlquote
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from annoying.decorators import ajax_request, render_to

from .models import Record, List, User, ActionRecord, get_poster_url
from .functions import add_movie_to_list, add_to_list_from_db, tmdb


# logger = logging.getLogger('moviesapp.test')
# logger.debug(options)


def get_friends(user):
    if user.is_vk_user():
        vk = vkontakte.API(settings.VK_APP_ID, settings.VK_APP_SECRET)
        friends = vk.friends.get(uid=user.username)
        friends = map(str, friends)
        return User.objects.filter(username__in=friends)


def filter_movies_for_recommendation(records, user):
    'Keeps movies only with 3+ rating, removes watched movies'
    return records.filter(rating__gte=3) \
                  .exclude(movie__in=user.get_movie_ids())


def logout_view(request):
    logout(request)
    return redirect('/login/')


@ensure_csrf_cookie       # CSRF thing for vk
@render_to('search.html')
@login_required
def search(request):
    return {}


def get_record_movie_data(record_ids_and_movies):
    movies = [x[1] for x in record_ids_and_movies]
    return (movies, {x[0]: x[1] for x in record_ids_and_movies})


def get_comments_and_ratings(record_ids_and_movies, user):
    movies, record_ids_and_movies_dict = get_record_movie_data(
        record_ids_and_movies)
    comments_and_ratings = Record.objects.filter(
        list_id=1,
        movie_id__in=movies
    )
    friends = get_friends(user)
    if friends is None:
        comments_and_ratings = []
    else:
        comments_and_ratings = comments_and_ratings.filter(user__in=friends).values(
            'movie_id', 'comment', 'rating', 'user__vk_profile__photo',
            'user__first_name', 'user__last_name', 'user__username')

    comments_and_ratings_dict = {}
    for x in comments_and_ratings:
        if x['comment'] or x['rating']:
            if x['movie_id'] not in comments_and_ratings_dict:
                comments_and_ratings_dict[x['movie_id']] = []
            data = {}
            if x['comment']:
                data['comment'] = x['comment']
            if x['rating']:
                data['rating'] = x['rating']
            data['avatar'] = x['user__vk_profile__photo']
            data['full_name'] = '%s %s' % (x['user__first_name'],
                                           x['user__last_name'])
            data['username'] = x['user__username']
            comments_and_ratings_dict[x['movie_id']].append(data)
    data = {}
    for record_id, value in record_ids_and_movies_dict.items():
        data[record_id] = comments_and_ratings_dict.get(value, None)
    return data


@render_to('recommendation.html')
@login_required
def recommendation(request):
    def get_recommendations_from_friends():
        def filter_duplicated_movies_and_limit(records):
            records_output = []
            movies = []
            record_ids_and_movies = []
            for record in records:
                if record.movie.pk not in movies:
                    records_output.append(record)
                    record_ids_and_movies.append((record.pk, record.movie.pk))
                    if len(records_output) == settings.MAX_RECOMMENDATIONS:
                        break
                    movies.append(record.movie.pk)
            return (records_output, record_ids_and_movies)
        # exclude own records and include only friends' records
        records = Record.objects.exclude(user=request.user) \
            .filter(user__in=friends).select_related()
        # order records by user rating and by imdb rating
        records = records.order_by('-rating', '-movie__imdb_rating',
                                   '-movie__release_date')
        records = filter_movies_for_recommendation(records, request.user)
        return filter_duplicated_movies_and_limit(records)

    friends = get_friends(request.user)
    if friends:
        records, record_ids_and_movies = get_recommendations_from_friends()
        reviews = get_comments_and_ratings(record_ids_and_movies, request.user)
    else:
        records = None
        reviews = None
    return {'records': records, 'reviews': reviews}


def ajax_save_preferences(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'lang' in POST:
            user = User.objects.get(pk=request.user.pk)
            user.preferences = POST
            user.save()
            return HttpResponse()


def paginate(objects, page, objects_on_page):
    paginator = Paginator(objects, objects_on_page)
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)
    return objects


def get_movie_count(username):
    LIST_IDS = {'watched': 1, 'to_watch': 2}

    def create_span_tag(title, list_id):
        def number_of_movies():
            return Record.objects.filter(list_id=list_id,
                                         user__username=username).count()

        return '<span title="%s">%d</span>' % (title, number_of_movies())

    watched = create_span_tag('Просмотрено', LIST_IDS['watched'])
    to_watch = create_span_tag('К просмотру', LIST_IDS['to_watch'])
    return '%s / %s' % (watched, to_watch)


@login_required
def list_username(request, list_name, username=None):
    if User.objects.get(username=username) in \
            get_available_users_and_friends(request.user):
        return list_view(request, list_name, username)


@render_to('list.html')
@login_required
def list_view(request, list_name, username=None):
    def initialize_session_values():
        if 'sort' not in request.session:
            request.session['sort'] = 'addition_date'
        if 'recommendation' not in request.session:
            request.session['recommendation'] = False
        if 'mode' not in request.session:
            request.session['mode'] = 'full'

    def get_list_data(records):
        movies, record_ids_and_movies_dict = get_record_movie_data(
            records.values_list('id', 'movie_id'))
        movie_ids_and_list_ids = (Record.objects.filter(user=request.user, movie_id__in=movies)
                                                .values_list('movie_id', 'list_id'))

        movie_id_and_list_id_dict = {}
        for x in movie_ids_and_list_ids:
            movie_id_and_list_id_dict[x[0]] = x[1]

        list_data = {}
        for record_id, value in record_ids_and_movies_dict.items():
            list_data[record_id] = movie_id_and_list_id_dict.get(value, 0)
        return list_data

    def sort_records(records, sort):
        if sort == 'release_date':
            records = records.order_by('-movie__release_date')
        elif sort == 'rating':
            if not username and list_name == 'to-watch':
                # sorting is changing here because there is no user rating yet.
                records = records.order_by('-movie__imdb_rating',
                                           '-movie__release_date')
            else:
                records = records.order_by('-rating', '-movie__release_date')
        else:
            records = records.order_by('-date')
        return records

    def get_records():
        'Gets records for certain user and list'
        if username:
            user = anothers_account
        else:
            user = request.user
        return Record.objects.select_related().filter(list__key_name=list_name,
                                                      user=user)

    def get_anothers_account():
        """Returns User if it's another's account and False if it's not"""
        if username:
            anothers_account = User.objects.get(username=username)
        else:
            anothers_account = False
        return anothers_account

    def search_records(query):
        return records.filter(Q(movie__title__icontains=query) |
                              Q(movie__title_ru__icontains=query))

    initialize_session_values()
    anothers_account = get_anothers_account()
    records = get_records()
    if request.POST.get('search', False):
        records = search_records(request.POST['search'])
    records = sort_records(records, request.session['sort'])

    if username and request.session['recommendation']:
        records = filter_movies_for_recommendation(records, request.user)

    if username:
        list_data = get_list_data(records)
        movie_count = get_movie_count(username)
    else:
        list_data = None
        movie_count = get_movie_count(request.user.username)

    if not username and list_name == 'to-watch' and records:
        comments_and_ratings = get_comments_and_ratings(
            records.values_list('id', 'movie_id'), request.user)
    else:
        comments_and_ratings = None
    records = paginate(records, request.GET.get('page'),
                       settings.RECORDS_ON_PAGE)
    return {'records': records,
            'reviews': comments_and_ratings,
            'list_id': List.objects.get(key_name=list_name).id,
            'anothers_account': anothers_account,
            'movie_count': movie_count,
            'list_data': json.dumps(list_data)}


def get_avatar(photo):
    return photo or settings.VK_NO_IMAGE_SMALL


def get_available_users_and_friends(user, sort=False):
    def available_users():
        return [u for u in User.objects.exclude(pk=user.pk) if not
                u.preferences.get('only_for_friends', False)]

    def join(x, z):
        # convert to list doesn't work for some reason.
        # list(get_friends(request.user)) - error
        output = []
        for a in x:
            output.append(a)
        if z is not None:
            for a in z:
                output.append(a)
        return output

    def sort_users(users):
        def username(x):
            return x.first_name
        return sorted(users, key=username)

    users = set(join(available_users(), get_friends(user)))
    if sort:
        users = sort_users(users)
    return users


@render_to('feed.html')
@login_required
def feed(request, list_name):
    FEED_TITLE = {
        'people': 'Люди',
        'friends': 'Друзья',
    }

    def get_title(action):
        if request.user.preferences['lang'] == 'en':
            return action['movie__title']
        else:
            return action['movie__title_ru']

    date_to = datetime.today()
    date_from = date_to - relativedelta(days=settings.FEED_DAYS)
    actions = ActionRecord.objects.filter(
        date__range=(date_from, date_to)).order_by('-pk')
    if list_name == 'friends':
        actions = actions.filter(user__in=get_friends(request.user))
    else:
        actions = actions.filter(
            user__in=get_available_users_and_friends(request.user))

    posters = [action.movie.get_poster(
        'small', request.user.preferences['lang']) for action in actions]
    actions = actions.values('user__vk_profile__photo', 'user__username',
                             'user__first_name', 'user__last_name',
                             'action__name', 'movie__title', 'movie__title_ru',
                             'list__title', 'comment', 'rating', 'date')
    actions_output = []

    i = 0
    for action in actions:
        full_name = '%s %s' % (action['user__first_name'],
                               action['user__last_name'])
        a = {
            'avatar': get_avatar(action['user__vk_profile__photo']),
            'full_name': full_name,
            'username': action['user__username'],
            'action': action['action__name'],
            'movie': get_title(action),
            'movie_poster': posters[i],
            'list': action['list__title'],
            'comment': action['comment'],
            'rating': action['rating'],
            'date': action['date'],
        }
        actions_output.append(a)
        i += 1
    return {'list_name': FEED_TITLE[list_name],
            'actions': actions_output}


# @cache_page(settings.CACHE_TIMEOUT)
@render_to('people.html')
@login_required
def generic_people(request, users):
    users_output = []
    for user in users:
        users_output.append({
            'full_name': user.get_full_name(),
            'username': user.username,
            'avatar': get_avatar(user.vk_profile.photo),
            'movie_count': get_movie_count(user.username)})
    return {'users': paginate(users_output, request.GET.get('page'),
            settings.PEOPLE_ON_PAGE)}


# @cache_page(settings.CACHE_TIMEOUT)
@login_required
def people(request):
    return generic_people(request,
                          get_available_users_and_friends(user=request.user,
                                                          sort=True))


# @cache_page(settings.CACHE_TIMEOUT)
@login_required
def friends(request):
    return generic_people(request,
                          get_friends(request.user).order_by('first_name'))


def ajax_apply_settings(request):
    if request.is_ajax() and request.method == 'POST':
            POST = request.POST
            if 'settings' in POST:
                session_settings = json.loads(POST.get('settings'))
                for setting in session_settings:
                    request.session[setting] = session_settings[setting]
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
            r = Record.objects.get(pk=id, user=request.user)
            if r.comment != comment:
                if not r.comment:
                    ActionRecord(action_id=4, user=request.user, movie=r.movie,
                                 comment=comment).save()
                r.comment = comment
                r.save()
    return HttpResponse()


def ajax_change_rating(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'id' in POST and 'rating' in POST:
            id = POST.get('id')
            rating = POST.get('rating')
            r = Record.objects.get(pk=id, user=request.user)
            if r.rating != rating:
                if not r.rating:
                    ActionRecord(action_id=3, user=request.user, movie=r.movie,
                                 rating=rating).save()
                r.rating = rating
                r.save()
    return HttpResponse()


# @ajax_request
# def ajax_download(request):
#     def get_url(query):
#         filter = urlquote(u'Íàéòè')
#         query = urlquote(query)
#         return 'http://2torrents.org/search/listjson?filters[title]=%s&filter=%s&sort=seeders&type=desc' % \
#             (query, filter)

#     if request.is_ajax() and request.method == 'POST':
#         POST = request.POST
#         if 'query' in POST:
#             url = get_url(POST.get('query'))
#             html = urllib2.urlopen(url).read()
#             html = html.replace('"items": {"list":[,{', '"items": {"list":[{')
#             return {'data': html}


@ajax_request
def ajax_search_movie(request):
    def get_movies_from_tmdb(query, type, options, user):
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
                movie['release_date'] = format_date(movie['release_date'])
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
                if movie['release_date']:
                    movies_with_date.append(movie)
                else:
                    movies_without_date.append(movie)
            movies_with_date = sorted(movies_with_date,
                                      key=itemgetter('release_date'), reverse=True)
            movies = movies_with_date + movies_without_date
            return movies

        def get_data(query, type):
            'For actor, director search - the first is used.'
            tmdb.set_locale(*settings.LOCALES[user.preferences['lang']])
            query = query.encode('utf-8')
            SEARCH_TYPES_IDS = {
                'movie': 1,
                'actor': 2,
                'director': 3,
            }
            if type == SEARCH_TYPES_IDS['movie']:
                try:
                    movies = tmdb.searchMovie(query)
                except:
                    return -1
            else:
                try:
                    result = tmdb.searchPerson(query)
                except:
                    return -1
                movies = []
                if len(result):
                    person = result[0]
                    if type == SEARCH_TYPES_IDS['actor']:
                        movies = person.roles
                    else:
                        for movie in person.crew:
                            if movie.job == 'Director':
                                movies.append(movie)
            return movies

        def get_title():
            if user.preferences['lang'] == 'en':
                return movie.originaltitle
            else:
                return movie.title

        output = {}
        movies_data = get_data(query, type)
        if movies_data == STATUS_CODES['error']:
            output['status'] = STATUS_CODES['error']
            return output
        movies = []
        i = 0

        if len(movies_data):
            try:
                for movie in movies_data:
                    i += 1
                    if i > settings.MAX_RESULTS:
                        break
                    # ignore movies if imdb not found
                    if Record.objects.filter(movie__tmdb_id=movie.id,
                                             user=user).exists() or not movie.imdb:
                        continue

                    movie = {
                        'id': movie.id,
                        'release_date': movie.releasedate,
                        'popularity': movie.popularity,
                        'title': get_title(),
                        'poster': get_poster_url('small', movie.poster),
                    }
                    movies.append(movie)
            except IndexError:         # strange exception in 'matrix case'
                pass
            if options['popular_only']:
                movies = remove_not_popular_movies(movies)
            if options['sort_by_date']:
                movies = sort_by_date(movies)
            # movies = sortByPopularity(movies)

            movies = set_proper_date(movies)
            if len(movies):
                output['status'] = STATUS_CODES['found']
                output['movies'] = movies
            else:
                output['status'] = STATUS_CODES['not found']
        else:
                output['status'] = STATUS_CODES['not found']
        return output
    if request.method == 'GET':
        type = int(request.GET.get('type'))
        query = request.GET.get('query')
        options = QueryDict(request.GET['options'])
        options = {'popular_only': json.loads(options['popular_only']),
                   'sort_by_date': json.loads(options['sort_by_date'])}
        output = get_movies_from_tmdb(query, type, options, request.user)
        return output


@ajax_request
def ajax_add_to_list_from_db(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        print POST
        if 'movie_id' in POST and 'list_id' in POST:
            error_code = add_to_list_from_db(int(POST.get('movie_id')),
                                             int(POST.get('list_id')),
                                             request.user)
            if error_code:
                return {'status': error_code}
    return HttpResponse()


def ajax_add_to_list(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            movie_id = POST.get('movie_id')
            list_id = POST.get('list_id')
            add_movie_to_list(movie_id, list_id, request.user)
    return HttpResponse()


@ajax_request
def ajax_upload_photo_to_wall(request):
    def get_filepath(record_id):
        movie = Record.objects.get(pk=record_id).movie
        poster_url = eval('movie.poster_%s_big_url()' %
                          request.user.preferences['lang'])
        file_contents = urllib2.urlopen(poster_url).read()
        path = tempfile.mkstemp()[1]
        file = open(path, 'w')
        file.write(file_contents)
        file.close()
        path_jpg = path + '.jpg'
        os.chmod(path, 0666)
        os.rename(path, path_jpg)
        return path_jpg

    def upload_file(url, filepath):
        register_openers()
        datagen, headers = multipart_encode({'photo': open(filepath, 'rb')})
        request = urllib2.Request(url, datagen, headers)
        response = urllib2.urlopen(request).read()
        return response

    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'url' in POST and 'record_id' in POST:
            filepath = get_filepath(POST.get('record_id'))
            response = upload_file(POST.get('url'), filepath)
            return {'response': response}
    return HttpResponse()
