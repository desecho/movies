.DEFAULT_GOAL := help

SHELL := /bin/bash
SOURCE_VENV_CMD := source venv/bin/activate
#------------------------------------
# Help
#------------------------------------
TARGET_MAX_CHAR_NUM := 20

# COLORS
RED     := \033[0;31m
GREEN   := \033[0;32m
YELLOW  := \033[0;33m
BLUE    := \033[0;34m
MAGENTA := \033[0;35m
CYAN    := \033[0;36m
WHITE   := \033[0;37m
RESET   := \033[0;10m

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
	${SOURCE_VENV_CMD} && \
		pip install -r requirements-dev.txt

.PHONY: yarn-install-locked
## Run yarn install using lockfile
yarn-install-locked:
	yarn install --frozen-lockfile

.PHONY: create-db
## Create db
create-db:
	mysql -uroot -ppassword -h127.0.0.1 -e"CREATE DATABASE movies CHARACTER SET utf8 COLLATE utf8_general_ci;"

.PHONY: load-initial-fixtures
## Load initial fixtures
load-initial-fixtures:
	$(MAKE) loaddata lists
	$(MAKE) loaddata actions

.PHONY: bootstrap
## Bootstrap project
bootstrap: install-deps yarn-install-locked create-venv create-db migrate load-initial-fixtures
#------------------------------------


#------------------------------------
# Linters
#------------------------------------
.PHONY: pydiatra
## Run pydiatra
pydiatra:
	${SOURCE_VENV_CMD} && \
	scripts/pydiatra.sh

.PHONY: jsonlint
## Run jsonlint
jsonlint:
	scripts/jsonlint.sh
#------------------------------------

#------------------------------------
# Development
#------------------------------------
.PHONY: yarn-install-fresh
## Run yarn install (fresh)
yarn-install-fresh:
	rm yarn.lock
	yarn install

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
	${SOURCE_VENV_CMD} && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort -rc src && \
	yarn run csscomb src/moviesapp/styles/* && \
	yarn run eslint ./*.js src/moviesapp/js/* --fix
#------------------------------------


#------------------------------------
# Django management commands
#------------------------------------

MANAGE_CMD := src/manage.py

.PHONY: makemessages
## Run makemessages
makemessages:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} makemessages -d djangojs --ignore=moviesapp/static/* --ignore=node_modules/* --ignore=venv/* --ignore=.tox/*

.PHONY: runserver
## Run server for development
runserver:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} runserver 0.0.0.0:8000

.PHONY: migrate
## Run data migration
migrate:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} migrate

ifeq (loaddata,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  LOADDATA_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(LOADDATA_ARGS):;@:)
endif

.PHONY: loaddata
## Load fixtures
loaddata:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} loaddata ${LOADDATA_ARGS}

.PHONY: collectstatic
## Collect static files
collectstatic:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} collectstatic

.PHONY: createsuperuser
## Create super user
createsuperuser:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} createsuperuser
#------------------------------------
