#!/bin/bash
/usr/local/sbin/clustOk/testfiles/stream.100M | grep Triad | awk '{print $2}'
