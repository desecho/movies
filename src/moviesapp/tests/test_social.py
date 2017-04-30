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

    def test_feed_people(self):
        url = reverse('feed', args=('people',))
        response = self.client.get(url)
        soup = self.get_soup(response)
        records = soup.findAll('tr', {'class': 'feed-record'})
        self.assertEqual(len(records), 3)
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
        self.assertEqual(records_data[0], {
            'user': 'Thomas Anderson',
            'movie': 'Pulp Fiction',
            'action': 'To Watch'
        })
        self.assertEqual(records_data[1], {
            'user': 'Thomas Anderson',
            'movie': 'Dogma',
            'action': 'Watched'
        })
        self.assertEqual(records_data[2], {
            'user': 'Thomas Anderson',
            'movie': 'The Matrix',
            'action': 'Watched'
        })
