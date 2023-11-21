#!/bin/bash
#SBATCH --nodes=1                    # node
#SBATCH --ntasks-per-node=128   # tasks per node
#SBATCH --time=22:00:00               # time limits: 1 hour
#SBATCH --partition=compute
#SBATCH --account=TG-IBN140002
#SBATCH --export=ALL
#SBATCH --mail-user=conrad.bittencourt@gmail.com
#SBATCH --mail-type=end

srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_0_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_0_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_1_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v108_batch1/v108_batch1_0_cfg.json netParams=../data/v108_batch1/v108_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v108_batch1/v108_batch1_1_cfg.json netParams=../data/v108_batch1/v108_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v108_batch1/v108_batch1_2_cfg.json netParams=../data/v108_batch1/v108_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v108_batch1/v108_batch1_3_cfg.json netParams=../data/v108_batch1/v108_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v108_batch1/v108_batch1_4_cfg.json netParams=../data/v108_batch1/v108_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_2_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_3_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py
srun ./x86_64/special -mpi -python init.py simConfig=../data/v107_batch1/v107_batch1_4_cfg.json netParams=../data/v107_batch1/v107_batch1_netParams.py

