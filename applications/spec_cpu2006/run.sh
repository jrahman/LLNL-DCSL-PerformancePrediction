#!/bin/bash

usage() {
    echo "Usage: run.sh SPEC_DIR DATA_DIR BMARK_NAME"
}

if [ $# -ne 3 ]; then
    usage
    exit 1
fi

SPEC_DIR=${1}
DATA_DIR=${2}
BMARK_NAME=${3}

BASE_DIR=$(dirname $0)/

echo "Run: Starting now..."
${SPEC_DIR}/bin/runspec -c custom-linux64.cfg --nobuild --noreportable --action run 
if [ $? -ne 0 ]; then
    echo "Error: Failed to run the benchmark"
    exit 1
fi
cat "${SPEC_DIR}/benchspec/${BMARK_NAME}/
echo "Run: Completed"

exit 0
