#!/bin/bash
infile=${1:-INFILE}
cp ./Preprocessing/MESH .
cp ./Preprocessing/INCON .
cp ./Preprocessing/${infile} .
mpiexec -n 4 tough3-eco2n ${infile}
toughio-export OUTPUT_ELEME.csv -m Preprocessing/mesh.pickle -f xdmf -o output.xdmf
