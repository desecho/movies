.DEFAULT_GOAL := help

SHELL := /bin/bash
SOURCE_VENV_CMD := source venv/bin/activate
#------------------------------------
# Help
#------------------------------------
TARGET_MAX_CHAR_NUM := 25

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
## Show help | Help
help:
	@echo ''
	@echo 'Usage:'
	@printf "  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}"
	@echo ''
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
		    if (index(lastLine, "|") != 0) { \
				stage = substr(lastLine, index(lastLine, "|") + 1); \
				printf "\n ${GRAY}%s: \n", stage;  \
			} \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			if (index(lastLine, "|") != 0) { \
				helpMessage = substr(helpMessage, 0, index(helpMessage, "|")-1); \
			} \
			printf "    ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
#------------------------------------

#------------------------------------
# Installation
#------------------------------------

.PHONY: install-deps
## Install dependencies | Installation
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
bootstrap: install-deps yarn-install-locked create-venv create-db migrate load-initial-fixtures yarn-build collectstatic create-local-settings

.PHONY: create-local-settings
## Create local_settings
create-local-settings:
	cp -n src/movies/local_settings_template.py src/movies/local_settings.py
#------------------------------------


#------------------------------------
# Tox
#------------------------------------
.PHONY: test
## Run tests | Tests
test:
	tox

.PHONY: pydiatra
## Run pydiatra
pydiatra:
	${SOURCE_VENV_CMD} && \
	scripts/pydiatra.sh

.PHONY: jsonlint
## Run jsonlint
jsonlint:
	scripts/jsonlint.sh lint

.PHONY: pylint
## Run pylint
pylint:
	tox -e py37-pylint

.PHONY: flake8
## Run flake8
flake8:
	tox -e py37-flake8

.PHONY: isort
## Run isort
isort:
	tox -e py37-isort

.PHONY: bandir
## Run bandir
bandir:
	tox -e py37-bandir

.PHONY: rstlint
## Run rstlint
rstlint:
	tox -e py37-rstlint

.PHONY: pydocstyle
## Run pydocstyle
pydocstyle:
	tox -e py37-pydocstyle

.PHONY: safety
## Run safety
safety:
	tox -e py37-safety

.PHONY: pytest
## Run pytest
pytest:
	tox -e py37-pytest

.PHONY: eslint
## Run eslint
eslint:
	tox -e py37-eslint

.PHONY: csscomb-linter
## Run csscomb-linter
csscomb-linter:
	tox -e py37-csscomb-linter

.PHONY: black
## Run black linter
black:
	tox -e py37-black
#------------------------------------

#------------------------------------
# Development
#------------------------------------
.PHONY: yarn-install-refresh
## Run yarn install (refresh) | Development
yarn-install-refresh:
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

.PHONY: format-fast
## Fast format code
format-fast:
	${SOURCE_VENV_CMD} && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort -rc src && \
	black .
	yarn run csscomb src/moviesapp/styles/*
	yarn run eslint ./*.js src/moviesapp/js/* --fix

.PHONY: format
## Format code
format: format-fast
	scripts/jsonlint.sh format
#------------------------------------


#------------------------------------
# Django management commands
#------------------------------------

MANAGE_CMD := src/manage.py

.PHONY: makemessages
## Run makemessages | Django
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

.PHONY: makemigrations
## Run makemigrations command
makemigrations:
	${SOURCE_VENV_CMD} && \
	${MANAGE_CMD} makemigrations
#------------------------------------
