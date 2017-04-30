# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import pytest
from django.core.urlresolvers import reverse

from .base import BaseTestCase


class SearchMoviesAnonymousTestCase(BaseTestCase):
    response_type_movie = None
    response_type_movie_popular = None
    response_type_movie_sorted = None

    def test_search_view(self):
        url = reverse('search')
        response = self.client.get(url)
        soup = self.get_soup(response)
        self.assertTrue(soup.find('form', id='search'))

    @pytest.fixture(autouse=True)
    def run_requests(self, mocker, client):
        def get_response(type_, options, mocktype):
            if mocktype == 'movie':
                mockfile = 'search_movies-type_movie-tmdb.json'
            params = {
                'options': options,
                'query': 'matrix',
                'type': type_,
            }
            tmdbsimple_movie = mocker.patch('tmdbsimple.search.Search.movie')
            tmdbsimple_movie.return_value = self.load_json(mockfile)
            response = client.get(url, params)
            return self.get_json(response)

        url = reverse('search_movie')
        self.response_type_movie = get_response('movie', 'popularOnly=false&sortByDate=false', 'movie')
        self.response_type_movie_popular = get_response('movie', 'popularOnly=true&sortByDate=false', 'movie')
        self.response_type_movie_sorted = get_response('movie', 'popularOnly=false&sortByDate=true', 'movie')
        # TODO
        # self.response_type_actor = get_response('actor', 'popularOnly=false&sortByDate=false',
        #     'search_movies-type_people-tmdb.json')

    def test_type_movie(self):
        self.assertEqual(self.response_type_movie['status'], 'success')
        self.assertEqual(self.response_type_movie['movies'], self.load_json('search_movies-type_movie.json'))

    def test_type_movie_popular(self):
        self.assertEqual(self.response_type_movie_popular['status'], 'success')
        self.assertEqual(self.response_type_movie_popular['movies'],
                         self.load_json('search_movies-type_movie-popular.json'))

    def test_type_movie_sorted(self):
        self.assertEqual(self.response_type_movie_sorted['status'], 'success')
        self.assertEqual(self.response_type_movie_sorted['movies'],
                         self.load_json('search_movies-type_movie-sorted.json'))

    # TODO
    # def test_type_actor(self):
    #     self.assertEqual(self.response_type_actor['status'], 'success')
    #     print json.dumps(self.response_type_actor['movies'])
    #     self.assertEqual(self.response_type_actor['status'], '')
    #     self.assertEqual(self.response_type_actor['movies'], self.load_json('search_movies-type_movie.json'))


class AddMoviesTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.client.logout()

    def test_add_movie(self):
        LIST_ID = 1
        MOVIE_ID = 603
        self.login()
        url = reverse('add_to_list_from_db')
        params = {
            'movieId': MOVIE_ID,
            'listId': LIST_ID,
        }
        # TODO Mock tmdbsimple
        response = self.client.post(url, params)
        response = self.get_json(response)
        self.assertEqual(response['status'], 'success')
        record = self.user.get_records().first()
        self.assertEqual(record.list.pk, LIST_ID)
        self.assertEqual(json.loads(self.dump_instance(record.movie)), self.load_json('add_movies_matrix.json'))
