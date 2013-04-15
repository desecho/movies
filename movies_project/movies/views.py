# -*- coding: utf8 -*-

#from django.views.decorators.cache import cache_page
import tempfile
import os
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
from django.utils.http import urlquote
from django.http import HttpResponse
from django.shortcuts import redirect
from movies.models import Record, List, User, ActionRecord
from annoying.decorators import ajax_request, render_to
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from movies.functions import (get_friends, filter_movies_for_recommendation,
                              add_movie_to_list, add_to_list_from_db,
                              get_movies_from_tmdb)
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from dateutil.relativedelta import relativedelta

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


def get_record_movie_data(record_ids_and_movies):
    movies = [x[1] for x in record_ids_and_movies]
    record_ids_and_movies_dict = {}
    for x in record_ids_and_movies:
        record_ids_and_movies_dict[x[0]] = x[1]
    return (movies, record_ids_and_movies_dict)


def get_comments_and_ratings(record_ids_and_movies, user):
    movies, record_ids_and_movies_dict = get_record_movie_data(record_ids_and_movies)
    comments_and_ratings = Record.objects.filter(
        user__in=get_friends(user),
        list_id=1,
        movie_id__in=movies
    ).values_list('movie_id', 'comment', 'rating', 'user__vk_profile__photo',
                  'user__first_name', 'user__last_name', 'user__username')

    comments_and_ratings_dict = {}
    for x in comments_and_ratings:
        if x[1] or x[2]:
            if x[0] not in comments_and_ratings_dict:
                comments_and_ratings_dict[x[0]] = []
            data = {}
            if x[1]:
                data['comment'] = x[1]
            if x[2]:
                data['rating'] = x[2]
            data['avatar'] = x[3]
            data['full_name'] = x[4] + ' ' + x[5]
            data['username'] = x[6]
            comments_and_ratings_dict[x[0]].append(data)
    data = {}
    for record_id in record_ids_and_movies_dict:
        data[record_id] = comments_and_ratings_dict.get(record_ids_and_movies_dict[record_id], None)
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
        records = records.order_by('-rating', '-movie__imdb_rating', '-movie__release_date')
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
    def number_of_movies(list_id):
        return Record.objects.filter(list_id=list_id, user__username=username).count()
    return '<span title="Просмотрено">%d</span> / <span title="К просмотру">%d' % (number_of_movies(1), number_of_movies(2))


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
        movies, record_ids_and_movies_dict = get_record_movie_data(records.values_list('id', 'movie_id'))
        movie_ids_and_list_ids = Record.objects.filter(user=request.user, movie_id__in=movies).values_list('movie_id', 'list_id')

        movie_id_and_list_id_dict = {}
        for x in movie_ids_and_list_ids:
            movie_id_and_list_id_dict[x[0]] = x[1]

        list_data = {}
        for record_id in record_ids_and_movies_dict:
            list_data[record_id] = movie_id_and_list_id_dict.get(record_ids_and_movies_dict[record_id], 0)
        return list_data

    def sort_records(records, sort):
        if sort == 'release_date':
            records = records.order_by('-movie__release_date')
        elif sort == 'rating':
            if not username and list == 'to-watch':
                # sorting is changing here because there is no user rating yet.
                records = records.order_by('-movie__imdb_rating', '-movie__release_date')
            else:
                records = records.order_by('-rating', '-movie__release_date')
        else:
            records = records.order_by('-date')
        return records

    def get_records():
        'gets records for certain user and list'
        if username:
            user = anothers_account
        else:
            user = request.user
        return Record.objects.select_related().filter(list__key_name=list, user=user)

    def get_anothers_account():
        "returns User if it's another's account and False if it's not"
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
        movie_count = get_movie_count(username)
    else:
        list_data = None
        movie_count = get_movie_count(request.user.username)

    if not username and list == 'to-watch':
        comments_and_ratings = get_comments_and_ratings(records.values_list('id', 'movie_id'), request.user)
    else:
        comments_and_ratings = None
    records = paginate(records, request.GET.get('page'), settings.RECORDS_ON_PAGE)
    return {'records': records,
            'reviews': comments_and_ratings,
            'list_id': List.objects.get(key_name=list).id,
            'anothers_account': anothers_account,
            'movie_count': movie_count,
            'list_data': json.dumps(list_data)}


def get_avatar(photo):
    return photo or settings.VK_NO_IMAGE_SMALL


@render_to('feed.html')
@login_required
def feed(request, list):
    date_to = datetime.today()
    date_from = date_to - relativedelta(days=settings.FEED_DAYS)
    actions = ActionRecord.objects.filter(date__range=(date_from, date_to)).order_by('-pk')
    if list == 'friends':
        actions = actions.filter(user__in=get_friends(request.user))
    else:
        actions = actions.exclude(user=request.user)
    posters = [action.movie.poster_small_url for action in actions]
    actions = actions.values('user__vk_profile__photo', 'user__username', 'user__first_name',
                             'user__last_name', 'action__name', 'movie__title_ru', 'list__title',
                             'comment', 'rating', 'date')
    actions_output = []
    i = 0
    for action in actions:
        a = {}
        a['avatar'] = get_avatar(action['user__vk_profile__photo'])
        a['full_name'] = action['user__first_name'] + ' ' + action['user__last_name']
        a['username'] = action['user__username']
        a['action'] = action['action__name']
        a['movie'] = action['movie__title_ru']
        a['movie_poster'] = posters[i]
        a['list'] = action['list__title']
        a['comment'] = action['comment']
        a['rating'] = action['rating']
        a['date'] = action['date']
        actions_output.append(a)
        i += 1
    return {'actions': actions_output}


#@cache_page(settings.CACHE_TIMEOUT)
@render_to('people.html')
@login_required
def generic_people(request, users):
    users = users.values('first_name', 'last_name', 'username', 'vk_profile__photo')

    users_output = []
    for user in users:
        u = {}
        u['full_name'] = user['first_name'] + ' ' + user['last_name']
        u['username'] = user['username']
        u['avatar'] = get_avatar(user['vk_profile__photo'])
        u['movie_count'] = get_movie_count(user['username'])
        users_output.append(u)

    users = paginate(users_output, request.GET.get('page'), settings.PEOPLE_ON_PAGE)
    return {'users': users}


#@cache_page(settings.CACHE_TIMEOUT)
@login_required
def people(request):
    return generic_people(request, User.objects.all().order_by('first_name'))


#@cache_page(settings.CACHE_TIMEOUT)
@login_required
def friends(request):
    return generic_people(request, get_friends(request.user))


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
                    ActionRecord(action_id=4, user=request.user, movie=r.movie, comment=comment).save()
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
                    ActionRecord(action_id=3, user=request.user, movie=r.movie, rating=rating).save()
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
            html = html.replace('"items": {"list":[,{', '"items": {"list":[{')
            return {'data': html}


@ajax_request
def ajax_search_movie(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'query' in POST and 'type' in POST and 'options[popular_only]' in POST and 'options[sort_by_date]' in POST:
            query = POST.get('query')
            type = int(POST.get('type'))
            options = {'popular_only': int(POST.get('options[popular_only]')), 'sort_by_date': int(POST.get('options[sort_by_date]'))}
            output = get_movies_from_tmdb(query, type, options, request.user)
            return output


@ajax_request
def ajax_add_to_list_from_db(request):
    if request.is_ajax() and request.method == 'POST':
        POST = request.POST
        if 'movie_id' in POST and 'list_id' in POST:
            error_code = add_to_list_from_db(int(POST.get('movie_id')), int(POST.get('list_id')), request.user)
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
        poster_url = movie.poster_huge_url()
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
