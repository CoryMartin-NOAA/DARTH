#!/usr/bin/env python
# gen_yaml_fv3jedi_hofx_nomodel.py
# generate YAML for fv3jedi_hofx_nomodel application
# based off of higher level YAML config file as input
import argparse
import yaml
import datetime
import re
import os
import glob

def gen_obslist(configdict):
    # determine which observations are available to run H(x) for
    obslist = []
    allobs = glob.glob(configdict['iodaobsdir']+'/*')
    for ob in allobs:
        if os.path.getsize(ob) > 1000: # get rid of 'empty' files
            basename = os.path.basename(ob)
            obpath = 'Data/obs/'+basename
            hofxpath = obpath.replace('obs','hofx')
            obtype = '_'.join(basename.split('_')[0:2])
            # get yaml from template
            obyamlfile = f"{configdict['ufoyamldir']}/{obtype}.yaml"
            with open(obyamlfile, 'r') as stream:
                obsetup = yaml.safe_load(stream)
            obsetup['obs space']['obsdatain']['obsfile'] = obpath
            obsetup['obs space']['obsdataout']['obsfile'] = hofxpath
            obslist.append(obsetup)

    return obslist

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
    npx = int(res) + 1
    npy = npx # only true for global
    layout = [1,1] # fixed for now, change later
    rsttimes = validtime.strftime('%Y%m%d.%H%M%S') # make this a list later and loop for FGAT
    # figure out which obs to process
    yamlconfig['ufoyamldir'] = os.getenv('HOMEDARTH','./') + '/parm/ufo/'
    yamlconfig['iodaobsdir'] = yamlconfig['observations']['iodadir']+'/'+validtimestr
    obslist = gen_obslist(yamlconfig)
    # set up the output YAML dictionary
    yamlout = {}
    yamlout['window begin'] = begintime.strftime('%Y-%m-%dT%H:%M:%SZ')
    yamlout['window length'] = 'PT%sH' % (cyclelen)
    yamlout['forecast length'] = 'PT%sH' % (cyclelen)
    yamlout['geometry'] = {
                           'nml_file_mpp': 'Data/fv3files/fmsmpp.nml',
                           'trc_file': 'Data/fv3files/field_table',
                           'akbk': f'Data/fv3files/akbk{npz}.nc4',
                           'layout': layout,
                           'io_layout': [1,1],
                           'npx': npx,
                           'npy': npy,
                           'npz': npz,
                           'ntiles': ntiles,
                           'fieldsets': [{'fieldset': 'Data/fieldsets/dynamics.yaml'},
                                        {'fieldset': 'Data/fieldsets/ufo.yaml'}],
                          }
    yamlout['forecasts'] = {
                           'datapath': 'Data/bkg/',
                           'filetype: gfs',
                           'filename_core': rsttimes+'.fv_core.res.nc',
                           'filename_trcr': rsttimes+'.fv_tracer.res.nc',
                           'filename_sfcd': rsttimes+'.sfc_data.nc',
                           'filename_sfcw': rsttimes+'.fv_srf_wnd.res.nc',
                           'filename_cplr': rsttimes+'.coupler.res',
                           'state variables': ['u','v','ua','va','T','DELP',
                                              'sphum','ice_wat','liq_wat','o3mr',
                                              'phis','slmsk','sheleg','tsea',
                                              'vtype','stype','vfrac','stc','smc',
                                              'snwdph','u_srf','v_srf','f10m','sss'],
                           }
    yamlout['observations'] = obslist
    yamlout['prints'] = {'frequency': 'PT3H'}
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
