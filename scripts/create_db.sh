#!/bin/bash

set -eou pipefail

mysql -u "$DB_USER" -p "$DB_PASSWORD" -h "$DB_HOST" -e"CREATE DATABASE $PROJECT CHARACTER SET utf8 COLLATE utf8_general_ci;"
