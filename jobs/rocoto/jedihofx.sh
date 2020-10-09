#!/bin/bash
# DARTHjedihofx.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}

# run the script for this job with the specified YAML
$HOMEDARTH/scripts/run_fv3jedi_hofx_nomodel.sh $ROTDIR/$adate/YAML/run_fv3jedi_hofx_${adate}.yaml || exit 1

date
echo "jedihofx.sh completed"
exit 0
