Movies
==============

|Build Status| |Requirements Status| |Codecov|

The web application on Python/Django, jQuery, AngularJS, Bootstrap. Create movie lists ("watched" and "to watch"), rate movies and add comments.

| It is also available as a `VK app <http://vk.com/app3504693_2912142>`_.
| Share your lists with VK and Facebook friends, get recommendations from friends.
| The website is live here - https://movies.desecho.org.
| The interface is available in English and Russian.

Used APIs
--------------
* TMDb_
* OMDb_

APIs require keys.

Installation instructions
----------------------------

1. Use ansible-playbook-server_ to deploy.
2. Do git clone.

Development
--------------

| Use ``clean.sh`` to automatically prettify your code.
| Use ``tox`` for testing and linting.


.. |Requirements Status| image:: https://requires.io/github/desecho/movies/requirements.svg?branch=master
   :target: https://requires.io/github/desecho/movies/requirements/?branch=master

.. |Codecov| image:: https://codecov.io/gh/desecho/movies/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/desecho/movies

.. |Build Status| image:: https://travis-ci.org/desecho/movies.svg?branch=master
   :target: https://travis-ci.org/desecho/movies

.. _TMDb: https://www.djangoproject.com
.. _OMDb: http://www.omdbapi.com/
.. _ansible-playbook-server: https://github.com/desecho/ansible-playbook-server
