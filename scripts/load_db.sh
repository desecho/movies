#!/bin/bash

set -eou pipefail

YESTERDAY=$(date -d "yesterday" '+%d-%m-%Y')
FILENAME=$PROJECT-$YESTERDAY.sql.gz
s3cmd get "s3://scrap-db-backups/$PROJECT/$FILENAME /tmp"
gunzip -c "/tmp/$FILENAME" | mysql -u "$DB_USER" -p "$DB_PASSWORD" -h "$DB_HOST" -D "$PROJECT"
