# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0007_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='loaded_initial_data',
            field=models.BooleanField(default=False),
        ),
    ]
