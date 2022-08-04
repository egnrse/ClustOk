#!/bin/bash
/home/hinkel/tests/osu_latency -m 2097152:2097152 | grep -v "#" | awk '{print $2}'