# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.db import migrations


def load_fixtures(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('moviesapp', '0010_auto_20170418_0137'),
    ]

    operations = [migrations.RunPython(load_fixtures)]
