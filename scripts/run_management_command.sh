#!/bin/bash

set -eou pipefail

POD_ID=$(kubectl get pods -lapp="$PROJECT" | grep Running | awk '{print $1}')
kubectl exec "$POD_ID" -- ./manage.py "$@"
