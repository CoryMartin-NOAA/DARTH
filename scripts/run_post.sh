#!/bin/bash
# run_post.sh
# generate automated figures/stats/etc.
# using post processing python scripts developed by
# kevin.dougherty@noaa.gov for GSI - UFO evaluation
# cory.r.martin@noaa.gov
set -x
## variable definitions
SCRIPTDIR=`dirname "$0"`
USHDIR=$SCRIPTDIR/../ush
PyGSIDir=$SCRIPTDIR/../sorc/PyGSI
YAMLFILE=$1
## source helper functions
source $USHDIR/parse_yaml.sh

## read YAML config file
if [[ -e $YAMLFILE ]]; then
   eval $(parse_yaml $YAMLFILE "POST_")
else
  echo "ERROR: YAML FILE $YAMLFILE DOES NOT EXIST, ABORT!"
  exit 1
fi

# source modulefile
source $POST_env_modulefile

# create working directory
rm -rf $POST_paths_postworkdir
mkdir -p $POST_paths_postworkdir
cd $POST_paths_postworkdir

# create output directory
mkdir -p $POST_paths_postoutdir

# generate YAML for post processing scripts
adate=$POST_time_year$POST_time_month$POST_time_day$POST_time_cycle
fixgsi=$POST_paths_gsidir/fix
# conventional
convinfo=$fixgsi/global_convinfo.txt
convyaml=$POST_paths_postworkdir/convyaml.yaml
$USHDIR/convinfo2yaml.py -d $POST_paths_gsidiagdir -c $adate -i $convinfo -y $convyaml || exit 1
# radiance
satinfo=$fixgsi/global_satinfo.txt
satyaml=$POST_paths_postworkdir/satyaml.yaml
$USHDIR/satinfo2yaml.py -d $POST_paths_gsidiagdir -c $adate -i $satinfo -y $satyaml || exit 1

# run the multiprocessing scripts
python $PyGSIDir/mp_plot_satDiags.py -n 20 -y $satyaml -o $POST_paths_postoutdir || exit 1

python $PyGSIDir/mp_plot_convDiags.py -n 20 -y $convyaml -o $POST_paths_postoutdir || exit 1


if [[ "$POST_cleanup" = "true" ]]; then
  cd $POST_paths_postoutdir
  rm -rf $POST_paths_postworkdir
fi

date
echo "DARTH post script completed"
