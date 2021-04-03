#!/bin/bash

set -eu

echo $(kubectl get pods -lapp=movies | grep Running | awk '{print $1}')
