#!/bin/bash

set -eou pipefail

shellcheck scripts/*.sh ./*.sh
