# -*- coding: utf-8 -*-

import annoying.fields
import django.core.validators
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(default=django.utils.timezone.now, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        unique=True,
                        max_length=30,
                        verbose_name="username",
                        validators=[
                            django.core.validators.RegexValidator("^[\\w.@+-]+$", "Enter a valid username.", "invalid")
                        ],
                    ),
                ),
                ("first_name", models.CharField(max_length=30, verbose_name="first name", blank=True)),
                ("last_name", models.CharField(max_length=30, verbose_name="last name", blank=True)),
                ("email", models.EmailField(max_length=75, verbose_name="email address", blank=True)),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "groups",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Group",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of his/her group.",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        related_query_name="user",
                        related_name="user_set",
                        to="auth.Permission",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Action",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "name",
                    models.CharField(
                        max_length=255,
                    ),
                ),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ActionRecord",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("comment", models.CharField(max_length=255, null=True, blank=True)),
                ("rating", models.IntegerField(null=True, blank=True)),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("action", models.ForeignKey(to="moviesapp.Action", on_delete=models.CASCADE)),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="List",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("title", models.CharField(max_length=255)),
                ("key_name", models.CharField(max_length=255)),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "title",
                    models.CharField(
                        max_length=255,
                    ),
                ),
                ("title_ru", models.CharField(max_length=255)),
                ("overview", models.TextField(null=True, blank=True)),
                ("plot", models.TextField(null=True, blank=True)),
                ("director", models.CharField(max_length=255, null=True, blank=True)),
                ("writer", models.CharField(max_length=255, null=True, blank=True)),
                ("genre", models.CharField(max_length=255, null=True, blank=True)),
                ("actors", models.CharField(max_length=255, null=True, blank=True)),
                ("imdb_id", models.CharField(unique=True, max_length=15, verbose_name="IMDB id")),
                ("tmdb_id", models.IntegerField(unique=True, verbose_name="TMDB id")),
                ("imdb_rating", models.DecimalField(null=True, max_digits=2, decimal_places=1)),
                (
                    "poster",
                    models.CharField(
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "release_date",
                    models.DateField(
                        null=True,
                    ),
                ),
                ("runtime", models.TimeField(null=True, blank=True)),
                ("homepage", models.URLField(null=True, verbose_name="\xd1\x81\xd0\xb0\xd0\xb9\xd1\x82", blank=True)),
                ("trailers", annoying.fields.JSONField(null=True, blank=True)),
            ],
            options={
                "ordering": ["pk"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Record",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("rating", models.IntegerField(default=0)),
                (
                    "comment",
                    models.CharField(
                        default="",
                        max_length=255,
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                ("list", models.ForeignKey(to="moviesapp.List", on_delete=models.CASCADE)),
                ("movie", models.ForeignKey(related_name="records", to="moviesapp.Movie", on_delete=models.CASCADE)),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="actionrecord",
            name="list",
            field=models.ForeignKey(blank=True, to="moviesapp.List", null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="actionrecord",
            name="movie",
            field=models.ForeignKey(to="moviesapp.Movie", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="actionrecord",
            name="user",
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
