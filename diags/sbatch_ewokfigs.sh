#!/bin/bash
#SBATCH --ntasks-per-node 40
#SBATCH -A da-cpu
#SBATCH -J gen_ewok_figs
#SBATCH -t 00:30:00
#SBATCH -q debug
#SBATCH --nodes 1

set -x
##### user defined variables here #####
# bash script to setup environment
IODARC=/work/noaa/da/Cory.R.Martin/noscrub/UFO_eval/env/ioda_diags.env.bash
# start and end cycle to process
SCYCLE=2020121700
ECYCLE=2020121718
# name of experiment in R2D2
EXPNAME='a00f'
# name of R2D2 database
R2D2DB='local'
# name of model
R2D2MODEL='gfs'
# top level stage/work directory
ROOTWORK=/work/noaa/stmp/cmartin/diags
# list of observations to process
OBSTYPES='
- sondes
- sfc
- sfcship
- amsua_n19
'
# procCycle path
PROCCYCLE=/work/noaa/da/Cory.R.Martin/noscrub/UFO_eval/DARTH/diags/procCycle.py
# genSite path
GENSITE=/work/noaa/da/Cory.R.Martin/noscrub/UFO_eval/DARTH/diags/genSite.py

##### should be no need to touch below this line #####
################################################################################
# load environment
source $IODARC

# create stage directory
mkdir -p $ROOTWORK/$EXPNAME

# loop through cycles
ICYCLE=$SCYCLE
while test $ICYCLE -le $ECYCLE ; do
  # create YAML
  cat > $ROOTWORK/$EXPNAME/${ICYCLE}_procCycle.yaml << EOF
stage: $ROOTWORK/$EXPNAME
model: ${R2D2MODEL}
experiment: ${EXPNAME}
cycle: ${ICYCLE}
database: ${R2D2DB}
obs_types:
${OBSTYPES}
EOF
  # run procCycle
  # todo: once procCycle has each diag in parallel, remove this pseudo parallel stuff below 
  $PROCCYCLE ${ROOTWORK}/${EXPNAME}/${ICYCLE}_procCycle.yaml > ${ROOTWORK}/${EXPNAME}/${ICYCLE}.log 2>&1 &
  sleep 10 # sleep 10 seconds before continuing in loop
  # update time
  PDY=${ICYCLE::8} ; CYC=${ICYCLE:8}
  ICYCLE=$(date -d "$PDY ${CYC} + 6 hours" +%Y%m%d%H)
done

wait # wait for all python processes to end

# generate website
$GENSITE --htmldir ${ROOTWORK}/${EXPNAME}/DARTH/html --expnane ${EXPNAME}
