#!/bin/bash
# DARTHprep.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

# generate the YAML for this cycle
adate=${PDY}${cyc}
mkdir -p $ROTDIR/$adate/$YAML
python $HOMEDARTH/scripts/gen_cycle_yaml.py -y $TOPYAML -d $adate -o $ROTDIR/$adate/YAML/DARTH_cycle_${adate}.yaml || exit 1

# generate the YAML for all subsequent jobs
python $HOMEDARTH/setup_proc_cycle.py -y $ROTDIR/$adate/YAML/DARTH_cycle_${adate}.yaml || exit 1

date
echo "prep.sh completed"
exit 0
