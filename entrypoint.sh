#!/bin/sh

set -eou pipefail

celery -A "$PROJECT.celery.app" worker -D
gunicorn --bind :8000 --workers 3 "$PROJECT.wsgi:application"
