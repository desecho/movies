# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import annoying.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='poster',
            new_name='poster_en',
        ),
        migrations.AddField(
            model_name='movie',
            name='country',
            field=models.CharField(max_length=255, null=True, verbose_name=b'\xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb0', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='movie',
            name='poster_ru',
            field=models.CharField(max_length=255, null=True, verbose_name=b'\xd0\xbf\xd0\xbe\xd1\x81\xd1\x82\xd0\xb5\xd1\x80 (\xd1\x80\xd1\x83\xd1\x81)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='preferences',
            field=annoying.fields.JSONField(default=b'{"lang": "ru"}', verbose_name=b'\xd0\xbd\xd0\xb0\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xb9\xd0\xba\xd0\xb8'),
            preserve_default=True,
        ),
    ]
