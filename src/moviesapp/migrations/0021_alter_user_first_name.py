# Generated by Django 3.2 on 2021-04-11 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("moviesapp", "0020_remove_record_learned_words"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
    ]