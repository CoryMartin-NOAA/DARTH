#!/bin/bash
set -eux
set +x
source /work/noaa/da/Cory.R.Martin/noscrub/UFO_eval/env/ioda_diags.env.bash
set -x

ulimit -s unlimited

gitdir=$PWD/..
hofxexe=/work/noaa/da/Cory.R.Martin/noscrub/JEDI/stable/fv3-bundle/build/bin/fv3jedi_hofx_nomodel.x

cd $gitdir/hofx

python stage_bkg.py ./expdir
python stage_obs.py ./expdir
python stage_fv3jedi.py ./expdir
python genyaml.py hofx ./expdir /work/noaa/stmp/$USER/hofxyaml_testcycle.yaml
srun -n6 $hofxexe /work/noaa/stmp/$USER/hofxyaml_testcycle.yaml
python archive_hofx.py ./expdir
