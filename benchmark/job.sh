#!/bin/bash
# Submete o benchmark na atlantica (nos exclusivos):
#   sbatch -N 1 -t 06:00:00 job.sh seq dcseq     # referencias em 1 core
#   sbatch job.sh forte muitos                   # versoes MPI em 2 nos
#   sbatch job.sh extra                          # envio bloqueante e -m cyclic
#SBATCH -N 2
#SBATCH --exclusive
#SBATCH -t 06:00:00
#SBATCH -J t3-dc
#SBATCH -o job-%j.log

export PATH=/LADAPPs/OpenMPI/openmpi-4.1.1/bin:$PATH
cd "$SLURM_SUBMIT_DIR"
echo "nos: $SLURM_JOB_NODELIST"
python3 -u benchmark.py "$@"
