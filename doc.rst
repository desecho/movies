Documentation
==============

Npm module dependencies
------------------------
* ``tether``, ``jquery`` and ``popper.js`` are ``bootstrap`` dependencies
* ``node-sass`` is  a dependency of ``sass-loader``
* ``less`` is a dependency of ``less-loader`` which is a dependency of ``font-awesome-webpack``

Avatars
-----------
Priority:

- Vk
- Fb
- Gravatar

Cron jobs
------------

Cron jobs are run with `GitHub Actions`_. Time zone is UTC.

- ``Remove unused movies`` runs at 07:00 UTC (03:00 EDT) on the first day of the month
- ``Update movie data`` runs at 04:00 UTC (00:00 EDT) on the first day of the month
- ``DB backup`` runs at 09:00 UTC (05:00 EDT) daily
- ``Update IMDb ratings`` runs at 06:00 UTC (02:00 EDT) on Mondays
- ``Update watch data`` runs at 07:00 UTC (03:00 EDT) on Mondays
- ``Update watch data minimal`` runs at 00:00 UTC (20:00 EDT) daily

CI/CD
----------
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
