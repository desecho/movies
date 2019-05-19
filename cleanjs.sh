#!/bin/bash

./eslint.sh
find . -type f -name "*.js" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/*" -not -path "./env/*" -exec js-beautify -r {} \;
find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/*" -not -path "./env/*" -exec js-beautify -r {} \;
