#!/bin/bash
# DARTHprep.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}

# create subdirectories for this cycle
mkdir -p $ROTDIR/$adate/YAML

# generate the YAML for this cycle
python $HOMEDARTH/scripts/gen_cycle_yaml.py -y $TOPYAML -d $adate -o $ROTDIR/$adate/YAML/DARTH_cycle_${adate}.yaml || exit 1

# generate the YAML for all subsequent jobs
python $HOMEDARTH/scripts/setup_proc_cycle.py -y $ROTDIR/$adate/YAML/DARTH_cycle_${adate}.yaml || exit 1

date
echo "prep.sh completed"
exit 0
