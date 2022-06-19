#!/bin/bash

set -eou pipefail
CDN_ID="$(doctl compute cdn list -o json | jq --arg SPACE_NAME "$SPACE_NAME" '.[] | select(.custom_domain==$SPACE_NAME).id' -r)"
doctl compute cdn flush "$CDN_ID"
