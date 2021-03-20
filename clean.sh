#!/bin/bash

# Remove imports before running the rest of formatters
autoflake --remove-all-unused-imports --in-place -r src
isort -rc src
csscomb src/moviesapp/styles/*
./cleanjs.sh
