#!/usr/bin/env python
# gen_yaml_fv3jedi_hofx_nomodel.py
# generate YAML for fv3jedi_hofx_nomodel application
# based off of higher level YAML config file as input
import argparse
import yaml
import datetime
import re

def main(configyamlfile):
    # read in the input YAML
    with open(configyamlfile, 'r') as stream:
        yamlconfig = yaml.safe_load(stream)
    # extract info from YAML
    validtimestr = yamlconfig['time']['year'] + yamlconfig['time']['month'] + \
                   yamlconfig['time']['day'] + yamlconfig['time']['cycle']
    validtime = datetime.datetime.strptime(validtimestr, "%Y%m%d%H")
    cyclelen = 6 # hard coded this for now, fix later in YAML
    begintime = validtime - datetime.timedelta(hours=cyclelen/2)
    npz = yamlconfig['background']['levs']
    res = yamlconfig['background']['res']
    res = re.sub('[^0-9]','', res) # remove C if it exists, like C768 to 768
    ntiles = 6 # hard coded for global for now
    npx = res + 1
    # set up the output YAML dictionary
    yamlout = {}
    yamlout['window begin'] = begintime.strftime('%Y-%m-%dT%H:%M:%SZ')
    yamlout['window length'] = 'PT%sH' % (cyclelen)
    yamlout['forecast length'] = 'PT%sH' % (cyclelen)
    yamlout['geometry'] = {}
    yamlout['forecasts'] = {}
    yamlout['observations'] = {}
    # write out the new YAML
    yamloutfile = yamlconfig['hofx']['yamlfile']
    with open(yamloutfile, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    print('YAML written to '+yamloutfile)

parser = argparse.ArgumentParser(description='Generate YAML for fv3jedi_hofx_nomodel application'+\
                                ' given an input YAML configuration file')
parser.add_argument('-c','--configyaml', type=str, help='path of high level YAML configuration file', required=True)
args = parser.parse_args()

main(args.configyaml)
