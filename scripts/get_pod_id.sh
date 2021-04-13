#!/bin/bash

set -eu

echo $(kubectl get pods -lapp=$PROJECT | grep Running | awk '{print $1}')
