# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from .base import BaseTestLoginCase


class PeopleTestCase(BaseTestLoginCase):
    fixtures = [
        'users.json',
        'lists.json',
        'actions.json',
        'movies.json',
        'records.json',
        'action_records.json',
    ]

    def setUp(self):
        BaseTestLoginCase.setUp(self)
        self.login('fox')

    def test_people(self):
        url = reverse('people')
        response = self.client.get(url)
        soup = self.get_soup(response)
        records = soup.findAll('div', {'class': 'person'})
        users = []
        for record in records:
            users.append(record.find('a', {'class': 'people-user'}).get_text())
        self.assertListEqual(users, ['admin', 'Thomas Anderson'])

    def test_feed_people(self):
        url = reverse('feed', args=('people',))
        response = self.client.get(url)
        soup = self.get_soup(response)
        records = soup.findAll('tr', {'class': 'feed-record'})
        self.assertEqual(len(records), 7)
        records_data = []
        for record in records:
            user = record.find('td', {'class': 'feed-user'}).find('a').find('img').attrs['title'].strip()
            movie = record.find('td', {'class': 'feed-movie'}).get_text().strip()
            action = record.find('td', {'class': 'feed-action-data'}).get_text().strip()
            records_data.append({
                'user': user,
                'movie': movie,
                'action': action
            })
        self.assertIn({
            'user': 'Thomas Anderson',
            'movie': 'The X Files',
            'action': 'Watched'
        }, records_data)
        self.assertIn({
            'user': 'Thomas Anderson',
            'movie': 'Pulp Fiction',
            'action': 'To Watch'
        }, records_data)
        self.assertIn({
            'user': 'Thomas Anderson',
            'movie': 'Dogma',
            'action': 'Watched'
        }, records_data)
        self.assertIn({
            'user': 'Thomas Anderson',
            'movie': 'The Matrix',
            'action': 'Watched'
        }, records_data)
