#!/bin/bash

set -eu

jsonFiles=$(find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/*" -not -path "./venv/*" -not -path "./.tox/*")

for file in $jsonFiles; do
    yarn run jsonlint $file
done
