#!/bin/bash
# get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

${SCRIPT_DIR}/../testfiles/osu_mbw_mr -m 2097152:2097152 | grep -v "#" | awk '{print $2}'
