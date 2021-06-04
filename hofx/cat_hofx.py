from solo.logger import Logger
from genyaml import gen_yaml as get_config
import click
from solo.netcdf import NetCDF
from netCDF4 import Dataset
import glob
import os
import shutil

logger = Logger('catHofx')
@click.command()
@click.argument('expdir', required=True)

def cat_HofX(expdir):
    # concatenate H(x) output files and store them in
    # a specified R2D2 database
    # get config
    config = get_config('archHofX', expdir, quiet=True)
    logger.info(f"Preparing to concatenate H(x) output files")
    for ob in config['observations']:
        obname = ob['obs space']['name'].lower()
        logger.info(f"Processing {obname}...")
        # output is current_dir in JEDI-GDAS, not an ideal name, but using it for compatibility
        hofxdir = config['obs_dir']
        netcdf_files = []
        filenames = sorted(glob.glob(os.path.join(hofxdir,f"*{obname}*_????.nc4")))
        netcdf_files = []
        for filename in filenames:
            if os.stat(filename).st_size > 0:
                data = Dataset(filename)
                if len(data.dimensions['nlocs']) > 0:
                    netcdf_files.append(filename)
            # Concatenate each obs file into one file, based on current obs window
        if (len(netcdf_files)) > 0:
            output = filenames[0].replace('_0000','')
            nc = NetCDF(obname)
            nc.concat_files(netcdf_files, output, compression=True)
        else:
            logger.info(f"No H(x) output for {obname}. Skipping.")
            continue

if __name__ == '__main__':
    cat_HofX()
