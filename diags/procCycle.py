from solo.date import Hour, DateIncrement
from solo.logger import Logger
from solo.configuration import Configuration
from solo.basic_files import mkdir
from r2d2 import fetch, date_sequence
import glob
import os
#import DARTHsite
from multiprocessing import Pool
import ioda
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

logger = Logger('procCycle')
config = Configuration('procCycle.yaml')
nprocs = 40

def procIodaDiag(config, diagpath):
    # read, plot, save output from IODA diag file
    # open IODA file and obs group
    diag = ioda.Engines.HH.openFile(
        name = diagpath,
        mode = ioda.Engines.BackendOpenModes.Read_Only)
    dlp = ioda._ioda_python.DLP.DataLayoutPolicy.generate(
        ioda._ioda_python.DLP.DataLayoutPolicy.Policies(0))
    og = ioda.ObsGroup(diag, dlp)
    # get list of variables in file
    varlist = og.vars.list()
    obsvarlist = []
    for v in varlist:
        vsplit = v.split('@') # will probably need to change this later
        try:
            if vsplit[1] == 'hofx':
                obsvarlist.append(vsplit[0])
        except IndexError:
            pass
    # for each variable type, now create figures and make stats
    # TODO fix this when brightness temp is 2D
    for v in obsvarlist:
        # get hofx from ufo and jedi
        #iodavar = og.vars.open(f'{v}@hofx')
        #hofxUFO = iodavar.readNPArray.float()
        #iodavar = og.vars.open(f'{v}@GsiHofX')
        #hofxGSI = iodavar.readNPArray.float()
        # get qc values
        iodavar = og.vars.open(f'{v}@EffectiveQC')
        qcUFO = iodavar.readNPArray.int()
        iodavar = og.vars.open(f'{v}@PreQC')
        qcGSI = iodavar.readNPArray.int()
        # get errors
        iodavar = og.vars.open(f'{v}@EffectiveError')
        errUFO = iodavar.readNPArray.float()
        errUFO[errUFO > 9e36] = np.nan
        iodavar = og.vars.open(f'{v}@GsiFinalObsError')
        errGSI = iodavar.readNPArray.float()
        errGSI[errGSI > 9e36] = np.nan


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
    # TODO set up a multiprocessing pool to process each diag file in parallel
    mkdir(os.path.join(config.stage, Hour(config.cycle).format('%Y%m%d%H'),
                       'DARTH', 'html', 'figs'))
    mkdir(os.path.join(config.stage, Hour(config.cycle).format('%Y%m%d%H'),
                       'DARTH', 'html', 'stats'))
    for diag in diagFiles:
        print(diag)
        procIodaDiag(config, diag)


if __name__ == "__main__":
    procCycle(config)
