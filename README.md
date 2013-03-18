#Movies

The web-application to create movie lists ("watched" and "to watch"), to share these lists along with ratings and comments. The interface is in Russian.

##Required packages

* [Python 2](http://www.python.org)
* [Django 1.5](http://djangoproject.com)
* [django-annoying](https://github.com/skorokithakis/django-annoying)
* [pytmdb3](https://github.com/wagnerrp/pytmdb3)

##Used Javascript libraries
* [jQuery v1.9.1](http://jquery.com/)
* [JQuery Raty v2.5.2](http://wbotelhos.com/raty/)
* [jQuery plugin: Validation v1.11.0](http://bassistance.de/jquery-plugins/jquery-plugin-validation/)
* [jGrowl 1.2.11]( https://github.com/stanlemon/jGrowl)

##Installation instructions

* Change the following variables in settings.py. You'll need an API key. You can obtain it here - http://api.themoviedb.org. Make sure that the user running the server has access to write to /cache/tmdb3.cache. You can generate SECRET_KEY using [Django Secret Key Generator](http://www.miniwebtool.com/django-secret-key-generator/)
    * DATABASES
    * SECRET_KEY
    * TMDB_KEY
    * BASE_PATH
    * DJANGO_PATH

* Run
```
python manage.py syncdb
python manage.py collectstatic
```

* Import db.sql to your database