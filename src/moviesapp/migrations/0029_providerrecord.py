# Generated by Django 4.0.5 on 2022-06-05 21:36

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('moviesapp', '0028_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provider_records', to='moviesapp.movie')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moviesapp.provider')),
            ],
        ),
    ]
