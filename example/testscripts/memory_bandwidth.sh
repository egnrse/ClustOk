#!/bin/bash
# get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

${SCRIPT_DIR}/../testfiles/stream.100M | grep Triad | awk '{print $2}'
