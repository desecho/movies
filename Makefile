.PHONY: install upgrade flake8 coverage travis pylint

install:
	pip install -r requirements-dev.txt

upgrade:
	pip install -r requirements-dev.txt -U

flake8:
	flake8

isort:
	isort --check-only --recursive --diff src

coverage:
	py.test --cov-report term-missing --cov src

pylint:
	pylint src

travis: install flake8 isort coverage
#travis: install pylint flake8 isort coverage
