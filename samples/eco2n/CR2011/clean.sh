#!/bin/bash
rm -f `ls | grep -v "^clean.sh$\|^run.sh$\|^CO2TAB$\|^Preprocessing$\|^Postprocessing$"`
rm -rf TABLE .OUTPUT_*