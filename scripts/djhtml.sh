#!/bin/bash

set -eou pipefail

action="$1"

htmlFiles=$(find src/templates -name '*.html')

if [ "$action" == "lint" ]; then
    for file in $htmlFiles; do
        echo "Linting $file"
        djhtml -c -t 2 "$file"
    done
fi

if [ "$action" == "format" ]; then
    for file in $htmlFiles; do
        djhtml -i -t 2 "$file"
    done
fi
