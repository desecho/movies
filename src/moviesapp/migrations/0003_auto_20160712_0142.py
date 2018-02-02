# -*- coding: utf-8 -*-

import annoying.fields
import django.contrib.auth.models
import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0002_auto_20160710_1517'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='list',
            name='title',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='overview',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='plot',
        ),
        migrations.AddField(
            model_name='list',
            name='name',
            field=models.CharField(default='', max_length=255,
                                   verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movie',
            name='description',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='description_en',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='description_ru',
            field=models.TextField(null=True, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='poster',
            field=models.CharField(max_length=255, null=True, verbose_name='poster'),
        ),
        migrations.AddField(
            model_name='movie',
            name='title_en',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='movie',
            name='title_original',
            field=models.CharField(default='', max_length=255, verbose_name='original title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='action',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='action',
            field=models.ForeignKey(verbose_name='\u0442\u0438\u043f \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
                                    to='moviesapp.Action', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='comment',
            field=models.CharField(max_length=255, null=True,
                                   verbose_name='\u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439',
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='\u0434\u0430\u0442\u0430'),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='list',
            field=models.ForeignKey(verbose_name='\u0441\u043f\u0438\u0441\u043e\u043a', blank=True,
                                    to='moviesapp.List', null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='movie',
            field=models.ForeignKey(verbose_name='\u0444\u0438\u043b\u044c\u043c', to='moviesapp.Movie', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='rating',
            field=models.IntegerField(null=True, verbose_name='\u0440\u0435\u0439\u0442\u0438\u043d\u0433', blank=True),
        ),
        migrations.AlterField(
            model_name='actionrecord',
            name='user',
            field=models.ForeignKey(
                verbose_name='\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='list',
            name='key_name',
            field=models.CharField(max_length=255,
                                   verbose_name='\u043a\u043b\u044e\u0447\u0435\u0432\u043e\u0435 \u0438\u043c\u044f'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='actors',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0430\u043a\u0442\u0451\u0440\u044b',
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='country',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0441\u0442\u0440\u0430\u043d\u0430',
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='director',
            field=models.CharField(max_length=255, null=True,
                                   verbose_name='\u0440\u0435\u0436\u0438\u0441\u0441\u0451\u0440', blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='genre',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0436\u0430\u043d\u0440', blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='homepage',
            field=models.URLField(null=True, verbose_name='\u0441\u0430\u0439\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='imdb_rating',
            field=models.DecimalField(null=True, verbose_name='IMDB \u0440\u0435\u0439\u0442\u0438\u043d\u0433',
                                      max_digits=2, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster_en',
            field=models.CharField(max_length=255, null=True, verbose_name='poster'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='poster'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='release_date',
            field=models.DateField(null=True,
                                   verbose_name='\u0434\u0430\u0442\u0430 \u0432\u044b\u043f\u0443\u0441\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='runtime',
            field=models.TimeField(null=True,
                                   verbose_name='\u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c',
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='trailers',
            field=annoying.fields.JSONField(null=True, verbose_name='\u0442\u0440\u0435\u0439\u043b\u0435\u0440\u044b',
                                            blank=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='writer',
            field=models.CharField(max_length=255, null=True,
                                   verbose_name='\u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0441\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='comment',
            field=models.CharField(default='', max_length=255,
                                   verbose_name='\u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439'),
        ),
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateTimeField(auto_now_add=True,
                                       verbose_name='\u0434\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='record',
            name='list',
            field=models.ForeignKey(verbose_name='\u0441\u043f\u0438\u0441\u043e\u043a', to='moviesapp.List', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='record',
            name='movie',
            field=models.ForeignKey(related_name='records', verbose_name='\u0444\u0438\u043b\u044c\u043c',
                                    to='moviesapp.Movie', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='record',
            name='rating',
            field=models.IntegerField(default=0, verbose_name='\u0440\u0435\u0439\u0442\u0438\u043d\u0433'),
        ),
        migrations.AlterField(
            model_name='record',
            name='user',
            field=models.ForeignKey(
                verbose_name='\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c',
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group',
                                         blank=True,
                                         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                         verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                   max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$',
                                                                                                    'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.',
                                                                                                    'invalid')],
                                   help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                   unique=True, verbose_name='username'),
        ),
    ]
