#!/bin/bash
# DARTHprep.sh
set -x
env

# load modules used by all jobs; for python3, etc.
source $HOMEDARTH/ush/load_modules_darth.sh || exit 1

adate=${PDY}${cyc}
NDATE=${NDATE:-`which ndate`}
gdate=`$NDATE -06 $adate`

# cd to $ROTDIR
mkdir -p $GESDIR
cd $GESDIR

# grab things via HPSS
if [[ "$CDUMP" = "gdas" ]] ; then
  ## TODO make this more explicit so it runs faster
  htar -xvf $HPSSROOT/$gdate/${CDUMP}.tar ./
  htar -xvf $HPSSROOT/$gdate/${CDUMP}_restarta.tar ./
  htar -xvf $HPSSROOT/$gdate/${CDUMP}_restartb.tar ./
else
  echo "$CDUMP not currently supported" && exit 1
fi
