.DEFAULT_GOAL := help

SHELL := /bin/bash

#------------------------------------
# Help
#------------------------------------
TARGET_MAX_CHAR_NUM := 20

# COLORS
RED     :=\033[0;31m
GREEN   :=\033[0;32m
YELLOW  :=\033[0;33m
BLUE    :=\033[0;34m
MAGENTA :=\033[0;35m
CYAN    :=\033[0;36m
WHITE   :=\033[0;37m
RESET   :=\033[0;10m

.PHONY: help
## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo -e '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-_0-9\\%]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{lastLine = $$0}' $(MAKEFILE_LIST)
#------------------------------------


#------------------------------------
# Installation
#------------------------------------
.PHONY: install-deps
## Install dependencies
install-deps:
	# Install Python
	sudo apt install python3.7 python3.7-venv python3.7-dev -y
	# Install MySQL dependencies
	sudo apt install libmysqlclient-dev -y

.PHONY: create-venv
## Create virtual environment and install requirements
create-venv:
	python3.7 -m venv venv
	source venv/bin/activate && \
		pip install -r requirements-dev.txt

.PHONY: yarn-install
## Run yarn install
yarn-install:
	rm yarn.lock
	yarn install

.PHONY: yarn-install-locked
## Run yarn install using lockfile
yarn-install-locked:
	yarn install --frozen-lockfile
#------------------------------------


#------------------------------------
# Linters
#------------------------------------
.PHONY: pydiatra
## Run pydiatra
pydiatra:
	source venv/bin/activate && \
	scripts/pydiatra.sh

.PHONY: jsonlint
## Run jsonlint
jsonlint:
	scripts/jsonlint.sh
#------------------------------------

#------------------------------------
# Development
#------------------------------------
.PHONY: yarn-build
## Run yarn build
yarn-build:
	yarn build

.PHONY: build
## Run yarn build for development
build:
	yarn build --watch
#------------------------------------


#------------------------------------
# Commands
#------------------------------------
.PHONY: test
## Run tests
test:
	tox

.PHONY: format
## Format code
format:
	source venv/bin/activate && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort -rc src && \
	yarn run csscomb src/moviesapp/styles/* && \
	yarn run eslint ./*.js src/moviesapp/js/* --fix
#------------------------------------


#------------------------------------
# Django management commands
#------------------------------------
.PHONY: makemessages
## Run makemessages
makemessages:
	# dev_scripts/run_server.sh
	source venv/bin/activate && \
	src/manage.py makemessages -d djangojs --ignore=moviesapp/static/* --ignore=node_modules/*

.PHONY: runserver
## Run server for development
runserver:
	source venv/bin/activate && \
	src/manage.py runserver 0.0.0.0:8000
#------------------------------------
