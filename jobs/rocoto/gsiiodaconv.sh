#!/bin/bash
# DARTHgsiiodaconv.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}

# run the script for this job with the specified YAML
$HOMEDARTH/scripts/run_gsincdiag_iodaconv.sh $ROTDIR/$adate/YAML/run_gsinc_iodaconv_${adate}.yaml || exit 1

date
echo "gsiiodaconv.sh completed"
exit 0
