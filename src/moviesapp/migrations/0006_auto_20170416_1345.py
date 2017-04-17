# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import annoying.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0005_auto_20160713_0122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={},
        ),
        migrations.AlterModelOptions(
            name='actionrecord',
            options={},
        ),
        migrations.AlterModelOptions(
            name='list',
            options={},
        ),
        migrations.AlterModelOptions(
            name='movie',
            options={'ordering': ['pk']},
        ),
        migrations.AlterModelOptions(
            name='record',
            options={},
        ),
        migrations.AlterField(
            model_name='action',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='action',
            field=models.ForeignKey(to='moviesapp.Action'),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='comment',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='list',
            field=models.ForeignKey(blank=True, to='moviesapp.List', null=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='movie',
            field=models.ForeignKey(to='moviesapp.Movie'),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='rating',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='list',
            name='key_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='list',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='movie',
            name='actors',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='country',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description_en',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description_ru',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='director',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='genre',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='homepage',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdb_id',
            field=models.CharField(unique=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdb_rating',
            field=models.DecimalField(null=True, max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='release_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='runtime',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title_original',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='tmdb_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='trailers',
            field=annoying.fields.JSONField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='writer',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='comment',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='list',
            field=models.ForeignKey(to='moviesapp.List'),
        ),
        migrations.AlterField(
            model_name='record',
            name='movie',
            field=models.ForeignKey(related_name='records', to='moviesapp.Movie'),
        ),
        migrations.AlterField(
            model_name='record',
            name='rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='record',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='only_for_friends',
            field=models.BooleanField(default=False),
        ),
    ]
