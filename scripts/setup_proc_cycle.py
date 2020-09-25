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


def main(yamlconfig):
    mydir = os.path.dirname(os.path.realpath(__file__))
    rootdir = '/'.join(mydir.split('/')[:-1])
    # run GSI observer if in YAML
    validtime = yamlconfig['analysis cycle']['time']
    if 'gsi observer' in yamlconfig:
        gsiconfig = yamlconfig['gsi observer']
        gsiobsyaml = gsiconfig['gsiwork']+'/%s_gsi_observer.yaml' % (validtime.strftime('%Y%m%d%H'))
        # create YAML for GSI observer script
        # create batch submission script
        if 'slurm' in gsiconfig: # only support slurm currently
            slurmdict = gsiconfig['slurm']
            slurmdict['job'] = 'run_gsi_observer'
            slurmdict['jobyaml'] = gsiobsyaml
            slurmdict['jobscript'] = rootdir + '/scripts/%s.sh' % (slurmdict['job'])
            slurmdict['validtime'] = validtime
            gsibatch = gen_slurm_submit(slurmdict)
            print('GSI observer sbatch submission file written to :'+gsibatch)
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
