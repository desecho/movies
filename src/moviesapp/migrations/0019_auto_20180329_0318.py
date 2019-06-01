# Generated by Django 2.0.3 on 2018-03-29 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0018_record_watched_in_4k'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='learned_words',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='record',
            name='watched_in_full_hd',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='record',
            name='watched_in_hd',
            field=models.BooleanField(default=False),
        ),
    ]