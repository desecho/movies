#!/bin/bash

result=$(find src -name '*.py' -exec py3diatra {} \;)
echo $result
if [[ $result ]]; then
	exit 1
fi
