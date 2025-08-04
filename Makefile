.DEFAULT_GOAL := help

include makefiles/colors.mk
include makefiles/help.mk
include makefiles/macros.mk

export PROJECT := movies
export APP := moviesapp
export BUCKET := scrap-db-backups
export DOCKER_SECRETS_ENV_FILE := docker_secrets.env

ENV_FILE := env.sh
ENV_CUSTOM_FILE := env_custom.sh
ENV_SECRETS_FILE := env_secrets.sh
DB_ENV_PROD_FILE := db_env_prod.sh

SHELL := /bin/bash

VENV_DIR := .venv
SOURCE_CMDS := source $(VENV_DIR)/bin/activate && source $(ENV_FILE) && source $(ENV_CUSTOM_FILE) && source $(ENV_SECRETS_FILE)
CMD_FRONTEND := cd frontend && source $(ENV_FILE)
PYTHON_VERSION := 3.11
PYTHON := python$(PYTHON_VERSION)

#------------------------------------
# Installation
#------------------------------------
BIN_DIR := /usr/local/bin

SHFMT_VERSION := 3.4.3
SHFMT_PATH := ${BIN_DIR}/shfmt

.PHONY: install-shfmt
## Install shfmt | Installation
install-shfmt:
	sudo curl https://github.com/mvdan/sh/releases/download/v${SHFMT_VERSION}/shfmt_v${SHFMT_VERSION}_linux_amd64 -Lo ${SHFMT_PATH}
	sudo chmod +x ${SHFMT_PATH}

HADOLINT_VERSION := 2.10.0
HADOLINT_PATH := ${BIN_DIR}/hadolint

.PHONY: install-hadolint
## Install hadolint
install-hadolint:
	sudo curl https://github.com/hadolint/hadolint/releases/download/v${HADOLINT_VERSION}/hadolint-Linux-x86_64 -Lo ${HADOLINT_PATH}
	sudo chmod +x ${HADOLINT_PATH}

ACTIONLINT_VERSION := 1.6.13
ACTIONLINT_PATH := ${BIN_DIR}/actionlint
ACTIONLINT_URL := https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz
ACTIONLINT_TMP_DIR := $(shell mktemp -d)
ACTIONLINT_ARCHIVE := actionlint.tar.gz
.PHONY: install-actionlint
## Install actionlint
install-actionlint:
	cd ${ACTIONLINT_TMP_DIR} && \
	curl ${ACTIONLINT_URL} -Lo ${ACTIONLINT_ARCHIVE} && \
	tar -xvf ${ACTIONLINT_ARCHIVE} && \
	sudo mv actionlint ${ACTIONLINT_PATH}

.PHONY: install-linters-binaries
## Install linters binaries
install-linters-binaries: install-shfmt install-hadolint install-actionlint

.PHONY: install-deps
## Install dependencies
install-deps: install-linters-binaries install-python install-mysql-client

.PHONY: install-python
install-python:
	$(call print,Installing Python)
	@sudo apt install ${PYTHON} ${PYTHON}-venv ${PYTHON}-dev -y

.PHONY: install-mysql-client-apt
install-mysql-client-apt:
	$(call print,Installing MySQL client)
	@sudo apt install libmysqlclient-dev -y

.PHONY: install-mysql-client
install-mysql-client:
	$(call print,Installing MySQL client)
	@brew install mysql-client pkg-config

.PHONY: install-main-python-deps
## Install main Python dependencies
install-main-python-deps:
	@pip3 install poetry
	@pip3 install tox

.PHONY: create-venv
## Create venv and install requirements
create-venv:
	$(call print,Creating venv)
	@poetry env use ${PYTHON_VERSION}
	@poetry install --no-root

.PHONY: create-tox-venv
create-tox-venv:
	$(call print,Creating tox venv and installing requirements)
	@tox -e py-requirements

.PHONY: create-venvs
## Create venv and tox venv and install requirements
create-venvs: create-venv create-tox-venv

.PHONY: yarn-install-locked
## Run yarn install using lockfile
yarn-install-locked:
	$(call print,Installing yarn dependencies using lockfile)
	@${CMD_FRONTEND} && \
	yarn install --immutable

.PHONY: create-db
## Create DB
create-db:
	$(call print,Creating DB)
	@source $(ENV_FILE) && \
	scripts/create_db.sh

.PHONY: load-initial-fixtures
## Load initial fixtures
load-initial-fixtures:
	$(call print,Loading initial fixtures)
	$(MAKE) manage arguments="loaddata lists"
	$(MAKE) manage arguments="loaddata actions"
	$(MAKE) manage arguments="loaddata providers"

.PHONY: bootstrap
## Bootstrap project
bootstrap: yarn-install-locked create-env-files create-venvs create-db migrate \
	load-initial-fixtures build

.PHONY: create-env-files
## Create env files
create-env-files: $(ENV_CUSTOM_FILE) $(ENV_SECRETS_FILE) $(DB_ENV_PROD_FILE) $(DOCKER_SECRETS_ENV_FILE)

$(DOCKER_SECRETS_ENV_FILE):
	$(call print,Creating docker secrets env file)
	@cp "${DOCKER_SECRETS_ENV_FILE}.tpl" $(DOCKER_SECRETS_ENV_FILE)

$(ENV_CUSTOM_FILE):
	$(call print,Creating env custom file)
	@cp $(ENV_CUSTOM_FILE).tpl $(ENV_CUSTOM_FILE)

$(ENV_SECRETS_FILE):
	$(call print,Creating env secrets file)
	@cp $(ENV_SECRETS_FILE).tpl $(ENV_SECRETS_FILE)

$(DB_ENV_PROD_FILE):
	$(call print,Creating DB env prod file)
	@cp $(DB_ENV_PROD_FILE).tpl $(DB_ENV_PROD_FILE)

#------------------------------------

#------------------------------------
# Scripts
#------------------------------------
.PHONY: pydiatra-script
pydiatra-script:
	scripts/pydiatra.sh

.PHONY: backup-db
backup-db:
	scripts/backup_db.sh

.PHONY: flush-cdn-cache
flush-cdn-cache:
	scripts/flush_cdn_cache.sh
#------------------------------------

#------------------------------------
# Tests
#------------------------------------
.PHONY: test
## Run tests | Tests
test: shellcheck hadolint shfmt actionlint tox eslint prettier-json-lint prettier-scss-lint \
	prettier-yaml-lint prettier-ts-lint prettier-html-lint prettier-vue-lint

.PHONY: test2
## Run tests 2 | Tests
test2: eslint prettier-json-lint prettier-scss-lint \
	prettier-yaml-lint prettier-ts-lint prettier-html-lint prettier-vue-lint

.PHONY: tox
## Run tox
tox:
	$(call print,Running tox)
	@tox

.PHONY: pydiatra
## Run pydiatra linter
pydiatra:
	$(call print,Running pydiatra)
	@tox -e py-pydiatra

.PHONY: pylint
## Run pylint linter
pylint:
	$(call print,Running pylint)
	@tox -e py-pylint

.PHONY: flake8
## Run flake8 linter
flake8:
	$(call print,Running flake8)
	@tox -e py-flake8

.PHONY: isort
## Run isort linter
isort:
	$(call print,Running isort linter)
	@tox -e py-isort

.PHONY: bandit
## Run bandit linter
bandit:
	$(call print,Running bandit)
	@tox -e py-bandit

.PHONY: rstlint
## Run rstlint linter
rstlint:
	$(call print,Running rstlint)
	@tox -e py-rstlint

.PHONY: pydocstyle
## Run pydocstyle linter
pydocstyle:
	$(call print,Running pydocstyle)
	@tox -e py-pydocstyle

.PHONY: safety
## Run safety linter
safety:
	$(call print,Running safety)
	@tox -e py-safety

.PHONY: pytest
## Run pytest
pytest:
	$(call print,Running pytest)
	@tox -e py-pytest

.PHONY: black
## Run black linter
black:
	$(call print,Running black linter)
	@tox -e py-black

.PHONY: mypy
## Run mypy linter
mypy:
	$(call print,Running mypy)
	@tox -e py-mypy

.PHONY: eslint
## Run eslint linter
eslint:
	$(call print,Running eslint linter)
	@${CMD_FRONTEND} && \
	yarn run eslint src/**/*.ts src/*.ts ./*.ts src/App.vue src/components/*.vue src/views/*.vue

.PHONY: shfmt
## Run shfmt linter
shfmt:
	$(call print,Running shfmt linter)
	@shfmt -l -d ./*.sh scripts/*.sh

.PHONY: shellcheck
## Run shellcheck linter
shellcheck:
	$(call print,Running shellcheck)
	@shellcheck scripts/*.sh ./*.sh

.PHONY: hadolint
## Run hadolint linter
hadolint:
	$(call print,Running hadolint)
	@hadolint Dockerfile

.PHONY: actionlint
## Run actionlint linter
actionlint:
	$(call print,Running actionlint)
	@actionlint

.PHONY: prettier-html-lint
## Run html linter
prettier-html-lint:
	$(call print,Running prettier check for html)
	@${CMD_FRONTEND} && \
	yarn run prettier --check ./*.html

.PHONY: prettier-ts-lint
## Run ts linter
prettier-ts-lint:
	$(call print,Running prettier check for ts)
	@${CMD_FRONTEND} && \
	yarn run prettier --check src/**/*.ts src/*.ts ./*.ts

.PHONY: prettier-scss-lint
## Run scss linter
prettier-scss-lint:
	$(call print,Running prettier check for scss)
	@${CMD_FRONTEND} && \
	yarn run prettier --check ./src/styles/*.scss

.PHONY: prettier-json-lint
## Run json linter
prettier-json-lint:
	$(call print,Running prettier check for json)
	@${CMD_FRONTEND} && \
	yarn run prettier --check ../**/*.json ../**/.*.json

.PHONY: prettier-yaml-lint
## Run yaml linter
prettier-yaml-lint:
	$(call print,Running prettier check for yaml)
	@${CMD_FRONTEND} && \
	yarn run prettier --check ../deployment/*.yaml ../.github/**/*.yaml

.PHONY: prettier-vue-lint
## Run vue linter
prettier-vue-lint:
	$(call print,Running prettier check for vue)
	@${CMD_FRONTEND} && \
	yarn run prettier --check src/App.vue src/components/*.vue src/views/*.vue
#------------------------------------

#------------------------------------
# Development
#------------------------------------
.PHONY: update-venvs
## Update packages in venv and tox venv with current requirements | Development
update-venvs:
	${SOURCE_CMDS} && \
	pip install -r requirements-dev.txt && \
	deactivate && \
	source .tox/py/bin/activate && \
	pip install -r requirements-dev.txt

.PHONY: delete-venvs
delete-venvs:
	$(call print,Deleting venvs)
	@rm -rf $(VENV_DIR)
	@rm -rf .tox

.PHONY: recreate-venvs
## Recreate venvs | Development
recreate-venvs: delete-venvs create-venvs

.PHONY: yarn-install
## Run yarn install
yarn-install:
	$(call print,Running yarn install)
	@${CMD_FRONTEND} && \
	yarn install

.PHONY: yarn-upgrade
## Run yarn upgrade
yarn-upgrade:
	$(call print,Running yarn upgrade)
	@${CMD_FRONTEND} && \
	yarn upgrade-interactive

.PHONY: dev
## Run yarn dev
dev:
	$(call print,Running yarn dev)
	@${CMD_FRONTEND} && \
	yarn dev

.PHONY: serve
## Run yarn serve
serve:
	$(call print,Running yarn serve)
	@${CMD_FRONTEND} && \
	yarn serve

.PHONY: build
## Run yarn build
build:
	$(call print,Running yarn build)
	@${CMD_FRONTEND} && \
	yarn build

.PHONY: drop-db
## Drop DB
drop-db:
	$(call print,Dropping DB)
	@source $(ENV_FILE) && \
	scripts/drop_db.sh

.PHONY: load-db
## Load DB from today's backup
load-db: drop-db create-db
	$(call print,Loading DB)
	@source $(ENV_FILE) && \
	scripts/load_db.sh

.PHONY: poetry-update
## Update python packages
poetry-update:
	$(call print,Updating python packages)
	@poetry update

.PHONY: poetry-show-outdated
## Show outdated python packages (outside of ranges)
poetry-show-outdated:
	$(call print,Showing outdated python packages)
	@poetry show --outdated | { grep --file=<(poetry show --tree | grep '^\w' | cut -d' ' -f1 | sed 's/.*/^&\\s/') || true; }

.PHONY: celery
## Run Celery
celery:
	${SOURCE_CMDS} && \
	cd src && \
	celery -A $(PROJECT).celery.app worker
#------------------------------------

#------------------------------------
# Formatting backend
#------------------------------------
.PHONY: format
## Format python code | Formatting backend
format:
	$(call print,Formatting python code)
	@${SOURCE_CMDS} && \
	autoflake --remove-all-unused-imports --in-place -r src && \
	isort src && \
	black .

.PHONY: f
## Format python code (format alias)
f: format
#------------------------------------


#------------------------------------
# Formatting miscellaneous
#------------------------------------
.PHONY: format-misc
## Format sh, json, yaml files | Formatting miscellaneous
format-misc: format-sh format-json format-yaml

.PHONY: format-sh
## Format sh files
format-sh:
	$(call print,Formatting sh files)
	@shfmt -l -w ./*.sh scripts/*.sh

.PHONY: format-json
## Format json files
format-json:
	$(call print,Formatting json files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write ../**/*.json ../**/.*.json

.PHONY: format-yaml
## Format yaml files
format-yaml:
	$(call print,Formatting yaml files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write ../deployment/*.yaml ../.github/**/*.yaml
#------------------------------------

#------------------------------------
# Formatting frontend
#------------------------------------
.PHONY: format-frontend
## Format files for frontend (vue, ts, scss, html) | Formatting frontend
format-frontend: format-html format-ts format-scss format-vue eslint-fix

.PHONY: ff
## Format files for frontend (vue, ts, scss, html) (format-frontend alias)
ff: format-frontend

.PHONY: format-ts
## Format ts files
format-ts:
	$(call print,Formatting ts files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write src/**/*.ts src/*.ts ./*.ts

.PHONY: eslint-fix
## Run eslint formatter
eslint-fix:
	@${CMD_FRONTEND} && \
	yarn run eslint src/**/*.ts src/*.ts ./*.ts src/App.vue src/components/*.vue src/views/*.vue --fix

.PHONY: format-scss
## Format scss files
format-scss:
	$(call print,Formatting scss files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write ./src/styles/*.scss

.PHONY: format-vue
## Format vue files
format-vue:
	$(call print,Formatting vue files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write src/App.vue src/components/*.vue src/views/*.vue

.PHONY: format-html
## Format html files
format-html:
	$(call print,Formatting html files)
	@${CMD_FRONTEND} && \
	yarn run prettier --write ./*.html
#------------------------------------

#------------------------------------
# Formatting all
#------------------------------------
.PHONY: format-all
## Format code | Formatting all
format-all: format format-sh format-json format-yaml format-frontend

.PHONY: fa
## Format code (format-all alias)
fa: format-all
#------------------------------------

#------------------------------------
# Django management commands
#------------------------------------
MANAGE_CMD := src/manage.py

.PHONY: runserver
## Run server for development | Django
runserver:
	$(call print,Running development server)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} runserver 0.0.0.0:8000

.PHONY: run
## Run server for development
run: runserver

.PHONY: migrate
## Run data migration
migrate:
	$(call print,Running data migration)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} migrate

.PHONY: collectstatic
## Collect static files
collectstatic:
	$(call print,Collecting static files)
	@${SOURCE_CMDS} && \
	export IS_DEV= && \
	${MANAGE_CMD} collectstatic --no-input

.PHONY: createsuperuser
## Create super user
createsuperuser:
	$(call print,Creating super user)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} createsuperuser

.PHONY: shell
## Run shell
shell:
	$(call print,Running Django shell)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} shell

.PHONY: makemigrations
## Run makemigrations command. Usage: make makemigrations arguments="[arguments]"
makemigrations:
	$(call print,Running makemigrations command with arguments `${arguments}`)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} makemigrations $(arguments) ${APP}

ifeq (manage,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(MANAGE_ARGS):;@:)
endif

.PHONY: manage
## Run management command. Usage: make manage [command] arguments="[arguments]"
manage:
	$(call print, Running management command `${MANAGE_ARGS} ${arguments}`)
	${SOURCE_CMDS} && \
	${MANAGE_CMD} ${MANAGE_ARGS} $(arguments)
#------------------------------------

#------------------------------------
# Docker commands
#------------------------------------
export DOCKER_ENV_FILE := docker.env

#------------------------------------
# Docker commands
#------------------------------------
export DOCKER_ENV_FILE := docker.env

.PHONY: docker-build-dev
## Build docker images | Docker
docker-build-dev: docker-build-backend docker-build-frontend-dev

.PHONY: docker-build-backend
## Build docker backend image
docker-build-backend:
	$(call print,Building Docker backend image)
	@docker build -t "${PROJECT}:backend" .

.PHONY: docker-build-frontend-dev
## Build docker frontend image
docker-build-frontend-dev:
	$(call print,Building Docker frontend image)
	docker build --build-arg VITE_BACKEND_URL="http://localhost:8000/" -t "${PROJECT}:frontend" ./frontend

.PHONY: docker-run
## Run server in docker
docker-run: collectstatic
	$(call print,Running server in docker)
	@docker-compose up

.PHONY: docker-sh
## Run docker shell
docker-sh:
	$(call print,Running docker shell)
	@docker run -ti --env-file ${DOCKER_ENV_FILE} --env-file $(DOCKER_SECRETS_ENV_FILE) ${PROJECT}:backend sh

.PHONY: docker-mypy
## Run mypy in docker
docker-mypy:
	$(call print,Running mypy in docker)
	@docker run -v .:/app ${PROJECT}:backend /app/scripts/docker_test.sh
#------------------------------------

#------------------------------------
# Production commands
#------------------------------------
.PHONY: prod-create-db
## Create prod db | Production
prod-create-db:
	source $(DB_ENV_PROD_FILE) && \
	scripts/create_db.sh

.PHONY: prod-drop-db
## Drop prod db
prod-drop-db:
	source $(DB_ENV_PROD_FILE) && \
	scripts/drop_db.sh

.PHONY: prod-load-db
## Load db to prod from today's backup
prod-load-db: prod-drop-db prod-create-db
	source $(DB_ENV_PROD_FILE) && \
	scripts/load_db.sh

.PHONY: prod-connect-db
## Connect to prod db
prod-connect-db:
	source $(DB_ENV_PROD_FILE) && \
	scripts/connect_db.sh

ifeq (prod-manage,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  PROD_MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(PROD_MANAGE_ARGS):;@:)
endif

.PHONY: prod-manage
## Run management command in prod. Usage: make prod-manage [command] arguments="[arguments]"
prod-manage:
	scripts/run_management_command_prod.sh ${PROD_MANAGE_ARGS} $(arguments)

ifeq (prod-manage-interactive,$(firstword $(MAKECMDGOALS)))
  # Use the rest as arguments
  PROD_MANAGE_INTERACTIVE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(PROD_MANAGE_INTERACTIVE_ARGS):;@:)
endif

.PHONY: prod-manage-interactive
## Run management command in prod (interactive). Usage: make prod-manage [command] arguments="[arguments]"
prod-manage-interactive:
	scripts/run_management_command_interactive_prod.sh ${PROD_MANAGE_INTERACTIVE_ARGS} $(arguments)

.PHONY: prod-shell
## Run shell in prod
prod-shell:
	scripts/run_shell_prod.sh

.PHONY: prod-migrate
## Run data migration for prod
prod-migrate:
	scripts/run_management_command_prod.sh migrate

.PHONY: prod-enable-debug
## Enable debug in prod. It will be reset with the next deployment
prod-enable-debug:
	yq eval '.data.DEBUG="True"' deployment/configmap.yaml | kubectl apply -f -
	kubectl rollout restart "deployment/${PROJECT}"

.PHONY: prod-load-initial-fixtures
## Load initial fixtures in prod
prod-load-initial-fixtures:
	$(MAKE) prod-manage arguments="loaddata lists"
	$(MAKE) prod-manage arguments="loaddata actions"
	$(MAKE) prod-manage arguments="loaddata providers"
	$(MAKE) prod-manage arguments="loaddata vk_countries"
#------------------------------------
