#!/bin/bash
#SBATCH --job-name=v200_batch2_0
#SBATCH -A TG-IBN140002
#SBATCH -t 0:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH -o ../data/v200_batch2/v200_batch2_0.run
#SBATCH -e ../data/v200_batch2/v200_batch2_0.err
#SBATCH --mail-user=fernandodasilvaborges@gmail.com
#SBATCH --mail-type=end

#SBATCH --mem=512G
#SBATCH --export=ALL
#SBATCH --partition=large-shared
source ~/.bashrc
cd /home/fborges/S1_HFO/sim/
mpirun -n 64 nrniv -python -mpi init.py simConfig=../data/v200_batch2/v200_batch2_0_cfg.json netParams=../data/v200_batch2/v200_batch2_netParams.py
wait
    