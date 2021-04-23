from solo.date import Hour, DateIncrement
from solo.logger import Logger
from solo.configuration import Configuration
from solo.basic_files import mkdir
from r2d2 import fetch, date_sequence
import glob
import os
import DARTHsite
from multiprocessing import Pool
import ioda
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, ticker, cm
from matplotlib.colors import Normalize
from scipy.interpolate import interpn
from sklearn.linear_model import LinearRegression

logger = Logger('procCycle')
config = Configuration('procCycle.yaml')
nprocs = 40
ozdiag = ['omps_npp']  # fill out later

#set figure params one time only.
rcParams['figure.subplot.left'] = 0.1
rcParams['figure.subplot.top'] = 0.85
rcParams['legend.fontsize'] = 12
rcParams['axes.grid'] = True

def procIodaDiag(config, diagpath):
    # read, plot, save output from IODA diag file
    # open IODA file and obs group
    diag = ioda.Engines.HH.openFile(
        name = diagpath,
        mode = ioda.Engines.BackendOpenModes.Read_Only)
    dlp = ioda._ioda_python.DLP.DataLayoutPolicy.generate(
        ioda._ioda_python.DLP.DataLayoutPolicy.Policies(0))
    og = ioda.ObsGroup(diag, dlp)
    # get name of platform, etc.
    diagpathbase = os.path.basename(diagpath).split('_')
    obstype = '_'.join(diagpathbase[0:diagpathbase.index('hofx')])
    if len(obstype.split('_')) > 1:
        # either radiance or ozone
        diagtype ='oz' if obstype in ozdiag else 'conv'
    else:
        diagtype = 'conv'
    # get list of variables in file
    varlist = og.vars.list()
    obsvarlist = []
    for v in varlist:
        vsplit = v.split('@')  # will probably need to change this later
        try:
            if vsplit[1] == 'hofx':
                obsvarlist.append(vsplit[0])
        except IndexError:
            pass
    # for each variable type, now create figures and make stats
    # TODO fix this when brightness temp is 2D
    for v in obsvarlist:
        getvars = [
            f'{v}@hofx',
            f'{v}@GsiHofXBc',
            f'{v}@EffectiveQC',
            f'{v}@PreQC',
            f'{v}@EffectiveError',
            f'{v}@GsiFinalObsError',
        ]
        nlocs = np.arange(1, len(get_ioda_var(og, f'{v}@hofx'))+1)
        dfDiag = pd.DataFrame(nlocs, columns=['nlocs'])
        for gv in getvars:
            dfDiag[gv] = get_ioda_var(og, gv)
        # create scatter plot of H(x)
        qc = dfDiag[dfDiag[f'{v}@GsiFinalObsError'].notnull()]
        tmp = qc[[f'{v}@hofx', f'{v}@GsiHofXBc']].dropna()
        outfig = os.path.join(config.stage,
                              'DARTH', 'html', 'figs',
                              Hour(config.cycle).format('%Y%m%d%H'),
                              f'{obstype}_hofx_{v}_scatter.png',
                              )
        scatter_mdata = {
            'title': f'{obstype} {v} H(x) Comparison',
            'cycle': f'{config.cycle}',
            'xlabel': 'GSI H(x)',
            'ylabel': 'UFO H(x)',
            'outfig': outfig,
            }
        gen_scatter(tmp[f'{v}@GsiHofXBc'], tmp[f'{v}@hofx'], scatter_mdata)

def get_ioda_var(og, vname):
    # get IODA var and return as numpy array
    iodaVar = og.vars.open(vname)
    if iodaVar.isA2(ioda._ioda_python.Types.float):
        fillVal = iodaVar.atts.open('_FillValue').readDatum.float()
        vdata = iodaVar.readNPArray.float()
        vdata[vdata == fillVal] = np.nan
    elif iodaVar.isA2(ioda._ioda_python.Types.int):
        vdata = iodaVar.readNPArray.int()
    else:
        raise TypeError("Only float and int supported for now")
    return vdata

def fetchDiags(config):
    # fetch diags from R2D2 to a working directory
    window_start = Hour(config.cycle) - DateIncrement('PT3H')
    ymdh = Hour(config.cycle).format('%Y%m%d%H')
    stagedir = f'{config.stage}/diags/{ymdh}/'
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

def _get_linear_regression(data1, data2):
    """
    Inputs:
        data1 : data on the x axis
        data2 : data on the y axis
    """
    x = np.array(data1).reshape((-1,1))
    y = np.array(data2)
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x,y)
    intercept = model.intercept_
    slope = model.coef_[0]
    # This is the same as if you calculated y_pred
    # by y_pred = slope * x + intercept
    y_pred = model.predict(x)
    return y_pred, r_sq, intercept, slope

def gen_scatter(dfX, dfY, metadata):
    # generate and save scatter plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    y_pred, r_sq, intercept, slope = _get_linear_regression(dfX, dfY)
    #plt.scatter(x=dfX, y =dfY, s=4, color='darkgray', label=f'n={dfX.count()}')
    density_scatter(dfX.values, dfY.values, ax=ax, fig=fig, bins = [100,100], s=4, cmap='hot')
    label = f'y = {slope:.4f}x + {intercept:.4f}\nR\u00b2 : {r_sq:.4f}'
    plt.plot(dfX, y_pred, color='black', linewidth=1, label=label)
    plt.legend(loc='upper left', fontsize=11)
    plt.title(metadata['title'], loc='left')
    plt.xlabel(metadata['xlabel'], fontsize=12)
    plt.ylabel(metadata['ylabel'], fontsize=12)
    plt.title(metadata['cycle'], loc='right', fontweight='semibold')
    plt.savefig(metadata['outfig'], bbox_inches='tight', pad_inches=0.1)
    plt.close('all')

def density_scatter( x , y, ax=None, fig=None, sort = True, bins = 20, **kwargs )   :
    """
    Scatter plot colored by 2d histogram
    """
    if ax is None :
        fig , ax = plt.subplots()
    data , x_e, y_e = np.histogram2d( x, y, bins = bins, density = True )
    z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T , method = "splinef2d", bounds_error = False)
    #To be sure to plot all data
    z[np.where(np.isnan(z))] = 0.0
    # Sort the points by density, so that the densest points are plotted last
    if sort :
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]
    ax.scatter( x, y, c=z, **kwargs )
    norm = Normalize(vmin = np.min(z), vmax = np.max(z))
    #cbar = fig.colorbar(cm.ScalarMappable(norm = norm), ax=ax)
    #cbar.ax.set_ylabel('Density')
    return ax

def procCycle(config):
    # process cycle of IODA diagnostic files
    # use R2D2 to stage diag files
    fetchDiags(config)
    # get list of diag files to process
    diagFiles = glob.glob(os.path.join(config.stage, 'diags',
                                       Hour(config.cycle).format('%Y%m%d%H'),
                                       '*_hofx_*'))
    # TODO set up a multiprocessing pool to process each diag file in parallel
    mkdir(os.path.join(config.stage, 'DARTH', 'html', 'figs',
                       Hour(config.cycle).format('%Y%m%d%H')))
    mkdir(os.path.join(config.stage, 'DARTH', 'html', 'stats',
                       Hour(config.cycle).format('%Y%m%d%H')))
    for diag in diagFiles:
        procIodaDiag(config, diag)


if __name__ == "__main__":
    procCycle(config)
