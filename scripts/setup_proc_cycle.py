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
    # TODO check if output directory exists, make it if not
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
    yamlpath = gsiconfig['yamldir'] + '/run_gsi_observer_%s.yaml' % (timestr)
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
                           'workdir': '%s' % (gsiconfig['gsiwork']),
                           'gsidir': gsiconfig['gsidir'],
                           'outputdir': '%s' % (gsiconfig['gsiout']),
                           'cleanup': gsiconfig['cleanup'],
    }
    yamlout['env'] = gsiconfig['env']
    # TODO check if output directory exists, make it if not
    with open(yamlpath, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    return yamlpath

def gen_fv3jedi_hofx_yaml(jediconfig):
    """
    generate YAML for use by run_fv3jedi_hofx_nomodel.sh
    """
    timestr = jediconfig['validtime'].strftime('%Y%m%d%H')
    yamlpath = jediconfig['yamldir'] + '/run_fv3jedi_hofx_%s.yaml' % (timestr)
    # set up an output dictionary, then use pyYAML to write it out
    yamlout = {}
    yamlout['time'] = {
                       'year': jediconfig['validtime'].strftime('%Y'),
                       'month': jediconfig['validtime'].strftime('%m'),
                       'day': jediconfig['validtime'].strftime('%d'),
                       'cycle': jediconfig['validtime'].strftime('%H'),
    }
    yamlout['background'] = jediconfig['background']
    yamlout['observations'] = {
                               'iodadir': jediconfig['observations']['iodadir'],
                               'dump': jediconfig['dump'],
                               'restricted': jediconfig['rstprod'],
    }
    yamlout['hofx'] = {
                           'workdir': '%s' % (jediconfig['hofxwork']),
                           'outputdir': '%s' % (jediconfig['hofxout']),
                           'cleanup': jediconfig['cleanup'],
                           'executable': jediconfig['executable'],
                           'yamlfile': jediconfig['hofxwork'] + '/fv3jedi_hofx_nomodel_%s.yaml' % (timestr),
    }
    yamlout['fix'] = { 'fixfv3jedi' : jediconfig['fixfv3jedi']}
    yamlout['env'] = jediconfig['env']
    # TODO check if output directory exists, make it if not
    with open(yamlpath, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    return yamlpath

def gen_post_yaml(postconfig):
    timestr = postconfig['validtime'].strftime('%Y%m%d%H')
    yamlpath = postconfig['yamldir'] + '/run_post_%s.yaml' % (timestr)
    # set up an output dictionary, then use pyYAML to write it out
    yamlout = {}
    yamlout['time'] = {
                       'year': postconfig['validtime'].strftime('%Y'),
                       'month': postconfig['validtime'].strftime('%m'),
                       'day': postconfig['validtime'].strftime('%d'),
                       'cycle': postconfig['validtime'].strftime('%H'),
    }
    yamlout['paths'] = {
                       'gsidiagdir': '%s' % (postconfig['gsidiagdir']),
                       'gsidir': '%s' % (postconfig['gsidir']),
                       'ufohofxdir': '%s' % (postconfig['hofxoutdir']),
                       'postworkdir': '%s' % (postconfig['postwork']),
                       'postoutdir': '%s' % (postconfig['postout']),
    }
    yamlout['env'] = postconfig['env']
    yamlout['cleanup'] = postconfig['cleanup']
    # TODO check if output directory exists, make it if not
    with open(yamlpath, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    return yamlpath

def gen_gsinc_iodaconv_yaml(iodaconvconfig):
    timestr = iodaconvconfig['validtime'].strftime('%Y%m%d%H')
    yamlpath = iodaconvconfig['yamldir'] + '/run_gsinc_iodaconv_%s.yaml' % (timestr)
    # set up an output dictionary, then use pyYAML to write it out
    yamlout = {}
    yamlout['time'] = {
                       'year': iodaconvconfig['validtime'].strftime('%Y'),
                       'month': iodaconvconfig['validtime'].strftime('%m'),
                       'day': iodaconvconfig['validtime'].strftime('%d'),
                       'cycle': iodaconvconfig['validtime'].strftime('%H'),
    }
    yamlout['data'] = {
                       'gsiindir': '%s' % (iodaconvconfig['gsidiagdir']),
                       'iodaoutdir': '%s' % (iodaconvconfig['iodaout']),
                       'iodaworkdir': '%s' % (iodaconvconfig['iodaconvwork']),
    }
    yamlout['iodaconv'] = {
                       'iodaconvbin': iodaconvconfig['iodaconvbin'],
    }
    yamlout['env'] = iodaconvconfig['env']
    # TODO check if output directory exists, make it if not
    with open(yamlpath, 'w') as file:
        yaml.dump(yamlout, file, default_flow_style=False)
    return yamlpath

def main(yamlconfig):
    mydir = os.path.dirname(os.path.realpath(__file__))
    rootdir = '/'.join(mydir.split('/')[:-1])
    # run GSI observer if in YAML
    validtime = yamlconfig['analysis cycle']['time']
    validtime = datetime.datetime.strptime(validtime, '%Y-%m-%dT%H:00:00Z')
    if 'gsi observer' in yamlconfig:
        gsiconfig = yamlconfig['gsi observer']
        gsiconfig['validtime'] = validtime
        gsiconfig['dump'] = yamlconfig['analysis cycle']['dump']
        gsiconfig['rstprod'] = yamlconfig['analysis cycle']['restricted data']
        gsiconfig['cleanup'] = yamlconfig['cleanup']
        gsiconfig['yamldir'] = yamlconfig['yamldir']
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
    if 'ioda-converters' in yamlconfig:
        iodaconvconfig = yamlconfig['ioda-converters']
        iodaconvconfig['validtime'] = validtime
        iodaconvconfig['cleanup'] = yamlconfig['cleanup']
        iodaconvconfig['yamldir'] = yamlconfig['yamldir']
        iodaconvyaml = gen_gsinc_iodaconv_yaml(iodaconvconfig)
        print('ioda-converter GSI ncdiag YAML written to: '+iodaconvyaml)
        if 'slurm' in iodaconvconfig: # only support slurm currently
            slurmdict = iodaconvconfig['slurm']
            slurmdict['job'] = 'run_gsincdiag_iodaconv'
            slurmdict['jobyaml'] = iodaconvyaml
            slurmdict['jobscript'] = rootdir + '/scripts/%s.sh' % (slurmdict['job'])
            slurmdict['validtime'] = validtime
            iodaconvbatch = gen_slurm_submit(slurmdict)
            print('GSI ncdiag ioda-converters sbatch submission file written to: '+iodaconvbatch)
    if 'jedi hofx' in yamlconfig:
        jediconfig = yamlconfig['jedi hofx']
        jediconfig['validtime'] = validtime
        jediconfig['dump'] = yamlconfig['analysis cycle']['dump']
        jediconfig['rstprod'] = yamlconfig['analysis cycle']['restricted data']
        jediconfig['cleanup'] = yamlconfig['cleanup']
        jediconfig['yamldir'] = yamlconfig['yamldir']
        # create YAML for JEDI H(x) driver script
        jedihofxyaml = gen_fv3jedi_hofx_yaml(jediconfig)
        print('FV3-JEDI H(x) driver configuration YAML file written to: '+jedihofxyaml)
        if 'slurm' in jediconfig: # only support slurm currently
            slurmdict = jediconfig['slurm']
            slurmdict['job'] = 'run_fv3jedi_hofx_nomodel'
            slurmdict['jobyaml'] = jedihofxyaml
            slurmdict['jobscript'] = rootdir + '/scripts/%s.sh' % (slurmdict['job'])
            slurmdict['validtime'] = validtime
            hofxbatch = gen_slurm_submit(slurmdict)
            print('FV3-JEDI H(x) sbatch submission file written to: '+hofxbatch)
    if 'post' in yamlconfig:
        postconfig = yamlconfig['post']
        postconfig['validtime'] = validtime
        postconfig['dump'] = yamlconfig['analysis cycle']['dump']
        postconfig['cleanup'] = yamlconfig['cleanup']
        postconfig['yamldir'] = yamlconfig['yamldir']
        # create YAML for post processing driver script
        postyaml = gen_post_yaml(postconfig)
        print('PyGSI - GSI/UFO evaluation scripts YAML file written to: '+postyaml)
        if 'slurm' in jediconfig:
            slurmdict = jediconfig['slurm']
            slurmdict['job'] = 'run_post'
            slurmdict['jobyaml'] = jedihofxyaml
            slurmdict['jobscript'] = rootdir + '/scripts/%s.sh' % (slurmdict['job'])
            slurmdict['validtime'] = validtime
            postbatch = gen_slurm_submit(slurmdict)
            print('Post-processing sbatch submission file written to: '+postbatch)


parser = argparse.ArgumentParser(description='Generate YAML, other scripts, etc.'+\
                                ' to process a global analysis cycle and produce output')
parser.add_argument('-y', '--yaml', type=str,
                    help='path to YAML file for this analysis cycle', required=True)
args = parser.parse_args()
YAML = args.yaml
with open(YAML, 'r') as stream:
    yamlconfig = yaml.safe_load(stream)

main(yamlconfig)
