#!/bin/bash

set -eou pipefail

cd "$(dirname "$0")"

FILENAME="$(./get_db_archive_name.sh)"
mkdir ../upload
mysqldump -u "${PROJECT}" -h "${DB_HOST}" "${PROJECT}" -p"${DB_PASSWORD}" --no-tablespaces | gzip -9 > "../upload/${FILENAME}"
