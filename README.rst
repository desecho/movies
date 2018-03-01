Movies
==============

|Build Status| |Requirements Status| |Codecov|

The web application on Django_ 2, Vue.js_ 2, Bootstrap_ 4. Create movie lists ("Watched" and "To watch"), rate movies and add comments.

| It is also available as a `VK app <http://vk.com/app3504693_2912142>`_.
| Share your lists with VK and Facebook friends, get recommendations from friends.
| The website is live here - https://movies.desecho.org.
| The interface is available in English and Russian.
| See more documentation_.

Used APIs
--------------
* TMDb_
* OMDb_

Installation instructions
----------------------------

1. Use ansible-playbook-server_ to deploy.
2. Do git clone.

Development
--------------

| Use ``clean.sh`` to automatically prettify your code.
| Use ``tox`` for testing and linting.


Images
-----------
* [IMDb logo](https://commons.wikimedia.org/wiki/File:IMDB_Logo_2016.svg)
* [Down arrow icon](https://www.iconfinder.com/icons/211614/arrow_b_down_icon)
* [TMDb Logos](https://www.themoviedb.org/about/logos-attribution)

.. |Requirements Status| image:: https://requires.io/github/desecho/movies/requirements.svg?branch=master
   :target: https://requires.io/github/desecho/movies/requirements/?branch=master

.. |Codecov| image:: https://codecov.io/gh/desecho/movies/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/desecho/movies

.. |Build Status| image:: https://travis-ci.org/desecho/movies.svg?branch=master
   :target: https://travis-ci.org/desecho/movies

.. _TMDb: https://www.themoviedb.org/
.. _OMDb: http://www.omdbapi.com/
.. _ansible-playbook-server: https://github.com/desecho/ansible-playbook-server
.. _documentation: https://github.com/desecho/movies/blob/master/doc.rst
.. _Vue.js: https://vuejs.org/
.. _Bootstrap: https://getbootstrap.com/
.. _Django: https://www.djangoproject.com/
