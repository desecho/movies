# Generated by Django 4.2.7 on 2023-11-03 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("moviesapp", "0036_user_hidden_alter_user_only_for_friends"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vkcountry",
            options={"verbose_name": "VK country", "verbose_name_plural": "VK countries"},
        ),
    ]
