#!/bin/bash

set -eou pipefail

jsonFiles=$(find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/${APP}/static/*" -not -path "./venv/*" -not -path "./.tox/*" -not -path "./.mypy_cache/*" -not -path "./.vscode/*")

if [ "$1" == "lint" ]; then
    for file in $jsonFiles; do
        yarn run jsonlint "$file" -q
    done
fi

if [ "$1" == "format" ]; then
    for file in $jsonFiles; do
        yarn run jsonlint "$file" -i
        # shellcheck disable=SC1003
        sed -i -e '$a\' "$file"
    done
fi
