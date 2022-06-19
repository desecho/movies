#!/bin/bash

# bool
export DEBUG=True
# bool
export COLLECT_STATIC=True
# bool
export IS_DEV=True
# bool
export DISABLE_CSRF=
export SECRET_KEY=key
export PROJECT_DOMAIN=localhost
export INTERNAL_IP=127.0.0.1
export STATIC_URL=/static/
export SENTRY_DSN=
export GOOGLE_ANALYTICS_ID=id

export DB_USER=root
export DB_PASSWORD=password
export DB_HOST=127.0.0.1

# bool
export IS_CELERY_DEBUG=True
export DJANGO_SETTINGS_MODULE=movies.settings
export REDIS_URL=redis://localhost:6379/
