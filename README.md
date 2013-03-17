#Movies

The web-application to create movie lists ("watched" and "to watch"), to share these lists along with ratings and comments. It's coded on Python 2, Django 1.5. The interface is in Russian.

##Required packages:
* Django 1.5

* easy_install:
    * django-annoying pytmdb3

##Installation

* Configure TMDB
    * You'll need an API key. You can obtain it here - http://api.themoviedb.org.
    * Enter tmdb settings to movies/views.py

    ```python
    TMDB_KEY = ''
    tmdb3.set_cache(filename='/path/to/cache/file/file.cache')
    ```

* Configure the settings.py file

    * Enter the db settings

    ```python
    DATABASES = {
            …
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            …
    }
    ```

    * Change the path variables

    ```python
    BASE_PATH = '/path/to/project/'
    DJANGO_PATH = '/usr/local/lib/python2.7/dist-packages/django/'
    ```

* Run
```
python manage.py syncdb
python manage.py collectstatic
```

* Load SQL data from db.sql

## Additional settings
Additional settings can be found here
```
movies/const.py
movies/models.py
movies/views.py
```
