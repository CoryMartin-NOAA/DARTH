#!/bin/bash
# run_fv3jedi_hofx_nomodel.sh
# run JEDI H(x) application on FV3 RESTART tiles
# cory.r.martin@noaa.gov
set -x
## variable definitions
SCRIPTDIR=`dirname "$0"`
USHDIR=$SCRIPTDIR/../ush
YAMLFILE=$1
## source helper functions
source $USHDIR/parse_yaml.sh

## read YAML config file
if [[ -e $YAMLFILE ]]; then
   eval $(parse_yaml $YAMLFILE "JEDI_")
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

## load JEDI runtime environment


## rm, make, and cd to working directory
rm -rf $JEDI_hofx_workdir
mkdir -p $JEDI_hofx_workdir
cd $JEDI_hofx_workdir

## link executable
ln -fs $JEDI_hofx_executable $JEDI_hofx_workdir/fv3jedi_hofx_nomodel.x

## run H(x)
$JEDI_env_launcher ./fv3jedi_hofx_nomodel.x $JEDI_hofx_yamlfile

## concatenate files
