Documentation
==============

Npm module dependencies
------------------------
* ``tether``, ``jquery`` and ``popper.js`` are ``bootstrap`` dependencies.
* ``node-sass`` is  a dependency of ``sass-loader``.
* ``less`` is a dependency of ``less-loader`` which is a dependency of ``font-awesome-webpack``.

Avatars
------------

Priority:

- Vk
- Fb
- Gravatar

Cron jobs
------------

Cronjobs are run with GitHub Actions.

- `Remove unused movies` command runs every month
- `Update movie data` command runs every month
- `Update IMDb ratings` command runs every month
- Backup runs daily
