import json

from raven.contrib.django.raven_compat.models import client

from moviesapp.exceptions import MovieNotInDb, NotAvailableSearchType
from moviesapp.models import Movie
from moviesapp.tmdb import get_movies_from_tmdb
from moviesapp.utils import add_movie_to_db

from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView
from .utils import add_movie_to_list


class SearchView(TemplateAnonymousView):
    template_name = 'search.html'


class SearchMovieView(AjaxAnonymousView):
    def get(self, request):
        AVAILABLE_SEARCH_TYPES = [
            'actor',
            'movie',
            'director',
        ]
        try:
            GET = request.GET
            query = GET['query']
            options = json.loads(GET['options'])
            type_ = GET['type']
            if type_ not in AVAILABLE_SEARCH_TYPES:
                raise NotAvailableSearchType
        except (KeyError, NotAvailableSearchType):
            return self.render_bad_request_response()
        movies = get_movies_from_tmdb(query, type_, options, request.user, self.request.LANGUAGE_CODE)
        return self.success(movies=movies)


class AddToListFromDbView(AjaxView):
    @staticmethod
    def _get_movie_id(tmdb_id):
        """Return movie id or None if movie is not found."""
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.id
        except Movie.DoesNotExist:
            return None

    @staticmethod
    def _add_to_list_from_db(movie_id, tmdb_id, list_id, user):
        """Return True on success and None of failure."""
        # If we don't find the movie in the db we add it to the database.
        if movie_id is None:
            try:
                movie_id = add_movie_to_db(tmdb_id)
            except MovieNotInDb:
                client.captureException()
                return None
        add_movie_to_list(movie_id, list_id, user)
        return True

    def post(self, request):
        try:
            POST = request.POST
            tmdb_id = int(POST['movieId'])
            list_id = int(POST['listId'])
        except (KeyError, ValueError):
            return self.render_bad_request_response()

        movie_id = self._get_movie_id(tmdb_id)
        result = self._add_to_list_from_db(movie_id, tmdb_id, list_id, request.user)
        if not result:
            output = {'status': 'not_found'}
            return self.render_json_response(output)
        return self.success()
