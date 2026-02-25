#!/bin/bash
./testfiles/measure_clock_drift_new --steps=1 --print-procs-ratio=1 --nrep=10  --clock-sync=None | grep -o "0.000000000   1.*" | awk '{print $3}'
