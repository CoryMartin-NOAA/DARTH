#!/usr/local/env python
# gen_cycle_yaml.py
# generate top level YAML
# from rocoto (or other workflow driver)
# to be used by setup_proc_cycle.py
# cory.r.martin@noaa.gov

import argparse
import yaml
import datetime
import re
import os

def main(yamlconfig, adate, outfile):
    # need to create a YAML file to be read by
    # setup_proc_cycle.py
    # figure out some variables
    comrot = yamlconfig['DARTH']['comrot']+'/'+adate.strftime('%Y%m%d%H')
    if os.getenv('SLURM_SET','NO') == 'YES':
       launcher = 'srun --export=ALL'
    else:
       launcher = 'mpirun -np ' #TODO finish this for non-slurm
    threads = 1
    yamlout = {}
    # things for this cycle specifically
    timestr = adate.strftime('%Y-%m-%dT%H:00:00Z')
    yamlout['analysis cycle'] = {
                                'time': timestr,
                                'dump': yamlconfig['DARTH']['dump'],
                                'restricted data': yamlconfig['DARTH']['rstprod'],
    }
    # YAML for the GSI observer step
    bkgres = re.sub('[^0-9]','', yamlconfig['background']['res'])
    gsibkg = {
             'jcap': int(bkgres) - 2,
             'jcap_b': (2*int(bkgres)) - 2,
             'levs': yamlconfig['background']['levs'],
             'guessdir': yamlconfig['paths']['guessdir'],
             'format': yamlconfig['background']['format'],
             'gfsv16': yamlconfig['background']['gfsv16'],
    }
    gsienv = {
             'launcher': launcher,
             'nthreads': threads,
    }
    yamlout['gsi observer'] = {
                              'background': gsibkg,
                              'observations': {'bufrdir': yamlconfig['paths']['obsdir']},
                              'gsidir': yamlconfig['paths']['gsiroot'],
                              'gsiwork': comrot+'/GSI_work/',
                              'gsiout': comrot+'/GSI_out/',
                              'env': gsienv,
    }
    # YAML for the JEDI H(x) step
    jedibkg = {
               'res': yamlconfig['background']['res'],
               'levs': yamlconfig['background']['levs'],
               'guessdir': yamlconfig['paths']['guessdir'],
               'gfsv16': yamlconfig['background']['gfsv16'],
    }
    jedienv = {
             'launcher': launcher,
             'nthreads': threads,
             'modulefile': yamlconfig['paths']['jedimodule'],
    }
    yamlout['jedi hofx'] = {
        'background': jedibkg,
        'observations': {'iodadir': comrot+'/IODA/'},
        'env': jedienv,
        'hofxwork': comrot+'/JEDI_work/',
        'hofxout': comrot+'/JEDI_hofx/',
        'executable': yamlconfig['paths']['jedibin'] + '/fv3jedi_hofx_nomodel.x',
        'fixfv3jedi': yamlconfig['paths']['jediroot'] + '/fv3-jedi/test/Data',
    }
    # YAML for the conversion step
    iodaenv = {
             'launcher': launcher,
             'nthreads': threads,
             'modulefile': yamlconfig['paths']['jedimodule'],
    }
    yamlout['ioda-converters'] = {
            'iodaconvbin': yamlconfig['paths']['iodaconvbin'] + '/proc_gsi_ncdiag.py',
            'iodaconvwork': comrot+'/IODA_work/',
            'gsidiagdir': comrot+'/GSI_out/',
            'iodaout': comrot+'/IODA/',
            'env': iodaenv,
    }
    # YAML for the post processing job
    postenv = {'modulefile': yamlconfig['paths']['pygsimodule']}
    yamlout['post'] = {
        'env': postenv,
        'postwork': comrot+'/POST_work/',
        'postout': comrot+'/verification/',
        'gsidiagdir': comrot+'/GSI_out/',
        'hofxoutdir': comrot+'/JEDI_hofx/',
        'gsidir': yamlconfig['paths']['gsiroot'],
    }
    # other misc things
    yamlout['cleanup'] = yamlconfig['DARTH']['cleanup']
    yamlout['yamldir'] = comrot + '/YAML/'

    # write out the YAML file
    with open(outfile, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    print('YAML written to: '+outfile)


parser = argparse.ArgumentParser(description='Generate YAML for this global cycle which is then'+\
                                ' used by setup_proc_cycle to generate more YAML')
parser.add_argument('-y', '--yaml', type=str,
                    help='path to input YAML file for this analysis cycle', required=True)
parser.add_argument('-d', '--date', type=str,
                    help='YYYYMMDDHH for this analysis cycle', required=True)
parser.add_argument('-o', '--yamlout', type=str,
                    help='path for output YAML file for this analysis cycle', required=True)
args = parser.parse_args()
YAML = args.yaml
outfile = args.yamlout
adate = datetime.datetime.strptime(args.date, "%Y%m%d%H")
with open(YAML, 'r') as stream:
    yamlconfig = yaml.safe_load(stream)

main(yamlconfig, adate, outfile)
