#!/usr/bin/env python
# setup_proc_cycle.py
# generate YAML, other scripts, etc. needed
# to process a global analysis cycle and produce output
# cory.r.martin@noaa.gov

import argparse
import yaml
import datetime
import os

def gen_slurm_submit(slurmdict):
    """
    generate a slurm submission script from an input dictionary
    """
    timestr = slurmdict['validtime'].strftime('%Y%m%d%H')
    batchfile = '%s/sbatch_%s_%s.sh' % (slurmdict['submitdir'], slurmdict['job'], timestr)
    sbatch = {
              '-J': slurmdict['job'],
              '-A': slurmdict['account'],
              '-q': slurmdict['queue'],
              '--nodes': slurmdict['nodes'],
              '--ntasks-per-node': slurmdict['taskspernode'],
              '-t': slurmdict['maxtime'],
    }
    with open (batchfile, 'w') as rsh:
        rsh.write('#!/bin/bash\n')
        for key, value in sbatch.items():
            rsh.write('#SBATCH '+key+' '+str(value)+'\n')
        rsh.write('\n')
        rsh.write(slurmdict['jobscript']+' '+slurmdict['jobyaml'])
        rsh.write('\n')
    return batchfile

def gen_gsi_observer_yaml(gsiconfig):
    """
    generate YAML for use by run_gsi_observer.sh
    """
    timestr = gsiconfig['validtime'].strftime('%Y%m%d%H')
    yamlpath = gsiconfig['gsiwork'] + '/run_gsi_observer_%s.yaml' % (timestr)
    # set up an output dictionary, then use pyYAML to write it out
    yamlout = {}
    yamlout['time'] = {
                       'year': gsiconfig['validtime'].strftime('%Y'),
                       'month': gsiconfig['validtime'].strftime('%m'),
                       'day': gsiconfig['validtime'].strftime('%d'),
                       'cycle': gsiconfig['validtime'].strftime('%H'),
    }
    yamlout['background'] = gsiconfig['background']
    yamlout['observations'] = {
                               'obsdir': gsiconfig['observations']['bufrdir'],
                               'dump': gsiconfig['dump'],
                               'restricted': gsiconfig['rstprod'],
    }
    yamlout['observer'] = {
                           'workdir': '%s/%s' % (gsiconfig['gsiwork'],timestr),
                           'gsidir': gsiconfig['gsidir'],
                           'outputdir': '%s/%s' % (gsiconfig['gsiout'],timestr),
                           'cleanup': gsiconfig['cleanup'],
    }
    yamlout['env'] = gsiconfig['env']
    with open(yamlpath, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    return yamlpath

def main(yamlconfig):
    mydir = os.path.dirname(os.path.realpath(__file__))
    rootdir = '/'.join(mydir.split('/')[:-1])
    # run GSI observer if in YAML
    validtime = yamlconfig['analysis cycle']['time']
    if 'gsi observer' in yamlconfig:
        gsiconfig = yamlconfig['gsi observer']
        gsiconfig['validtime'] = validtime
        gsiconfig['dump'] = yamlconfig['analysis cycle']['dump']
        gsiconfig['rstprod'] = yamlconfig['analysis cycle']['restricted data']
        gsiconfig['cleanup'] = yamlconfig['cleanup']
        # create YAML for GSI observer script
        gsiobsyaml = gen_gsi_observer_yaml(gsiconfig)
        print('GSI observer configuration YAML file written to: '+gsiobsyaml)
        # create batch submission script
        if 'slurm' in gsiconfig: # only support slurm currently
            slurmdict = gsiconfig['slurm']
            slurmdict['job'] = 'run_gsi_observer'
            slurmdict['jobyaml'] = gsiobsyaml
            slurmdict['jobscript'] = rootdir + '/scripts/%s.sh' % (slurmdict['job'])
            slurmdict['validtime'] = validtime
            gsibatch = gen_slurm_submit(slurmdict)
            print('GSI observer sbatch submission file written to: '+gsibatch)
        # TODO add other batch systems (lsf for wcoss)
    # TODO add JEDI things
    # TODO add plotting / analysis things

parser = argparse.ArgumentParser(description='Generate YAML, other scripts, etc.'+\
                                ' to process a global analysis cycle and produce output')
parser.add_argument('-y', '--yaml', type=str,
                    help='path to YAML file for this analysis cycle', required=True)
args = parser.parse_args()
YAML = args.yaml
with open(YAML, 'r') as stream:
    yamlconfig = yaml.safe_load(stream)

main(yamlconfig)
