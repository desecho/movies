#Movies

The web-application to create movie lists ("watched" and "to watch"), to share these lists along with ratings and comments. The interface is in Russian.

##Required packages

* [Python v2.6.5+](http://www.python.org)
* [Django v1.5](http://djangoproject.com)
* [CoffeeScript v1.6.1](http://coffeescript.org)
* [django-annoying v0.7.7+](https://github.com/skorokithakis/django-annoying)
* [django-simple-menu](https://github.com/fatbox/django-simple-menu)
* [django-bootstrap-pagination](https://github.com/jmcclell/django-bootstrap-pagination)
* [pytmdb3 v0.6.16+](https://github.com/wagnerrp/pytmdb3)
* [vkontakte](https://bitbucket.org/kmike/vkontakte/src)
* [django-vkontakte-iframe](https://bitbucket.org/kmike/django-vkontakte-iframe/)
* [django-admin-tools](https://bitbucket.org/izi/django-admin-tools)
* [python-dateutil](http://labix.org/python-dateutil)
* [poster 0.8.1](https://pypi.python.org/pypi/poster/)

##Required API Keys
* [TMDb](http://www.themoviedb.org/)

##Used APIs
* [OMDb](http://www.omdbapi.com/)
* [2torrents.org](http://2torrents.org)

##Used Javascript libraries

* [jQuery v2.1.1](http://jquery.com/)
* [JQuery Raty v2.5.2](http://wbotelhos.com/raty/)
* [jQuery plugin: Validation v1.11.1](http://bassistance.de/jquery-plugins/jquery-plugin-validation/)
* [jGrowl v1.2.11](https://github.com/stanlemon/jGrowl)
* [Spin.js v2.0.1](http://fgnass.github.com/spin.js/)
* [Bootstrap v2.3.1](http://twitter.github.com/bootstrap/)

##Used Graphics Packages
* [Font Awesome v3.0.2](http://fortawesome.github.com/Font-Awesome/)

##Installation instructions

* Change/Add the following variables in settings.py:
    * DATABASES
    * TMDB_KEY
    * VK_APP_ID
    * VK_APP_SECRET

Make sure that the user running the server has write access to /cache/tmdb3.cache.

* Insert your analytics code to movies_project/static/js/analytics.js if you'd like
* Run
```
python manage.py syncdb
python manage.py collectstatic
python manage.py loaddata vk-geo
```

* Import db.sql to your database.

* Run the following command to compile coffeescript.
```
coffee -bo movies_project/static/js/ -cw movies_project/static/src/
```

* Delete movies_project/static/src folder before deployment.