#!/bin/bash
module load compilers/icc
icc --version || module unload compilers/icc
module unload compilers/icc