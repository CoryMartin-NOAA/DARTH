#!/bin/bash
#SBATCH -J run_gsi_observer 
#SBATCH -A da-cpu
#SBATCH --nodes=30
#SBATCH --ntasks-per-node=8
#SBATCH -q debug 
##SBATCH -q batch 
#SBATCH -t 00:30:00

ScriptDir=/scratch1/NCEPDEV/da/Cory.R.Martin/GitHub/DARTH/scripts

cd $ScriptDir

./run_gsi_observer.sh test.yaml
