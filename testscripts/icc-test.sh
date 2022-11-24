#!/bin/bash
module load compilers/icc
icc --version >> /dev/null && echo true || module unload compilers/icc
module unload compilers/icc
