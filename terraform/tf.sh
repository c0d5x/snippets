#!/bin/bash

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
PREFIX="gl"
ENVIRONMENT="${PWD##*/}"
BUCKET="${PREFIX}-remote-state-${ENVIRONMENT}"
STATE_FILE="terraform.tfstate"
ARGS=$*

remote() {
    terraform remote config \
        -backend=s3 \
        -backend-config="region=${REGION}" \
        -backend-config="bucket=${BUCKET}" \
        -backend-config="key=${STATE_FILE}"
}

run() {
    terraform $ARGS
}


type terraform >/dev/null 2>&1 || {
    echo >&2 "'terraform' not found"
    exit 1
}

echo Region: $REGION
echo Prefix: $PREFIX
echo Environment: $ENVIRONMENT
echo State Bucket: $BUCKET
echo State File: $STATE_FILE


if ! terraform remote pull ; then 
    remote
fi

run
