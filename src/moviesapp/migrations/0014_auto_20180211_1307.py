# Generated by Django 2.0.2 on 2018-02-11 18:07

import django.contrib.auth.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0013_auto_20170428_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionrecord',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='actions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='record',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='records', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('ru', 'Русский')], default='en', max_length=2),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='only_for_friends',
            field=models.BooleanField(
                default=False,
                help_text='Privacy setting. It indicates whether only your friends have access to your movie lists.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=150,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name='username'),
        ),
    ]
