export
.DEFAULT_GOAL := help

PROJECT := movies
APP := moviesapp

SHELL := /bin/bash
SOURCE_CMDS := source venv/bin/activate && source env.sh

#------------------------------------
# Help
#------------------------------------
TARGET_MAX_CHAR_NUM := 25

# COLORS
GREEN   := \033[0;32m
YELLOW  := \033[0;33m
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
	sudo apt install python3.10 python3.10-venv python3.10-dev -y
	# Install MySQL dependencies
	sudo apt install libmysqlclient-dev -y
	# Install dependency for makemessages
	sudo apt install gettext -y

.PHONY: create-venv
## Create virtual environment and install requirements
create-venv:
	python3.10 -m venv venv
	${SOURCE_CMDS} && \
		pip install -r requirements-dev.txt

.PHONY: yarn-install-locked
## Run yarn install using lockfile
yarn-install-locked:
	yarn install --frozen-lockfile

.PHONY: create-db
## Create db
create-db:
	source env.sh && \
	scripts/create_db.sh

.PHONY: load-initial-fixtures
## Load initial fixtures
load-initial-fixtures:
	$(MAKE) loaddata lists
	$(MAKE) loaddata actions

.PHONY: bootstrap
## Bootstrap project
bootstrap: install-deps yarn-install-locked create-venv create-env-files create-db migrate load-initial-fixtures yarn-build

.PHONY: create-env-files
## Create env files
create-env-files:
	cp -n env_template.sh env.sh
	cp -n db_env_prod_template.sh db_env_prod.sh
#------------------------------------


#------------------------------------
# Scripts
#------------------------------------

.PHONY: pydiatra-script
pydiatra-script:
	scripts/pydiatra.sh

.PHONY: jsonlint-script
jsonlint-script:
	scripts/jsonlint.sh lint

.PHONY: shellcheck-script
shellcheck-script:
	scripts/shellcheck.sh

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
	tox -e py-pydiatra

.PHONY: jsonlint
## Run jsonlint
jsonlint:
	tox -e py-jsonlint

.PHONY: pylint
## Run pylint
pylint:
	tox -e py-pylint

.PHONY: flake8
## Run flake8
flake8:
	tox -e py-flake8

.PHONY: isort
## Run isort
isort:
	tox -e py-isort

.PHONY: bandit
## Run bandit
bandit:
	tox -e py-bandit

.PHONY: rstlint
## Run rstlint
rstlint:
	tox -e py-rstlint

.PHONY: pydocstyle
## Run pydocstyle
pydocstyle:
	tox -e py-pydocstyle

.PHONY: safety
## Run safety
safety:
	tox -e py-safety

.PHONY: pytest
## Run pytest
pytest:
	tox -e py-pytest

.PHONY: eslint
## Run eslint
eslint:
	tox -e py-eslint

.PHONY: csscomb-linter
## Run csscomb-linter
csscomb-linter:
	tox -e py-csscomb-linter

.PHONY: black
## Run black linter
black:
	tox -e py-black

.PHONY: shfmt
## Run shfmt linter
shfmt:
	tox -e py-shfmt

.PHONY: shellcheck
## Run shellcheck linter
shellcheck:
	tox -e py-shellcheck

#------------------------------------

#------------------------------------
# Development
#------------------------------------
.PHONY: update-venv
## Update packages in venv and tox with current requirements | Development
update-venv:
	${SOURCE_CMDS} && \
	pip install -r requirements-dev.txt && \
	deactivate && \
	source .tox/py/bin/activate && \
	pip install -r requirements-dev.txt

.PHONY: yarn-install-refresh
## Run yarn install (refresh)
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

.PHONY: format
## Format code except for json files
format:
	${SOURCE_CMDS} && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort src && \
	black .
	yarn run csscomb src/${APP}/styles/*
	yarn run eslint ./*.js src/${APP}/js/* --fix
	shfmt -l -w .

.PHONY: format-json
## Format json files
format-json:
	scripts/jsonlint.sh format

.PHONY: format-all
## Format code
format-all: format format-json

.PHONY: ngrok
## Run ngrok
ngrok:
	ngrok http 8000

.PHONY: drop-db
## Drop db
drop-db:
	source env.sh && \
	scripts/drop_db.sh

.PHONY: load-db
## Load db from yesterday's backup
load-db: drop-db create-db
	source env.sh && \
	./scripts/load_db.sh
#------------------------------------


#------------------------------------
# Django management commands
#------------------------------------

MANAGE_CMD := src/manage.py

.PHONY: makemessages
## Run makemessages | Django
makemessages:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} makemessages -a --ignore=venv --ignore=.tox --ignore=static && \
	${MANAGE_CMD} makemessages -a -d djangojs --ignore=src/${APP}/static --ignore=node_modules --ignore=venv --ignore=.tox --ignore=static

.PHONY: runserver
## Run server for development
runserver:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} runserver 0.0.0.0:8000

.PHONY: run
## Run server for development
run: runserver

.PHONY: migrate
## Run data migration
migrate:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} migrate

ifeq (loaddata,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  LOADDATA_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(LOADDATA_ARGS):;@:)
endif

.PHONY: loaddata
## Load fixtures. Usage: [fixture]
loaddata:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} loaddata ${LOADDATA_ARGS}

.PHONY: collectstatic
## Collect static files
collectstatic:
	${SOURCE_CMDS} && \
	export IS_DEV= && \
	${MANAGE_CMD} collectstatic --no-input

.PHONY: createsuperuser
## Create super user
createsuperuser:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} createsuperuser

.PHONY: makemigrations
## Run makemigrations command
makemigrations:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} makemigrations ${APP}

ifeq (manage,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(MANAGE_ARGS):;@:)
endif

.PHONY: manage
## Run management command. Usage: [command]
manage:
	${SOURCE_CMDS} && \
	${MANAGE_CMD} ${MANAGE_ARGS}
#------------------------------------


#------------------------------------
# Docker commands
#------------------------------------
DOCKER_ENV_FILE := env_docker

.PHONY: docker-build
## Build image | Docker
docker-build:
	docker build -t ${PROJECT} .

.PHONY: docker-run
## Run server in docker
docker-run:
	docker-compose up

.PHONY: docker-sh
## Run docker shell
docker-sh:
	docker run -ti --env-file ${DOCKER_ENV_FILE} ${PROJECT} sh

#------------------------------------


#------------------------------------
# Production commands
#------------------------------------
.PHONY: prod-create-db
## Create prod db | Production
prod-create-db:
	source db_env_prod.sh && \
	scripts/create_db.sh

.PHONY: prod-drop-db
## Drop prod db
prod-drop-db:
	source db_env_prod.sh && \
	scripts/drop_db.sh

.PHONY: prod-load-db
## Load db to prod from yesterday's backup
prod-load-db: prod-drop-db prod-create-db
	source db_env_prod.sh && \
	./scripts/load_db.sh

ifeq (prod-manage,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  PROD_MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(PROD_MANAGE_ARGS):;@:)
endif

.PHONY: prod-manage
## Run management command in prod. Usage: [command]
prod-manage:
	scripts/run_management_command.sh ${PROD_MANAGE_ARGS}

.PHONY: prod-enable-debug
## Enable debug in prod. It will be reset with the next deployment
prod-enable-debug:
	yq eval '.data.DEBUG="True"' deployment/configmap.yaml | kubectl apply -f -
	kubectl rollout restart "deployment/${PROJECT}"
#------------------------------------
