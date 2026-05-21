#!/bin/bash
# get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

${SCRIPT_DIR}/../testfiles/measure_clock_drift_new --steps=1 --print-procs-ratio=1 --nrep=10  --clock-sync=None | grep -o "0.000000000   1.*" | awk '{print $3}'
