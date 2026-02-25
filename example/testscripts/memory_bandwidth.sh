#!/bin/bash
./testfiles/stream.100M | grep Triad | awk '{print $2}'
