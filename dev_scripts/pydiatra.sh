#!/bin/bash

set -eu

result=$(find src -name '*.py' -exec py3diatra {} \;)
if [[ $result ]]; then
	echo $result
	exit 1
fi
