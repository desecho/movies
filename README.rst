Movies
==============

|Deployment Status| |Requirements Status| |Codecov|

The web application on Django_ 4, Vue.js_ 2, Bootstrap_ 4. Create movie lists "Watched" and "To Watch", rate movies, and add comments.

You can also add additional information such as if you watched the movie in the original version, in theatre, an extended version, in 4K, etc.

You can also see where you can stream movies.

| It is also available as a `VK app`_. Not working temporarily.
| Share your lists with VK and Facebook friends, get recommendations from friends. Not working temporarily.
| The website is live here - https://movies.samarchyan.me.
| The interface is available in English and Russian.
| See more documentation_.

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
| Open http://localhost:8000/rosetta to access rosetta.

Run in Docker:

1. Run ``make docker-build``
2. Edit file ``docker_secrets.env``
3. Run ``make docker-run``

Debugging the VK App:

1. Register account on https://ngrok.io
2. Run ``make ngrok``
3. Set ``IS_VK_DEV`` to ``True``
4. Set ``HOST_MOVIES_TEST`` to ngrok host
5. Set iframe address to ``https://[ngrok_host]/complete/vk-app/`` in the app settings

Production
----------------------------
To use production commands:

1. Edit ``db_env_prod.sh``
2. Activate the kubectl context

CI/CD
----------------------------
`GitHub Actions`_  are used for CI/CD.

Tests are automatically run on pull requests and in master or dev branches.

Deployment is automatically done in master branch.

The following GitHub Actions are used:

* `Cancel Workflow Action`_
* Checkout_
* `Setup Python`_
* `Setup Node.js environment`_
* Codecov_
* `Docker Login`_
* `Build and push Docker images`_
* `GitHub Action for DigitalOcean - doctl`_
* `Kubectl tool installer`_
* `DigitalOcean Spaces Upload Action`_
* Cache_
* `Docker Setup Buildx`_
* `Set Timezone`_

Used APIs
--------------
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

.. _GitHub Actions: https://github.com/features/actions

.. _Cancel Workflow Action: https://github.com/marketplace/actions/cancel-workflow-action
.. _Checkout: https://github.com/marketplace/actions/checkout
.. _Setup Python: https://github.com/marketplace/actions/setup-python
.. _Setup Node.js environment: https://github.com/marketplace/actions/setup-node-js-environment
.. _Codecov: https://github.com/marketplace/actions/codecov
.. _Docker Login: https://github.com/marketplace/actions/docker-login
.. _Build and push Docker images: https://github.com/marketplace/actions/build-and-push-docker-images
.. _GitHub Action for DigitalOcean - doctl: https://github.com/marketplace/actions/github-action-for-digitalocean-doctl
.. _Kubectl tool installer: https://github.com/marketplace/actions/kubectl-tool-installer
.. _DigitalOcean Spaces Upload Action: https://github.com/marketplace/actions/digitalocean-spaces-upload-action
.. _Cache: https://github.com/marketplace/actions/cache
.. _Docker Setup Buildx: https://github.com/marketplace/actions/docker-setup-buildx
.. _Set Timezone: https://github.com/marketplace/actions/set-timezone

.. _VK app: http://vk.com/app3504693_2912142

.. _IMDb logo: https://commons.wikimedia.org/wiki/File:IMDB_Logo_2016.svg
.. _Down arrow icon: https://www.iconfinder.com/icons/211614/arrow_b_down_icon
.. _TMDB Logos: https://www.themoviedb.org/about/logos-attribution
