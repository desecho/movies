#!/bin/bash

set -eu

jsonFiles=$(find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/${APP}/static/*" -not -path "./venv/*" -not -path "./.tox/*")

if [ $1 == "lint" ]; then
    for file in $jsonFiles; do
        yarn run jsonlint $file -q
    done
fi

if [ $1 == "format" ]; then
    for file in $jsonFiles; do
        yarn run jsonlint $file -i
        sed -i -e '$a\' $file
    done
fi
