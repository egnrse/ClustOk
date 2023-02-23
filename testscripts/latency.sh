#!/bin/bash
/home/hinkel/clustok/testfiles/osu_latency -m 2097152:2097152 | grep -v "#" | awk '{print $2}'