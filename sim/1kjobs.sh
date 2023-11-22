#!/bin/bash
#SBATCH --nodes=35                    # node
#SBATCH --ntasks-per-node=48   # tasks per node
#SBATCH --time=5:00:00               # time limits: 24 hours
#SBATCH --partition=g100_usr_prod
#SBATCH --qos=g100_qos_bprod
#SBATCH --account=icei_H_King

srun ./x86_64/special -mpi -python init.py simConfig=../data/v122_batch1/v122_batch1_0_cfg.json netParams=../data/v122_batch1/v122_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py 


