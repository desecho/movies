# Generated by Django 2.0.2 on 2018-02-11 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0014_auto_20180211_1307'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='avatar',
            new_name='avatar_big',
        ),
        migrations.AddField(
            model_name='user',
            name='avatar_small',
            field=models.URLField(blank=True, null=True),
        ),
    ]
