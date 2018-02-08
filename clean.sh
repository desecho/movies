#!/bin/bash

# We want to remove imports before running isort.
autoflake --remove-all-unused-imports --in-place -r src
yapf -ri src
# We want to run isort after yapf to make sure isort lint pass.
isort -rc src
csscomb src/moviesapp/static/css/style.css
eslint src/moviesapp/static/js/*  --fix
find src/moviesapp/static/js -type f -name "*.js" -exec js-beautify -r {} \;
find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/vendor/*" -exec js-beautify -r {} \;
