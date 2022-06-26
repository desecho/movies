# Generated by Django 4.0.5 on 2022-06-26 17:47

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0034_vkcountry'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='US/Eastern'),
        ),
    ]