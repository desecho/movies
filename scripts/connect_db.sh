#!/bin/bash

set -eou pipefail

mysql -u "$DB_USER" -p"$DB_PASSWORD" -h "$DB_HOST"
