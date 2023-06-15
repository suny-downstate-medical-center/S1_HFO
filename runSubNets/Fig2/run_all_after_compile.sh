#!/bin/bash

for i in {0..1034..8}; do 
   echo $i | time -f "Elapsed Time = %E, CPU Usage = %P, CPU Time= %S, Job = $i" -o time.txt --append ipython compare_somatic_efel.py $i 
done

