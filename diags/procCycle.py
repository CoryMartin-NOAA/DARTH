from solo.date import Hour, DateIncrement
from solo.logger import Logger
from solo.configuration import Configuration
from solo.basic_files import mkdir
from r2d2 import fetch, date_sequence
import glob
import os
import DARTHsite

logger = Logger('procCycle')
config = Configuration('procCycle.yaml')

def fetchDiags(config):
    # fetch diags from R2D2 to a working directory
    window_start = Hour(config.cycle) - DateIncrement('PT3H')
    ymdh = Hour(config.cycle).format('%Y%m%d%H')
    stagedir = f'{config.stage}/{ymdh}/diags'
    mkdir(stagedir)
    fetch(
        type='diag',
        model=config.model,
        experiment=config.experiment,
        date=window_start,
        obs_type=config.obs_types,
        database=config.database,
        target_file=f'{stagedir}/$(obs_type)_hofx_{config.model}_$(date).nc4',
        )


def procCycle(config):
    # process cycle of IODA diagnostic files
    # use R2D2 to stage diag files
    fetchDiags(config)
    # get list of diag files to process
    diagFiles = glob.glob(os.path.join(config.stage,
                                       Hour(config.cycle).format('%Y%m%d%H'),
                                       'diags', '*_hofx_*'))



if __name__ == "__main__":
    procCycle(config)

