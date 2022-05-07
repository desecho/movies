#!/bin/bash

set -eou pipefail

NOW="$(date +"%d-%m-%Y")"
ARCHIVE="${PROJECT}-${NOW}.sql.gz"
s3cmd put "${ARCHIVE}" "s3://${BUCKET}/${PROJECT}/" --acl-private --no-mime-magic --guess-mime-type
