# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import tempfile
# import logging
import urllib2
from datetime import datetime

from annoying.decorators import ajax_request, render_to
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from .models import (ActionRecord, List, Record, User,
                     activate_user_language_preference)
from .search import get_movies_from_tmdb
from .social import Fb, Vk
from .utils import add_movie_to_list, add_to_list_from_db


# logger = logging.getLogger('moviesapp.test')
# logger.debug(options)


def get_friends(user):
    if user.is_linked:
        friends = User.objects.none()
        if user.is_vk_user():
            friends |= Vk(user).get_friends()
        if user.is_fb_user():
            friends |= Fb(user).get_friends()
        return friends


def filter_movies_for_recommendation(records, user):
    """Keep movies only with 3+ rating, removes watched movies."""
    return records.filter(rating__gte=3).exclude(movie__in=user.get_movie_ids())


def logout_view(request):
    logout(request)
    return redirect('/login/')


@ensure_csrf_cookie  # for vk
@render_to('search.html')
@login_required
def search(request):  # pylint: disable=unused-argument
    return {}


@render_to('preferences.html')
@login_required
def preferences(request):  # pylint: disable=unused-argument
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
        comments_and_ratings = comments_and_ratings.filter(user__in=friends)

    comments_and_ratings_dict = {}
    for x in comments_and_ratings:
        if x.comment or x.rating:
            data = {
                'user': x.user
            }
            if x.movie.pk not in comments_and_ratings_dict:
                comments_and_ratings_dict[x.movie.pk] = []
            if x.comment:
                data['comment'] = x.comment
            if x.rating:
                data['rating'] = x.rating
            comments_and_ratings_dict[x.movie.pk].append(data)
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
        records = Record.objects.exclude(user=request.user).filter(user__in=friends).select_related()
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
        if 'language' in POST:
            user = User.objects.get(pk=request.user.pk)
            user.language = POST['language']
            user.only_for_friends = json.loads(POST.get('onlyForFriends', 'false'))
            user.save()
            activate_user_language_preference(request, POST['language'])
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


@login_required
def list_username(request, list_name, username=None):
    if User.objects.get(username=username) in get_available_users_and_friends(request.user):
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
        movie_ids_and_list_ids = (Record.objects
                                  .filter(user=request.user, movie_id__in=movies)
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
        elif sort == 'addition_date':
            records = records.order_by('-date')
        return records

    def get_records():
        """Get records for certain user and list."""
        if username:
            user = anothers_account
        else:
            user = request.user
        return Record.objects.select_related().filter(list__key_name=list_name,
                                                      user=user)

    def get_anothers_account():
        """Return User if it's another's account and False if it's not."""
        if username:
            anothers_account = User.objects.get(username=username)
        else:
            anothers_account = False
        return anothers_account

    def search_records(query):
        return records.filter(Q(movie__title_en__icontains=query) |
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
    else:
        list_data = None

    if not username and list_name == 'to-watch' and records:
        comments_and_ratings = get_comments_and_ratings(records.values_list('id', 'movie_id'), request.user)
    else:
        comments_and_ratings = None
    records = paginate(records, request.GET.get('page'),
                       settings.RECORDS_ON_PAGE)
    return {'records': records,
            'reviews': comments_and_ratings,
            'list_id': List.objects.get(key_name=list_name).id,
            'anothers_account': anothers_account,
            'list_data': json.dumps(list_data)}


def get_available_users_and_friends(user, sort=False):
    def available_users():
        return [u for u in User.objects.exclude(pk=user.pk, only_for_friends=True)]

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
        'people': _('People'),
        'friends': _('Friends'),
    }

    date_to = datetime.today()
    date_from = date_to - relativedelta(days=settings.FEED_DAYS)
    actions = ActionRecord.objects.filter(
        date__range=(date_from, date_to)).order_by('-pk')
    if list_name == 'friends':
        actions = actions.filter(user__in=get_friends(request.user))
    else:
        actions = actions.filter(user__in=get_available_users_and_friends(request.user))

    posters = [action.movie.poster_small for action in actions]
    actions_output = []

    i = 0
    for action in actions:
        a = {
            'user': action.user,
            'action': action,
            'movie': action.movie,
            'movie_poster': posters[i],
            'list': action.list,
            'comment': action.comment,
            'rating': action.rating,
            'date': action.date,
        }
        actions_output.append(a)
        i += 1
    return {'list_name': FEED_TITLE[list_name],
            'actions': actions_output}


# @cache_page(settings.CACHE_TIMEOUT)
@render_to('people.html')
@login_required
def generic_people(request, users):
    return {'users': paginate(users, request.GET.get('page'),
                              settings.PEOPLE_ON_PAGE)}


# @cache_page(settings.CACHE_TIMEOUT)
@login_required
def people(request):
    return generic_people(request, get_available_users_and_friends(user=request.user,
                                                                   sort=True))


# @cache_page(settings.CACHE_TIMEOUT)
@login_required
def friends(request):
    return generic_people(request, get_friends(request.user).order_by('first_name'))


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
            id_ = POST.get('id')
            Record.objects.get(pk=id_, user_id=request.user.id).delete()
    return HttpResponse()


def ajax_save_comment(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'id' in POST and 'comment' in POST:
            id_ = POST.get('id')
            comment = POST.get('comment')
            r = Record.objects.get(pk=id_, user=request.user)
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
            id_ = POST.get('id')
            rating = POST.get('rating')
            r = Record.objects.get(pk=id_, user=request.user)
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
    if request.method == 'GET':
        type_ = int(request.GET.get('type'))
        query = request.GET.get('query')
        options = QueryDict(request.GET['options'])
        options = {'popular_only': json.loads(options['popularOnly']),
                   'sort_by_date': json.loads(options['sortByDate'])}
        output = get_movies_from_tmdb(query, type_, options, request.user)
        return output


@ajax_request
def ajax_add_to_list_from_db(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movieId' in POST and 'listId' in POST:
            error_code = add_to_list_from_db(int(POST.get('movieId')),
                                             int(POST.get('listId')),
                                             request.user)
            if error_code:
                return {'status': error_code}
    return HttpResponse()


def ajax_add_to_list(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movieId' in POST and 'listId' in POST:
            movie_id = POST.get('movieId')
            list_id = POST.get('listId')
            add_movie_to_list(movie_id, list_id, request.user)
    return HttpResponse()


@ajax_request
def ajax_upload_photo_to_wall(request):
    def get_filepath(record_id):
        movie = Record.objects.get(pk=record_id).movie
        file_contents = urllib2.urlopen(movie.poster_big).read()
        path = tempfile.mkstemp()[1]
        with open(path, 'w') as file_:
            file_.write(file_contents)
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
        if 'url' in POST and 'recordId' in POST:
            filepath = get_filepath(POST.get('recordId'))
            response = upload_file(POST.get('url'), filepath)
            return {'response': response}
    return HttpResponse()
