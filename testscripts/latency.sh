#!/bin/bash
/usr/local/sbin/clustOk/testfiles/osu_latency -m 2097152:2097152 | grep -v "#" | awk '{print $2}'
