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
rm -rf $IODA_data_iodaoutdir/obs
mkdir -p $IODA_data_iodaoutdir/obs
rm -rf $IODA_data_iodaoutdir/geoval
mkdir -p $IODA_data_iodaoutdir/geoval

#
# run script to generate IODA obs files
$IODA_iodaconv_iodaconvbin -n 20 -o $IODA_data_iodaoutdir/obs -g $IODA_data_iodaoutdir/geoval $IODA_data_gsiindir

# concatenate these files together
adate=$IODA_time_year$IODA_time_month$IODA_time_day$IODA_time_cycle
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/obs/sfc_*.nc4 -o $IODA_data_iodaoutdir/obs/sfc_obs_"$adate".nc4 -g $IODA_data_iodaoutdir/geoval/
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/obs/sfcship_*.nc4 -o $IODA_data_iodaoutdir/obs/sfcship_obs_"$adate".nc4 -g $IODA_data_iodaoutdir/geoval/
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/obs/aircraft_*.nc4 -o $IODA_data_iodaoutdir/obs/aircraft_obs_"$adate".nc4 -g $IODA_data_iodaoutdir/geoval/
python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/obs/sondes_ps*.nc4 $IODA_data_iodaoutdir/obs/sondes_q*.nc4 $IODA_data_iodaoutdir/obs/sondes_tsen*.nc4 $IODA_data_iodaoutdir/obs/sondes_tv*.nc4 $IODA_data_iodaoutdir/obs/sondes_uv*.nc4 -o $IODA_data_iodaoutdir/obs/sondes_obs_"$adate".nc4 -g $IODA_data_iodaoutdir/geoval/
#python $IODA_iodaconv_iodacombinebin -i $IODA_data_iodaoutdir/obs/sondes_ps*.nc4 $IODA_data_iodaoutdir/obs/sondes_q*.nc4 $IODA_data_iodaoutdir/obs/sondes_tv*.nc4 $IODA_data_iodaoutdir/obs/sondes_uv*.nc4 -o $IODA_data_iodaoutdir/obs/sondes_tvirt_obs_"$adate".nc4 -g $IODA_data_iodaoutdir/geoval/

# gnssro converter
ln -sf $IODA_data_iodaoutdir/obs/gnssro_obs_${adate}.nc4 ./gnssro_obs_${adate}.nc4
ln -sf $IODA_data_iodaoutdir/geoval/gnssro_geoval_${adate}.nc4 ./gnssro_geoval_${adate}.nc4
$IODA_iodaconv_iodaconvgnssrobin $adate $IODA_data_gsiindir/diag_conv_gps_* 1

# convert from v1 to v2 of IODA
rm -rf $IODA_data_iodaoutdir/obs_v1
mkdir -p $IODA_data_iodaoutdir/obs_v1
mv $IODA_data_iodaoutdir/obs/* $IODA_data_iodaoutdir/obs_v1/.
for ifile in `ls $IODA_data_iodaoutdir/obs_v1/`; do
  ofile=`basename $ifile`
  $IODA_iodaconv_iodaconvv2bin $IODA_data_iodaoutdir/obs_v1/$ifile $IODA_data_iodaoutdir/obs/$ofile
done

if [[ "$IODA_data_restricted" = "true" ]]; then
  chgrp rstprod $IODA_data_iodaoutdir/obs/*
  chmod 640 $IODA_data_iodaoutdir/obs/*
  chgrp rstprod $IODA_data_iodaoutdir/obs_v1/*
  chmod 640 $IODA_data_iodaoutdir/obs_v1/*
fi

if [[ "$IODA_iodaconv_cleanup" = "true" ]]; then
  cd $IODA_data_iodaoutdir
  rm -rf $IODA_data_iodaworkdir
fi
date
echo "GSI ncdiag ioda converter script completed"
