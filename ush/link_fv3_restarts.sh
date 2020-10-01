#!/bin/bash
# link_fv3_restarts.sh
# symbolically link FV3 RESTART tiles
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
   eval $(parse_yaml $YAMLFILE "FV3_")
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

NDATE=${NDATE:-`which ndate`}
ncpc=/bin/cp
ncpl="ln -fs"

## get analysis/guess date
adate=$FV3_time_year$FV3_time_month$FV3_time_day$FV3_time_cycle
PDYa=`echo $adate | cut -c1-8`
cyca=`echo $adate | cut -c9-10`
gdate=`$NDATE -06 $adate`
PDYg=`echo $gdate | cut -c1-8`
cycg=`echo $gdate | cut -c9-10`

## GFSv16 adds /atmos/ to the guess dir
if [[ "$FV3_background_gfsv16" = "true" ]]; then
  atmos=atmos
fi

# Calculate RESTART directory path
datges=${FV3_background_guessdir}/${GSI_observations_dump}.${PDYg}/${cycg}/${atmos}/RESTART

# RESTART time string
RSTPREFIX=$PDYa.${cyca}0000
RSTGLOBAL=".coupler.res .fv_core.res.nc"
RSTTILES=".fv_core.res .fv_srf_wnd.res .fv_tracer.res .phy_data .sfc_data"

# loop through files that are not per each cubed-sphere tile
for file in $RSTGLOBAL; do
  RSTFILEIN=$datges/$RSTPREFIX$file
  RSTFILEOUT=$FV3_hofx_workdir/$RSTPREFIX$file
  $ncpl $RSTFILEIN $RSTFILEOUT
done

# loop through files that are one per cubed-sphere tile
for ((tile=1;tile<=6;tile++)); do
  TILESUFFIX=tile${tile}.nc
  for file in $RSTTILES; do
    RSTFILEIN=$datges/${RSTPREFIX}${file}.${TILESUFFIX}
    RSTFILEOUT=$FV3_hofx_workdir/${RSTPREFIX}${file}.${TILESUFFIX}
    $ncpl $RSTFILEIN $RSTFILEOUT
  done
done

exit 0
