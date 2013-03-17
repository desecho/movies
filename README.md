#Movies

The web-application to create movie lists ("watched" and "to watch"), to share these lists along with ratings and comments.
It's coded in Python 2, Django 1.5. The interface is in Russian.

##Required packages:
* Django 1.5

* required packages:
    * [django-annoying](https://github.com/skorokithakis/django-annoying)
    * [pytmdb3](https://github.com/wagnerrp/pytmdb3)

##Installation

* Configure the settings.py file. You'll need an API key. You can obtain it here - http://api.themoviedb.org.

    * Change the following variables:
        * DATABASES
        * TMDB_KEY
        * BASE_PATH
        * DJANGO_PATH

* Run
```
python manage.py syncdb
python manage.py collectstatic
```

* Import db.sql to your database