#Movies

The web-application to create movie lists ("watched" and "to watch"), to share these lists along with ratings and comments. The interface is in Russian.

##Required packages

* [Python v2.6.5+](http://www.python.org)
* [Django v1.5](http://djangoproject.com)
* [pytmdb3 v0.6.16+](https://github.com/wagnerrp/pytmdb3)
* [vkontakte](https://bitbucket.org/kmike/vkontakte/src)
* [django-annoying v0.7.7+](https://github.com/skorokithakis/django-annoying)
* [django-vkontakte-iframe](https://bitbucket.org/kmike/django-vkontakte-iframe/)
* [django-simple-menu](https://github.com/fatbox/django-simple-menu)
* [django-bootstrap-pagination](https://github.com/jmcclell/django-bootstrap-pagination)
* [django-admin-tools](https://bitbucket.org/izi/django-admin-tools)

##Required API Keys
* [TMDb](http://www.themoviedb.org/)

##Used APIs
* [OMDb](http://www.omdbapi.com/)
* [2torrents.org](http://2torrents.org)

##Used Javascript libraries
* [jQuery v1.9.1](http://jquery.com/)
* [JQuery Raty v2.5.2](http://wbotelhos.com/raty/)
* [jQuery plugin: Validation v1.11.0](http://bassistance.de/jquery-plugins/jquery-plugin-validation/)
* [jGrowl v1.2.11](https://github.com/stanlemon/jGrowl)
* [Spin.js v1.2.8](http://fgnass.github.com/spin.js/)
* [jQuery Plugin for Spin.js](https://gist.github.com/its-florida/1290439/)
* [Bootstrap v2.3.1](http://twitter.github.com/bootstrap/)

##Used Graphics Packages
* [Font Awesome v3.0.2](http://fortawesome.github.com/Font-Awesome/)

##Installation instructions

* Change the following variables in settings.py:
    * DATABASES
    * TMDB_KEY
    * VK_APP_ID
    * VK_APP_SECRET

Make sure that the user running the server has write access to /cache/tmdb3.cache.

* Insert your analytics code to /static/js/analytics.js if you'd like
* Run
```
python manage.py syncdb
python manage.py collectstatic
python manage.py loaddata vk-geo
```

* Import db.sql to your database.
* Use the following command to recompile coffeescript.
```
coffee -bo js/ -cw src/
```

* Delete the /static/src folder in production