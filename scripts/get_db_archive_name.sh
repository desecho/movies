#!/bin/bash

set -eou pipefail

TODAY="$(date +"%d-%m-%Y")"
echo "${PROJECT}-${TODAY}.sql.gz"
