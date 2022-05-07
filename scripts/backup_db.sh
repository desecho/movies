#!/bin/bash

set -eou pipefail

NOW="$(date +"%d-%m-%Y")"
ARCHIVE="${PROJECT}-${NOW}.sql.gz"
mysqldump -u root -h "${DB_HOST}" "${PROJECT}" -p"${DB_PASSWORD}" | gzip -9 > "${ARCHIVE}"
