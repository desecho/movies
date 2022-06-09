Documentation
==============

Npm module dependencies
------------------------
* ``tether``, ``jquery`` and ``popper.js`` are ``bootstrap`` dependencies
* ``node-sass`` is  a dependency of ``sass-loader``
* ``less`` is a dependency of ``less-loader`` which is a dependency of ``font-awesome-webpack``

Avatars
------------

Priority:

- Vk
- Fb
- Gravatar

Cron jobs
------------

Cron jobs are run with GitHub Actions. Time zone is UTC.

- ``Remove unused movies`` runs at 07:00 UTC (03:00 EDT) on the first day of the month
- ``Update movie data`` runs at 04:00 UTC (00:00 EDT) on the first day of the month
- ``DB backup`` runs at 9:00 UTC (05:00 EDT) daily
- ``Update IMDb ratings`` runs at 06:00 UTC (02:00 EDT) weekly on Mondays
