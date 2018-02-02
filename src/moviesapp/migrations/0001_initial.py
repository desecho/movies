# -*- coding: utf-8 -*-

import annoying.fields
import django.core.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name='superuser status')),
                ('username',
                 models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                  unique=True, max_length=30, verbose_name='username', validators=[
                         django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.',
                                                 verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True,
                                                  help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups',
                 models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True,
                                        help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.',
                                        verbose_name='groups')),
                ('user_permissions',
                 models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission',
                                        blank=True, help_text='Specific permissions for this user.',
                                        verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255,
                                          verbose_name=b'\xd0\xbd\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
            ],
            options={
                'verbose_name': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435',
                'verbose_name_plural': '\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActionRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=255, null=True,
                                             verbose_name=b'\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x80\xd0\xb8\xd0\xb9',
                                             blank=True)),
                ('rating', models.IntegerField(null=True,
                                               verbose_name=b'\xd1\x80\xd0\xb5\xd0\xb9\xd1\x82\xd0\xb8\xd0\xbd\xd0\xb3',
                                               blank=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name=b'\xd0\xb4\xd0\xb0\xd1\x82\xd0\xb0')),
                ('action', models.ForeignKey(
                    verbose_name=b'\xd1\x82\xd0\xb8\xd0\xbf \xd0\xb4\xd0\xb5\xd0\xb9\xd1\x81\xd1\x82\xd0\xb2\xd0\xb8\xd1\x8f',
                    to='moviesapp.Action', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f',
                'verbose_name_plural': '\u0437\u0430\u043f\u0438\u0441\u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255,
                                           verbose_name=b'\xd0\xbd\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
                ('key_name', models.CharField(max_length=255,
                                              verbose_name=b'\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb5 \xd0\xb8\xd0\xbc\xd1\x8f')),
            ],
            options={
                'verbose_name': '\u0441\u043f\u0438\u0441\u043e\u043a',
                'verbose_name_plural': '\u0441\u043f\u0438\u0441\u043a\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255,
                                           verbose_name=b'\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb3\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xbe\xd0\xb5 \xd0\xbd\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
                ('title_ru', models.CharField(max_length=255,
                                              verbose_name=b'\xd0\xbd\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
                ('overview', models.TextField(null=True,
                                              verbose_name=b'\xd0\xbe\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 (\xd1\x80\xd1\x83\xd1\x81)',
                                              blank=True)),
                ('plot', models.TextField(null=True,
                                          verbose_name=b'\xd0\xbe\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 (\xd0\xb0\xd0\xbd\xd0\xb3\xd0\xbb)',
                                          blank=True)),
                ('director', models.CharField(max_length=255, null=True,
                                              verbose_name=b'\xd1\x80\xd0\xb5\xd0\xb6\xd0\xb8\xd1\x81\xd1\x81\xd1\x91\xd1\x80',
                                              blank=True)),
                ('writer', models.CharField(max_length=255, null=True,
                                            verbose_name=b'\xd1\x81\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb0\xd1\x80\xd0\xb8\xd1\x81\xd1\x82',
                                            blank=True)),
                ('genre', models.CharField(max_length=255, null=True, verbose_name=b'\xd0\xb6\xd0\xb0\xd0\xbd\xd1\x80',
                                           blank=True)),
                ('actors', models.CharField(max_length=255, null=True,
                                            verbose_name=b'\xd0\xb0\xd0\xba\xd1\x82\xd1\x91\xd1\x80\xd1\x8b',
                                            blank=True)),
                ('imdb_id', models.CharField(unique=True, max_length=15, verbose_name=b'IMDB id')),
                ('tmdb_id', models.IntegerField(unique=True, verbose_name=b'TMDB id')),
                ('imdb_rating', models.DecimalField(null=True,
                                                    verbose_name=b'IMDB \xd1\x80\xd0\xb5\xd0\xb9\xd1\x82\xd0\xb8\xd0\xbd\xd0\xb3',
                                                    max_digits=2, decimal_places=1)),
                ('poster', models.CharField(max_length=255, null=True,
                                            verbose_name=b'\xd0\xbf\xd0\xbe\xd1\x81\xd1\x82\xd0\xb5\xd1\x80 (\xd0\xb0\xd0\xbd\xd0\xb3\xd0\xbb)')),
                ('release_date', models.DateField(null=True,
                                                  verbose_name=b'\xd0\xb4\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xb2\xd1\x8b\xd0\xbf\xd1\x83\xd1\x81\xd0\xba\xd0\xb0')),
                ('runtime', models.TimeField(null=True,
                                             verbose_name=b'\xd0\xb4\xd0\xbb\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c',
                                             blank=True)),
                ('homepage', models.URLField(null=True, verbose_name=b'\xd1\x81\xd0\xb0\xd0\xb9\xd1\x82', blank=True)),
                ('trailers', annoying.fields.JSONField(null=True,
                                                       verbose_name=b'\xd1\x82\xd1\x80\xd0\xb5\xd0\xb9\xd0\xbb\xd0\xb5\xd1\x80\xd1\x8b',
                                                       blank=True)),
            ],
            options={
                'ordering': ['pk'],
                'verbose_name': '\u0444\u0438\u043b\u044c\u043c',
                'verbose_name_plural': '\u0444\u0438\u043b\u044c\u043c\u044b',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.IntegerField(default=0,
                                               verbose_name=b'\xd1\x80\xd0\xb5\xd0\xb9\xd1\x82\xd0\xb8\xd0\xbd\xd0\xb3')),
                ('comment', models.CharField(default=b'', max_length=255,
                                             verbose_name=b'\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x80\xd0\xb8\xd0\xb9')),
                ('date', models.DateTimeField(auto_now_add=True,
                                              verbose_name=b'\xd0\xb4\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xb4\xd0\xbe\xd0\xb1\xd0\xb0\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8f')),
                ('list', models.ForeignKey(verbose_name=b'\xd1\x81\xd0\xbf\xd0\xb8\xd1\x81\xd0\xbe\xd0\xba',
                                           to='moviesapp.List', on_delete=models.CASCADE)),
                ('movie',
                 models.ForeignKey(related_name=b'records', verbose_name=b'\xd1\x84\xd0\xb8\xd0\xbb\xd1\x8c\xd0\xbc',
                                   to='moviesapp.Movie', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(
                    verbose_name=b'\xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c',
                    to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': '\u0437\u0430\u043f\u0438\u0441\u044c',
                'verbose_name_plural': '\u0437\u0430\u043f\u0438\u0441\u0438',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='actionrecord',
            name='list',
            field=models.ForeignKey(verbose_name=b'\xd1\x81\xd0\xbf\xd0\xb8\xd1\x81\xd0\xbe\xd0\xba', blank=True,
                                    to='moviesapp.List', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actionrecord',
            name='movie',
            field=models.ForeignKey(verbose_name=b'\xd1\x84\xd0\xb8\xd0\xbb\xd1\x8c\xd0\xbc', to='moviesapp.Movie', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actionrecord',
            name='user',
            field=models.ForeignKey(
                verbose_name=b'\xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c',
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
