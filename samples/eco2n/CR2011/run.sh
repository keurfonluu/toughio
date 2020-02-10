#!/bin/bash
infile=${1:-INFILE}
cp ./Preprocessing/MESH .
cp ./Preprocessing/INCON .
cp ./Preprocessing/${infile} .
time mpiexec -n 4 tough3-eco2n ${infile}
