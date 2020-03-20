#!/bin/bash
rm -f `ls | grep -v "^clean.sh$\|^run.sh$\|^CO2TAB$\|^Preprocessing$\|^Postprocessing$\|^README.md$"`
rm -rf TABLE .OUTPUT_*