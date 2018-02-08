#!/bin/bash

# We want to remove imports before running isort.
autoflake --remove-all-unused-imports --in-place -r src
yapf -ri src
# We want to run isort after yapf to make sure isort lint pass.
isort -rc src
csscomb src/moviesapp/static/css/style.css
eslint src/moviesapp/static/js/*  --fix
