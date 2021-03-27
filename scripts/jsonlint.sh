#!/bin/bash

set -eu

jsonFiles=$(find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/*" -not -path "./venv/*" -not -path "./.tox/*")

if [ $1 == "lint" ]; then
    for file in $jsonFiles; do
        yarn run jsonlint $file -q
    done
fi
