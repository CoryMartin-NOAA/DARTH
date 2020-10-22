#!/bin/bash
# DARTHpost.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}

# run the script for this job with the specified YAML
$HOMEDARTH/scripts/run_post.sh $ROTDIR/$adate/YAML/run_post_${adate}.yaml || exit 1

date
echo "post.sh completed"
exit 0
