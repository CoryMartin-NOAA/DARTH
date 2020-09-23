#!/bin/bash
# run_gsi_observer.sh
# run GSI observer for a specified
# analysis cycle and subset of observations
# cory.r.martin@noaa.gov
set -x
# variable definitions
SCRIPTDIR=`dirname "$0"`
USHDIR=$SCRIPTDIR/../ush
YAMLFILE=$1
# source helper functions
source $USHDIR/parse_yaml.sh

# read YAML config file
if [[ -e $YAMLFILE ]]; then
#  eval $(parse_yaml $YAMLFILE "gfs" "analysis time")
   parse_yaml $YAMLFILE GSI
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

env
