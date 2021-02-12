#!/bin/bash
# link_fv3jedi_hofx_fix.sh
# symbolically link FV3-JEDI fix files
# cory.r.martin@noaa.gov
set -x
## variable definitions
USHDIR=`dirname "$0"`
SCRIPTDIR=$USHDIR/../scripts
YAMLFILE=$1
## source helper functions
source $USHDIR/parse_yaml.sh

## read YAML config file
if [[ -e $YAMLFILE ]]; then
   eval $(parse_yaml $YAMLFILE "HOFX_")
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

NDATE=${NDATE:-`which ndate`}
ncpc=/bin/cp
ncpl="ln -fs"

LEVS=$HOFX_background_levs

# akbk file
$ncpl $HOFX_fix_fixfv3jedi/fv3files/akbk${LEVS}.nc4 $HOFX_hofx_workdir/Data/fv3files/akbk${LEVS}.nc4
# FMS namelist file
$ncpl $HOFX_fix_fixfv3jedi/fv3files/fmsmpp.nml $HOFX_hofx_workdir/Data/fv3files/fmsmpp.nml
# field table file
$ncpl $HOFX_fix_fixfv3jedi/fv3files/field_table $HOFX_hofx_workdir/Data/fv3files/field_table # more generic later?

# link fieldsets
$ncpl $HOFX_fix_fixfv3jedi/fieldsets/dynamics.yaml $HOFX_hofx_workdir/Data/fieldsets/dynamics.yaml
$ncpl $HOFX_fix_fixfv3jedi/fieldsets/ufo.yaml $HOFX_hofx_workdir/Data/fieldsets/ufo.yaml

# link CRTM files
$ncpl $HOFX_fix_fixcrtm $HOFX_hofx_workdir/Data/crtm

exit 0
