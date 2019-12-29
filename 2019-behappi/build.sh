#!/bin/bash
CXX=clang++
mkdir -p bin
$CXX solver.cpp -o -Wextra -Werror -pedantic -O3 -std=c++11 -o bin/solver
