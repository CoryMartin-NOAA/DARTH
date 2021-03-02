#!/usr/local/env python
# create_workflow.py
# setup rocoto workflow for DARTH
# cory.r.martin@noaa.gov
import yaml
import rocoto
import argparse
import sys
import workflow_utils as wfu
from collections import OrderedDict
import re

def main():
    parser = argparse.ArgumentParser(description='create rocoto workflow for DARTH')
    parser.add_argument('-y','--yaml', type=str, help='path to input YAML file', required=True)
    parser.add_argument('-x','--xml', type=str, help='path to output XML', required=True)
    args = parser.parse_args()
    create_workflow(args.yaml, args.xml)

def get_preamble():
    '''
        Generate preamble for XML
    '''

    strings = []

    strings.append('<?xml version="1.0"?>\n')
    strings.append('<!DOCTYPE workflow\n')
    strings.append('[\n')
    strings.append('\t<!--\n')
    strings.append('\tPROGRAM\n')
    strings.append('\t\tMain workflow manager for DARTH\n')
    strings.append('\n')
    strings.append('\tAUTHOR:\n')
    strings.append('\t\tCory Martin\n')
    strings.append('\t\tcory.r.martin@noaa.gov\n')
    strings.append('\n')
    strings.append('\tadapted from global-workflow rocoto scripts by Rahul Mahajan\n')
    strings.append('\n')
    strings.append('\t-->\n')

    return ''.join(strings)

def get_workflow_footer():
    '''
        Generate workflow footer
    '''

    strings = []
    strings.append('\n</workflow>\n')

    return ''.join(strings)

def create_entities(yamlconfig):
    machine = wfu.detectMachine()
    scheduler = wfu.get_scheduler(machine)
    interval = 24/int(yamlconfig['DARTH']['cycles'])
    if yamlconfig['background']['format'] == 'netcdf':
        histformat = 'nc'
    else:
        histformat = 'nemsio'
    strings = []
    strings.append('\n')
    strings.append('\t<!-- Experiment parameters such as name, starting, ending dates -->\n')
    strings.append('\t<!ENTITY PSLOT "DARTH">\n')
    strings.append('\t<!ENTITY SDATE "%s">\n' % yamlconfig['DARTH']['sdate'])
    strings.append('\t<!ENTITY EDATE "%s">\n' % yamlconfig['DARTH']['edate'])
    strings.append('\t<!ENTITY INTERVAL "%02d:00:00">\n' % interval)
    strings.append('\t<!ENTITY TOPYAML "%s">\n' % yamlconfig['mypath'])
    strings.append('\t<!ENTITY ROTDIR "%s">\n' % yamlconfig['DARTH']['comrot'])
    strings.append('\t<!ENTITY GESDIR "%s">\n' % yamlconfig['paths']['guessdir'])
    strings.append('\t<!ENTITY CDUMP "%s">\n' % yamlconfig['DARTH']['dump'])
    strings.append('\t<!ENTITY HOMEDARTH "%s">\n' % yamlconfig['paths']['rootdir'])
    strings.append('\t<!ENTITY JOBS_DIR "%s">\n' % (yamlconfig['paths']['rootdir']+'/jobs/rocoto'))
    strings.append('\t<!ENTITY HPSSROOT "%s">\n' % (yamlconfig['paths']['hpssroot']))
    strings.append('\t<!ENTITY STARTROOT "%s">\n' % (yamlconfig['paths']['startroot']))
    if yamlconfig['background']['gfsv16']:
        strings.append('\t<!ENTITY ATMDIR "/atmos/">\n')
    else:
        strings.append('\t<!ENTITY ATMDIR "/">\n')
    if yamlconfig['background']['lam']:
        strings.append('\t<!ENTITY ATMFILE "dynf006.%s">\n' % (histformat))
    else:
        strings.append('\t<!ENTITY ATMFILE "&CDUMP;t@Hz.atmf006.%s">\n' % (histformat))
    strings.append('\t<!-- Machine related entities -->\n')
    strings.append('\t<!ENTITY ACCOUNT    "%s">\n' % yamlconfig['account'])
    strings.append('\t<!ENTITY QUEUE      "%s">\n' % yamlconfig['queue'])
    strings.append('\t<!ENTITY QUEUE_ARCH "%s">\n' % yamlconfig['queue_arch'])
    if scheduler in ['slurm']:
            strings.append('\t<!ENTITY PARTITION_ARCH "%s">\n' % yamlconfig['partition_arch'])
    if scheduler in ['slurm'] and machine in ['ORION']:
        strings.append('\t<!ENTITY PARTITION_BATCH "%s">\n' % yamlconfig['partition'])
    strings.append('\t<!ENTITY SCHEDULER  "%s">\n' % scheduler)
    strings.append('\t<!ENTITY ROOTWORK "%s">\n' % yamlconfig['paths']['rootdir'])
    strings.append('\n')
    strings.append('\t<!-- ROCOTO parameters that control workflow -->\n')
    strings.append('\t<!ENTITY CYCLETHROTTLE "1">\n')
    strings.append('\t<!ENTITY TASKTHROTTLE  "25">\n')
    strings.append('\t<!ENTITY MAXTRIES      "2">\n')
    strings.append('\n')
    return ''.join(strings)

def get_resource_xml(task, resourcedict):
    wtimestr = resourcedict['maxtime']
    nodes = resourcedict['nodes']
    ppn = resourcedict['taskspernode']
    tpp = 1
    resstr = f'<nodes>{nodes}:ppn={ppn}:tpp={tpp}</nodes>'
    natstr = "--export=NONE"
    strings = []
    TASK = task.upper()
    strings.append('\t<!ENTITY QUEUE_%s_DARTH     "%s">\n' % (TASK, '&QUEUE;'))
    strings.append('\t<!ENTITY WALLTIME_%s_DARTH  "%s">\n' % (TASK, wtimestr))
    strings.append('\t<!ENTITY RESOURCES_%s_DARTH "%s">\n' % (TASK, resstr))
    strings.append('\t<!ENTITY NATIVE_%s_DARTH    "%s">\n' % (TASK, natstr))
    if task == 'gethpss':
        strings.append('\t<!ENTITY PARTITION_%s_DARTH "%s">\n' % (TASK, '&PARTITION_ARCH;'))
        strings.append('\t<!ENTITY MEMORY_%s_DARTH    "%s">\n' % (TASK, resourcedict['memory']))
    strings.append('\n')
    return ''.join(strings)

def get_workflow_header():
    strings = []
    strings.append('\n')
    strings.append(']>\n')
    strings.append('\n')
    strings.append('<workflow realtime="F" scheduler="&SCHEDULER;" cyclethrottle="&CYCLETHROTTLE;" taskthrottle="&TASKTHROTTLE;">\n')
    strings.append('\n')
    strings.append('\t<log verbosity="10"><cyclestr>&ROTDIR;/logs/@Y@m@d@H.log</cyclestr></log>\n')
    strings.append('\n')
    strings.append('\t<!-- Define the cycles -->\n')
    strings.append('\t<cycledef group="DARTH"  >&SDATE; &EDATE; &INTERVAL;</cycledef>\n')
    strings.append('\n')
    return ''.join(strings)

def get_tasks_xml(tasks):
    # create rocoto tasks based on YAML input
    envars = []
    if wfu.get_scheduler(wfu.detectMachine()) in ['slurm']:
        envars.append(rocoto.create_envar(name='SLURM_SET', value='YES'))
    envars.append(rocoto.create_envar(name='ROTDIR', value='&ROTDIR;'))
    envars.append(rocoto.create_envar(name='GESDIR', value='&GESDIR;'))
    envars.append(rocoto.create_envar(name='HOMEDARTH', value='&HOMEDARTH;'))
    envars.append(rocoto.create_envar(name='TOPYAML', value='&TOPYAML;'))
    envars.append(rocoto.create_envar(name='CDUMP', value='&CDUMP;'))
    envars.append(rocoto.create_envar(name='CDATE', value='<cyclestr>@Y@m@d@H</cyclestr>'))
    envars.append(rocoto.create_envar(name='PDY', value='<cyclestr>@Y@m@d</cyclestr>'))
    envars.append(rocoto.create_envar(name='cyc', value='<cyclestr>@H</cyclestr>'))
    envars.append(rocoto.create_envar(name='HPSSROOT', value='&HPSSROOT;'))

    dict_tasks = OrderedDict()
    for itask in tasks:
        if itask == 'gethpss':
            deps = []
            data = '&STARTROOT;/&CDUMP;.@Y@m@d/@H/&CDUMP;.t@Hz.prepbufr'
            dep_dict = {'type': 'data', 'data': data, 'offset': '01:18:00:00'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('gethpss', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHgethpss'] = task
        elif itask == 'prep':
            deps = []
            data = '&GESDIR;/&CDUMP;.@Y@m@d/@H&ATMDIR;&ATMFILE;'
            dep_dict = {'type': 'data', 'data': data, 'offset': '-&INTERVAL;'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('prep', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHprep'] = task
        elif itask == 'gsiobserver':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHprep'}
            deps.append(rocoto.add_dependency(dep_dict))
            data = '&GESDIR;/&CDUMP;.@Y@m@d/@H&ATMDIR;&ATMFILE;'
            dep_dict = {'type': 'data', 'data': data, 'offset': '-&INTERVAL;'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep_condition='and', dep=deps)
            task = wfu.create_wf_task('gsiobserver', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHgsiobserver'] = task
        elif itask == 'gsiiodaconv':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('gsiiodaconv', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHgsiiodaconv'] = task
        elif itask == 'jedihofx':
            if 'gsiiodaconv' in tasks:
                deps = []
                dep_dict = {'type': 'task', 'name': 'DARTHgsiiodaconv'}
                deps.append(rocoto.add_dependency(dep_dict))
                data = '&GESDIR;/&CDUMP;.@Y@m@d/@H&ATMDIR;RESTART/'
                dep_dict = {'type': 'data', 'data': data, 'offset': '-&INTERVAL;'}
                deps.append(rocoto.add_dependency(dep_dict))
                dependencies = rocoto.create_dependency(dep_condition='and', dep=deps)
                task = wfu.create_wf_task('jedihofx', cdump='DARTH', envar=envars, dependency=dependencies)
                dict_tasks['DARTHjedihofx'] = task
            else:
                deps = []
                dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
                deps.append(rocoto.add_dependency(dep_dict))
                data = '&GESDIR;/&CDUMP;.@Y@m@d/@H&ATMDIR;RESTART/'
                dep_dict = {'type': 'data', 'data': data, 'offset': '-&INTERVAL;'}
                deps.append(rocoto.add_dependency(dep_dict))
                dependencies = rocoto.create_dependency(dep_condition='and', dep=deps)
                task = wfu.create_wf_task('jedihofx', cdump='DARTH', envar=envars, dependency=dependencies)
                dict_tasks['DARTHjedihofx'] = task
        elif itask == 'post':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
            deps.append(rocoto.add_dependency(dep_dict))
            dep_dict = {'type': 'task', 'name': 'DARTHjedihofx'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep_condition='and', dep=deps)
            task = wfu.create_wf_task('post', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHpost'] = task
        else:
            print(itask+' is not supported')
    return dict_tasks

def dict_to_strings(dict_in):

    strings = []
    for key in dict_in.keys():
        strings.append(dict_in[key])
        strings.append('\n')

    return ''.join(strings)

def create_workflow(yamlpath, xmlpath):
    # read in YAML file for configuration
    with open(yamlpath, 'r') as stream:
        yamlconfig = yaml.safe_load(stream)
    yamlconfig['mypath'] = yamlpath
    darthconfig = yamlconfig['DARTH']
    # get list of tasks
    tasks = darthconfig['steps']
    task_dict = get_tasks_xml(tasks)
    # remove MEMORY
    for each_task in task_dict:
        temp_task_string = []
        if not each_task == 'DARTHgethpss':
            for each_line in re.split(r'(\s+)', task_dict[each_task]):
                if 'memory' not in each_line:
                    temp_task_string.append(each_line)
            task_dict[each_task] = ''.join(temp_task_string)

    # loop through tasks
    taskresources = {}
    xmlresources = []
    for task in tasks:
        taskresources[task] = yamlconfig[task]
        xmlresources.append(get_resource_xml(task, taskresources[task]))
    xmlresources = ''.join(xmlresources)

    # setup the XML
    preamble = get_preamble()
    workflow_footer = get_workflow_footer()

    xmlfile = []
    xmlfile.append(preamble)
    xmlfile.append(create_entities(yamlconfig))
    xmlfile.append(xmlresources)
    xmlfile.append(get_workflow_header())
    xmlfile.append(dict_to_strings(task_dict))
    xmlfile.append(workflow_footer)


    # Write the XML file
    fh = open(xmlpath, 'w')
    fh.write(''.join(xmlfile))
    fh.close()

    return


if __name__ == '__main__':
    main()
    sys.exit(0)
