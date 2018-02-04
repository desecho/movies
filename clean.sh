#!/bin/bash

autoflake --remove-all-unused-imports --in-place -r src
yapf -ri src
isort -rc src
