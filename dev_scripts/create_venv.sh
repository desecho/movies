#!/bin/bash

set -eu

cd $(dirname "$0")

source ../venv/bin/activate
pip install -r ../requirements-dev.txt
