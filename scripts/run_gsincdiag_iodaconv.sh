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
source $IODA_iodaconv_modulefile

# make working directory
rm -rf $IODA_data_iodaworkdir
mkdir -p $IODA_data_iodaworkdir
cd $IODA_data_iodaworkdir

# make output directory
rm -rf $IODA_data_iodaoutdir
mkdir -p $IODA_data_iodaoutdir

#
# run script
python ./proc_gsi_ncdiag.py -n 24 -o $OutDir/obs -g $OutDir/geoval $OutDir/GSI_diags
$IODA_iodaconv_iodaconvbin -n 24 -o $IODA_data_iodaoutdir $IODA_data_gsiindir

if [[ "$IODA_iodaconv_cleanup" = "true" ]]; then
  cd $IODA_data_iodaoutdir
  rm -rf $IODA_data_iodaworkdir
fi
date
echo "GSI ncdiag ioda converter script completed"
