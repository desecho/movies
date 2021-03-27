# -*- coding: utf-8 -*-

from django_tqdm import BaseCommand
from tabulate import tabulate

from moviesapp.models import Movie

ALLOWED_CHARS = "абвгдеёжзийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ123456789 -:0,\"«».?+/–º·№!()½⅓'"


class Command(BaseCommand):
    help = "Displays wrong russian titles"

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        ids_to_ignore = [
            1989,
            1873,
            1756,
            1569,
            1296,
            931,
            845,
            376,
            406,
            450,
            1872,
            1622,
            1643,
            1614,
            1597,
            471,
            786,
            1153,
            1041,
            653,
        ]
        rows = []
        for movie in Movie.objects.exclude(pk__in=ids_to_ignore):
            for letter in movie.title_ru:
                if letter not in ALLOWED_CHARS:
                    rows.append((movie.id, movie.tmdb_id, movie.title_ru, movie.title_original))
                    break
        headers = ("Id", "TMDB Id", "Title (ru)", "Title (eng)")
        self.info(tabulate(rows, headers, "fancy_grid"))
        number_of_rows = len(rows)
        self.info(f"Total: {number_of_rows}")
