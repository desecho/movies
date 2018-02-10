#!/bin/bash

eslint src/moviesapp/static/js/*  --fix
find src/moviesapp/static/js -type f -name "*.js" -exec js-beautify -r {} \;
find . -type f -name "*.json" -not -path "./node_modules/*" -not -path "./src/moviesapp/static/vendor/*" -exec js-beautify -r {} \;
