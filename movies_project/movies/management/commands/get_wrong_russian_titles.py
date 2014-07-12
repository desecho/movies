# -*- coding: utf8 -*-
from movies.models import Movie
from django.core.management.base import BaseCommand

ALLOWED_CHARS = u'абвгдеёжзийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ123456789 -:0,"«».?+/–º·№!'


class Command(BaseCommand):
    help = 'Displays wrong russian titles'

    def handle(self, *args, **options):
        for movie in Movie.objects.all():
            for letter in movie.title_ru:
                if letter not in ALLOWED_CHARS:
                    print '%d - %s - %s' % (movie.id, movie.title_ru,
                                            movie.title)
                    break
