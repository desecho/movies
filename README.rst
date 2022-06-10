Movies
==============

|Deployment Status| |Requirements Status| |Codecov|

| The web application on Django_ 4, Vue.js_ 2, Bootstrap_ 4. Create movie lists "Watched" and "To Watch", rate movies, and add comments.
| You can also add additional information such as if you watched the movie in the original version, in theatre, an extended version, in 4K, etc.
| You can also see where you can stream movies.

| It is also available as a `VK app`_. Not working temporarily.
| Share your lists with VK and Facebook friends, get recommendations from friends. Not working temporarily.

| The website is live here - https://movies.samarchyan.me.
| The interface is available in English and Russian.

See more documentation_.

Development
----------------------------
1. Use ubuntu-vm_ as a development VM
2. Use mysql-docker_ to bring up MySQL in Docker
3. Run ``make bootstrap``
4. Run ``make createsuperuser`` to create a superadmin user
5. Edit files ``env_custom.sh`` and ``env_secrets.sh``

| Run ``make build`` and ``make run`` to run the server for development.
| Run ``make help`` to get a list of all available commands.

| Open http://localhost:8000/ to access the web application.
| Open http://localhost:8000/admin to access the admin section.
| Open http://localhost:8000/rosetta to access Rosetta.

Run in Docker:

1. Run ``make docker-build``
2. Edit file ``docker_secrets.env``
3. Run ``make docker-run``

Debugging the VK app:

1. Register account on https://ngrok.io
2. Run ``make ngrok``
3. Set ``IS_VK_DEV`` to ``True``
4. Set ``HOST_MOVIES_TEST`` to ngrok host
5. Set iframe address to ``https://[ngrok_host]/complete/vk-app/`` in the app settings

Production
------------
To use production commands:

1. Edit file ``db_env_prod.sh``
2. Activate the kubectl context

Used APIs
-----------
* TMDB_
* OMDb_

Used images
-----------
* `IMDb logo`_
* `Down arrow icon`_
* `TMDB Logos`_


.. |Requirements Status| image:: https://requires.io/github/desecho/movies/requirements.svg?branch=master
   :target: https://requires.io/github/desecho/movies/requirements/?branch=master

.. |Codecov| image:: https://codecov.io/gh/desecho/movies/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/desecho/movies

.. |Deployment Status| image:: https://github.com/desecho/movies/actions/workflows/deployment.yaml/badge.svg
   :target: https://github.com/desecho/movies/actions/workflows/deployment.yaml

.. _TMDB: https://www.themoviedb.org/
.. _OMDb: http://www.omdbapi.com/

.. _documentation: https://github.com/desecho/movies/blob/master/doc.rst

.. _Vue.js: https://vuejs.org/
.. _Bootstrap: https://getbootstrap.com/
.. _Django: https://www.djangoproject.com/

.. _ubuntu-vm: https://github.com/desecho/ubuntu-vm
.. _mysql-docker: https://github.com/desecho/mysql-docker

.. _VK app: http://vk.com/app3504693_2912142

.. _IMDb logo: https://commons.wikimedia.org/wiki/File:IMDB_Logo_2016.svg
.. _Down arrow icon: https://www.iconfinder.com/icons/211614/arrow_b_down_icon
.. _TMDB Logos: https://www.themoviedb.org/about/logos-attribution
