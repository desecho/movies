# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.db import migrations, models


def load_fixtures(apps, schema_editor):
    call_command('loaddata', 'lists', app_label='moviesapp')
    call_command('loaddata', 'actions', app_label='moviesapp')


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0010_auto_20170418_0137'),
    ]

    operations = [migrations.RunPython(load_fixtures)]
