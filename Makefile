.DEFAULT_GOAL := help

# COLORS
RED     :=\033[0;31m
GREEN   :=\033[0;32m
YELLOW  :=\033[0;33m
BLUE    :=\033[0;34m
MAGENTA :=\033[0;35m
CYAN    :=\033[0;36m
WHITE   :=\033[0;37m
RESET   :=\033[0;10m

TARGET_MAX_CHAR_NUM := 20

.PHONY: create-venv
## Create virtual environment and install requirements
create-venv:
	dev_scripts/create_venv.sh


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

.PHONY: install-deps
## Install dependencies
install-deps:
	# Install Python
	sudo apt install python3.7 python3.7-venv python3.7-dev -y
	# Install MySQL dependencies
	sudo apt install libmysqlclient-dev -y

.PHONY: pydiatra
## Run pydiatra
pydiatra:
	dev_scripts/pydiatra.sh

.PHONY: yarn-build
## Run yarn build
yarn-build:
	yarn build

.PHONY: yarn-install
## Run yarn install
yarn-install:
	rm yarn.lock
	yarn install

.PHONY: yarn-install-locked
## Run yarn install using lockfile
yarn-install-locked:
	yarn install --frozen-lockfile

.PHONY: eslint
## Run eslint
eslint:
	yarn run eslint "./*.js"
	yarn run eslint "src/moviesapp/js/*"

.PHONY: test
## Run tests
test:
	tox
