# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moviesapp", "0004_user_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="only_for_friends",
            field=models.BooleanField(default=False, verbose_name="only for friends"),
        ),
    ]
