# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0008_user_loaded_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='name_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='action',
            name='name_ru',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
