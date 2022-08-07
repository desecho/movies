#!/bin/bash

set -eou pipefail

cd "$(dirname "$0")"

FILENAME="$(./get_db_archive_name.sh)"
s3cmd get "s3://$BUCKET/$PROJECT/$FILENAME" /tmp
gunzip -c "/tmp/$FILENAME" | mysql -u "$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" -D "$PROJECT"
