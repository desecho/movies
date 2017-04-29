import json

from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseForbidden

from ..models import Action, ActionRecord, List, Record, User
from .mixins import (AjaxAnonymousView, AjaxView, TemplateAnonymousView,
                     TemplateView)
from .utils import add_movie_to_list, paginate


class ChangeRatingView(AjaxView):
    def post(self, request):
        try:
            POST = request.POST
            id_ = POST['id']
            rating = POST['rating']
        except KeyError:
            return self.render_bad_request_response()

        r = request.user.get_record(id_)
        if r.rating != rating:
            if not r.rating:
                ActionRecord(action_id=Action.ADDED_RATING,
                             user=request.user,
                             movie=r.movie,
                             rating=rating).save()
            r.rating = rating
            r.save()
        return HttpResponse()


class AddToListView(AjaxView):
    def post(self, request):
        try:
            POST = request.POST
            movie_id = int(POST['movieId'])
            list_id = int(POST['listId'])
        except (KeyError, ValueError):
            return self.render_bad_request_response()
        add_movie_to_list(movie_id, list_id, request.user)
        return self.render_json_response({'status': 'success'})


class RecordMixin(AjaxView):
    def post(self, request):
        try:
            POST = request.POST
            record_id = int(POST['id'])
        except (KeyError, ValueError):
            return self.render_bad_request_response()
        self.record = request.user.get_record(record_id)


class RemoveMovieView(RecordMixin):
    def post(self, request):
        super(RemoveMovieView, self).post(request)
        self.record.delete()
        return self.render_json_response({'status': 'success'})


class ApplySettingsView(AjaxAnonymousView):
    def post(self, request):
        try:
            POST = request.POST
            session_settings = json.loads(POST['settings'])
        except KeyError:
            return self.render_bad_request_response()

        for setting in session_settings:
            request.session[setting] = session_settings[setting]
        return HttpResponse()


class SaveCommentView(RecordMixin):
    def post(self, request):
        super(SaveCommentView, self).post(request)
        try:
            comment = request.POST['comment']
        except KeyError:
            return self.render_bad_request_response()

        r = self.record
        if r.comment != comment:
            if not r.comment:
                ActionRecord(action_id=Action.ADDED_COMMENT,
                             user=request.user,
                             movie=r.movie,
                             comment=comment).save()
            r.comment = comment
            r.save()
        return HttpResponse()


class ListView(TemplateAnonymousView):
    template_name = 'list/list.html'
    session = None
    anothers_account = None

    @staticmethod
    def _filter_records_for_recommendation(records, user):
        """Keep movies only with 3+ rating, removes watched movies."""
        return records.filter(rating__gte=3).exclude(movie__in=user.get_movie_ids())

    def _get_comments_and_ratings(self, record_ids_and_movies, user):
        movies, record_ids_and_movies_dict = self._get_record_movie_data(
            record_ids_and_movies)
        comments_and_ratings = Record.objects.filter(
            list_id=1,
            movie_id__in=movies
        )
        friends = user.get_friends()
        if friends is None:
            comments_and_ratings = []
        else:
            comments_and_ratings = comments_and_ratings.filter(user__in=friends)

        comments_and_ratings_dict = {}
        for x in comments_and_ratings:
            if x.comment or x.rating:
                data = {'user': x.user}
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

    @staticmethod
    def _get_anothers_account(username):
        if username:
            return User.objects.get(username=username)
        return False

    @staticmethod
    def _filter_records(records, query):
        return records.filter(Q(movie__title_en__icontains=query) |
                              Q(movie__title_ru__icontains=query))

    @staticmethod
    def _sort_records(records, sort, username, list_name):
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

    @staticmethod
    def _get_record_movie_data(record_ids_and_movies):
        movies = [x[1] for x in record_ids_and_movies]
        return (movies, {x[0]: x[1] for x in record_ids_and_movies})

    def _get_list_data(self, records):
        movies, record_ids_and_movies_dict = self._get_record_movie_data(
            records.values_list('id', 'movie_id'))
        movie_ids_and_list_ids = (self.request.user.get_records()
                                  .filter(movie_id__in=movies)
                                  .values_list('movie_id', 'list_id'))
        movie_id_and_list_id_dict = {}
        for x in movie_ids_and_list_ids:
            movie_id_and_list_id_dict[x[0]] = x[1]

        list_data = {}
        for record_id, value in record_ids_and_movies_dict.items():
            list_data[record_id] = movie_id_and_list_id_dict.get(value, 0)
        return list_data

    def _initialize_session_values(self):
        session = self.request.session
        if 'sort' not in session:
            session['sort'] = 'addition_date'
        if 'recommendation' not in session:
            session['recommendation'] = False
        if 'mode' not in session:
            session['mode'] = 'full'
        self.session = session

    def _get_records(self, list_name):
        """Get records for certain user and list."""
        if self.anothers_account:
            user = self.anothers_account
        else:
            user = self.request.user
        return user.get_records().filter(list__key_name=list_name).select_related('movie')

    def get_context_data(self, list_name, username=None):
        if username is None and self.request.user.is_anonymous():
            raise Http404
        self.anothers_account = self._get_anothers_account(username)
        if self.anothers_account:
            if User.objects.get(username=username) not in self.request.user.get_users():
                return HttpResponseForbidden()

        records = self._get_records(list_name)
        request = self.request
        session = self.session
        query = request.GET.get('query', False)
        if query:
            query = query.strip()
            records = self._filter_records(records, query)
        records = self._sort_records(records, session['sort'], username, list_name)

        if username and session['recommendation']:
            records = self._filter_records_for_recommendation(records, request.user)

        if username:
            list_data = self._get_list_data(records)
        else:
            list_data = None

        if not username and list_name == 'to-watch' and records:
            comments_and_ratings = self._get_comments_and_ratings(records.values_list('id', 'movie_id'), request.user)
        else:
            comments_and_ratings = None
        records = paginate(records, request.GET.get('page'),
                           settings.RECORDS_ON_PAGE)
        return {
            'records': records,
            'reviews': comments_and_ratings,
            'list_id': List.objects.get(key_name=list_name).id,
            'anothers_account': self.anothers_account,
            'list_data': json.dumps(list_data),
            'query': query,
        }

    def get(self, *args, **kwargs):
        self._initialize_session_values()
        return super(ListView, self).get(*args, **kwargs)


class RecommendationsView(TemplateView, ListView):
    template_name = 'list/recommendations.html'

    @staticmethod
    def _filter_duplicated_movies_and_limit(records):
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

    def _get_recommendations_from_friends(self, friends):
        # exclude own records and include only friends' records
        records = Record.objects.exclude(user=self.request.user).filter(user__in=friends).select_related('movie')
        # order records by user rating and by imdb rating
        records = records.order_by('-rating', '-movie__imdb_rating',
                                   '-movie__release_date')
        return self._filter_records_for_recommendation(records, self.request.user)

    def get_context_data(self):
        friends = self.request.user.get_friends()
        records = self._get_recommendations_from_friends(friends)
        records, record_ids_and_movies = self._filter_duplicated_movies_and_limit(records)
        reviews = self._get_comments_and_ratings(record_ids_and_movies, self.request.user)
        return {'records': records, 'reviews': reviews}

    def get(self, *args, **kwargs):
        has_friends = self.request.user.has_friends()
        if not has_friends:
            raise Http404
        return super(RecommendationsView, self).get(*args, **kwargs)
