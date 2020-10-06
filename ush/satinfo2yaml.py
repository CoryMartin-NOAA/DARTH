#!/usr/bin/env python
# satinfo2yaml.py
# generate YAML from input satinfo file
# for specified input GSI diag file(s)
import argparse
import yaml
import glob
import csv

def main(config):
    # read in satinfo file
    sensor = [] # string used in the filename
    channel = [] # integer value of channel
    obuse = [] # use 1, monitor -1
    cv = open(config['satinfo'])
    rdcv = csv.reader(filter(lambda row: row[0]!='!', cv))
    for row in rdcv:
        try:
            rowsplit = row[0].split()
            sensor.append(rowsplit[0])
            channel.append(rowsplit[1])
            obuse.append(rowsplit[2])
        except IndexError:
            pass # end of file
    cv.close()

    # get list of diagnostic files available
    diagpath = config['diagdir'] + '/diag_*_' + config['loop'] + '.' + config['cycle'] + '.nc4'
    diagfiles = glob.glob(diagpath)

    # initialize YAML dictionary for output
    yamlout = { 'diagnostic': [] }
    if config['loop'] == 'ges':
        diagtype = 'O-F'
    else:
        diagtype = 'O-A'
    figs = ['histogram', 'spatial']

    # loop through obtypes
    print(diagfiles)
    for i in range(len(sensor)):
        # first get filename and verify it exists
        diagfile = config['diagdir'].rstrip('/') + '/diag_' + sensor[i] + '_' + config['loop'] + '.' + config['cycle'] + '.nc4'
        if diagfile not in diagfiles:
            continue # skip if diag file is missing
        if int(obuse[i]) != 1:
            continue # only process assimilated obs for now
        dictloop = {
                   'path': [diagfile],
                   'channel': [int(channel[i])],
                   'qc flag': [0],
                   'data type': [diagtype],
                   'plot type': [figs],
                   }
        yamlout['diagnostic'].append({'radiance input': dictloop})

    # write out the YAML
    with open(config['yaml'], 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    print('YAML written to '+config['yaml'])

parser = argparse.ArgumentParser(description='Given an input satinfo GSI file and path to GSI diags,'+\
                                ' generate an output YAML file for use by PyGSI')
parser.add_argument('-d','--diagdir', type=str, help='path to GSI netCDF diags', required=True)
parser.add_argument('-c','--cycle', type=str, help='cycle YYYYMMDDHH', required=True)
parser.add_argument('-i','--satinfo', type=str, help='path to GSI satinfo file', required=True)
parser.add_argument('-y','--yaml', type=str, help='path to output YAML file', required=True)
parser.add_argument('-l','--loop', type=str, help='ges|anl default ges', default='ges')
args = parser.parse_args()

config = {}
config['diagdir'] = args.diagdir
config['cycle'] = args.cycle
config['satinfo'] = args.satinfo
config['yaml'] = args.yaml
config['loop'] = args.loop

main(config)

