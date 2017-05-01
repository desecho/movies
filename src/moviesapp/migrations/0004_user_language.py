# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0003_auto_20160712_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(default='en', max_length=2, choices=[(b'en', 'English'), (b'ru', 'Russian')]),
        ),
    ]
