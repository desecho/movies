.DEFAULT_GOAL := help

include help.mk

export PROJECT := movies
export APP := moviesapp

SHELL := /bin/bash
SOURCE_CMDS := source venv/bin/activate && source env.sh
PYTHON := python3.10

#------------------------------------
# Installation
#------------------------------------
SHFMT_VERSION := 3.4.3
SHFMT_PATH := /usr/local/bin/shfmt

.PHONY: install-shfmt
## Install shfmt | Installation
install-shfmt:
	sudo curl https://github.com/mvdan/sh/releases/download/v${SHFMT_VERSION}/shfmt_v${SHFMT_VERSION}_linux_amd64 -Lo ${SHFMT_PATH}
	sudo chmod +x ${SHFMT_PATH}

HADOLINT_VERSION := 2.10.0
HADOLINT_PATH := /usr/local/bin/hadolint

.PHONY: install-hadolint
## Install hadolint
install-hadolint:
	sudo curl https://github.com/hadolint/hadolint/releases/download/v${HADOLINT_VERSION}/hadolint-Linux-x86_64 -Lo ${HADOLINT_PATH}
	sudo chmod +x ${HADOLINT_PATH}

.PHONY: install-deps
## Install dependencies
install-deps: install-shfmt install-hadolint
	# Install Python
	sudo apt install ${PYTHON} ${PYTHON}-venv ${PYTHON}-dev -y
	# Install MySQL dependencies
	sudo apt install libmysqlclient-dev -y
	# Install dependency for makemessages
	sudo apt install gettext -y

.PHONY: create-venv
## Create virtual environment and install requirements
create-venv:
	${PYTHON} -m venv venv
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
bootstrap: install-deps yarn-install-locked create-env-files create-venv create-db migrate load-initial-fixtures yarn-build

.PHONY: create-env-files
## Create env files
create-env-files: env.sh db_env_prod.sh

env.sh:
	cp env_template.sh env.sh

db_env_prod.sh:
	cp db_env_prod_template.sh db_env_prod.sh
#------------------------------------

#------------------------------------
# Scripts
#------------------------------------
.PHONY: pydiatra-script
pydiatra-script:
	scripts/pydiatra.sh
#------------------------------------

#------------------------------------
# Tests
#------------------------------------
.PHONY: test
## Run tests | Tests
test: shellcheck hadolint shfmt csscomb-linter eslint jsonlint tox

.PHONY: tox
## Run tox
tox:
	tox

.PHONY: pydiatra
## Run pydiatra linter
pydiatra:
	tox -e py-pydiatra

.PHONY: pylint
## Run pylint linter
pylint:
	tox -e py-pylint

.PHONY: flake8
## Run flake8 linter
flake8:
	tox -e py-flake8

.PHONY: isort
## Run isort linter
isort:
	tox -e py-isort

.PHONY: bandit
## Run bandit linter
bandit:
	tox -e py-bandit

.PHONY: rstlint
## Run rstlint linter
rstlint:
	tox -e py-rstlint

.PHONY: pydocstyle
## Run pydocstyle linter
pydocstyle:
	tox -e py-pydocstyle

.PHONY: safety
## Run safety linter
safety:
	tox -e py-safety

.PHONY: pytest
## Run pytest
pytest:
	tox -e py-pytest

.PHONY: black
## Run black linter
black:
	tox -e py-black

.PHONY: yamllint
## Run yamllint linter
yamllint:
	tox -e py-yamllint

.PHONY: eslint
## Run eslint linter
eslint:
	yarn run eslint "./*.js" "src/${APP}/js/*"

.PHONY: csscomb-linter
## Run csscomb-linter linter
csscomb-linter:
	yarn run csscomb-linter "src/${APP}/styles/*"

.PHONY: shfmt
## Run shfmt linter
shfmt:
	shfmt -l -d .

.PHONY: shellcheck
## Run shellcheck linter
shellcheck:
	shellcheck scripts/*.sh ./*.sh

.PHONY: hadolint
## Run hadolint linter
hadolint:
	hadolint Dockerfile

.PHONY: jsonlint
## Run jsonlint linter
jsonlint:
	scripts/jsonlint.sh lint
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
## Format python code
format:
	${SOURCE_CMDS} && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort src && \
	black .

.PHONY: format-json
## Format json files
format-json:
	scripts/jsonlint.sh format

.PHONY: format-css
## Format css files
format-css:
	yarn run csscomb src/${APP}/styles/*

.PHONY: format-js
## Format js files
format-js:
	yarn run eslint ./*.js src/${APP}/js/* --fix

.PHONY: format-sh
## Format sh files
format-sh:
	shfmt -l -w .

.PHONY: format-all
## Format code
format-all: format format-json format-css format-js format-sh

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
