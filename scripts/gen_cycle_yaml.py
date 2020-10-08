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

def main(yamlconfig, adate, outfile):
    # need to create a YAML file to be read by
    comrot = yamlconfig['DARTH']['comrot']+'/'+adate.strftime('%Y%m%d%H')
    # setup_proc_cycle.py
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
    yamlout['gsi observer'] = {
                              'background': gsibkg,
                              'observations': {'bufrdir': yamlconfig['paths']['obsdir']},
                              'gsidir': yamlconfig['paths']['gsiroot'],
                              'gsiwork': comrot+'/GSI_work/',
                              'gsiout': comrot+'/GSI_out/',
    }
    # YAML for the JEDI H(x) step
    yamlout['jedi hofx'] = {
    }
    # YAML for the conversion step
    yamlout['ioda-converters'] = {
    }
    # other misc things
    yamlout['cleanup'] = yamlconfig['DARTH']['cleanup']


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
