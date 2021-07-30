#!/bin/bash
# run_gsincdiag_iodaconv.sh
# run python ioda-iodaconverters
# on GSI netCDF diag files to generate
# IODA formatted observations for UFO H(x)
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
   eval $(parse_yaml $YAMLFILE "IODA_")
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

# source modulefile to get proper python on environment
source $IODA_env_modulefile

# make working directory
rm -rf $IODA_data_iodaworkdir
mkdir -p $IODA_data_iodaworkdir
cd $IODA_data_iodaworkdir

# make output directory
rm -rf $IODA_data_iodaoutdir
mkdir -p $IODA_data_iodaoutdir

#
# run script to generate IODA obs files
$IODA_iodaconv_iodaconvbin -n 20 -o $IODA_data_iodaoutdir $IODA_data_gsiindir

# concatenate these files together
adate=$IODA_time_year$IODA_time_month$IODA_time_day$IODA_time_cycle
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/sfc_*.nc4 -o $IODA_data_iodaoutdir/sfc_obs_"$adate".nc4
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/sfcship_*.nc4 -o $IODA_data_iodaoutdir/sfcship_obs_"$adate".nc4
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/aircraft_*.nc4 -o $IODA_data_iodaoutdir/aircraft_obs_"$adate".nc4
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/sondes_ps*.nc4 $IODA_data_iodaoutdir/sondes_q*.nc4 $IODA_data_iodaoutdir/sondes_tsen*.nc4 $IODA_data_iodaoutdir/sondes_uv*.nc4 -o $IODA_data_iodaoutdir/sondes_obs_"$adate".nc4
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/sondes_ps*.nc4 $IODA_data_iodaoutdir/sondes_q*.nc4 $IODA_data_iodaoutdir/sondes_tv*.nc4 $IODA_data_iodaoutdir/sondes_uv*.nc4 -o $IODA_data_iodaoutdir/sondes_tvirt_obs_"$adate".nc4

# gnssro converter
$IODA_iodaconv_iodaconvgnssrobin $IODA_data_gsiindir/diag_conv_gps_* $IODA_data_iodaoutdir/gnssro_${adate}.nc4

if [[ "$IODA_data_restricted" = "true" ]]; then
  chgrp rstprod $IODA_data_iodaoutdir/*
  chmod 640 $IODA_data_iodaoutdir/*
fi

if [[ "$IODA_iodaconv_cleanup" = "true" ]]; then
  cd $IODA_data_iodaoutdir
  rm -rf $IODA_data_iodaworkdir
fi
date
echo "GSI ncdiag ioda converter script completed"
