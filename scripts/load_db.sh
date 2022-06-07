#!/bin/bash

set -eou pipefail

TODAY=$(date '+%d-%m-%Y')
FILENAME="$PROJECT-$TODAY.sql.gz"
s3cmd get "s3://$BUCKET/$PROJECT/$FILENAME" /tmp
gunzip -c "/tmp/$FILENAME" | mysql -u "$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST" -D "$PROJECT"
