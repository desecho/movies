# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0009_auto_20170418_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='list',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
