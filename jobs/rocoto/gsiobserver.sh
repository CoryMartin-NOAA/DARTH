#!/bin/bash
# DARTHgsiobserver.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}

# run the script for this job with the specified YAML
$HOMEDARTH/scripts/run_gsi_observer.sh $ROTDIR/$adate/YAML/run_gsi_observer_${adate}.yaml

date
echo "gsiobserver.sh completed"
exit 0
