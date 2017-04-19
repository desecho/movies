# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from tabulate import tabulate

from ...models import Movie

ALLOWED_CHARS = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ123456789 -:0,"«».?+/–º·№!()½⅓\''


class Command(BaseCommand):
    help = 'Displays wrong russian titles'

    def handle(self, *args, **options):
        ids_to_ignore = [1989, 1873, 1756, 1569, 1296, 931, 845, 376, 406]
        rows = []
        for movie in Movie.objects.exclude(pk__in=ids_to_ignore):
            for letter in movie.title_ru:
                if letter not in ALLOWED_CHARS:
                    rows.append((movie.id, movie.title_ru, movie.title_original))
                    break
        headers = ('Id', 'Title (ru)', 'Title (eng)')
        self.stdout.write(tabulate(rows, headers, 'fancy_grid'))
        self.stdout.write('Total: %d' % len(rows))
