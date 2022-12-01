#!/bin/bash
#date "+%Y%m%d%H%M%S%6N"
/home/hinkel/clustok/testfiles/measure_clock_drift_new | awk 'NR==10{ print; }' | awk '{print $3}'
