#!/bin/bash

set -eu

mysql -u$DB_USER -p$DB_PASSWORD -h$DB_HOST -e"DROP DATABASE $PROJECT;"
