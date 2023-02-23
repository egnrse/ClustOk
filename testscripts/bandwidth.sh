#!/bin/bash
/home/hinkel/clustok/testfiles/osu_mbw_mr -m 2097152:2097152 | grep -v "#" | awk '{print $2}'