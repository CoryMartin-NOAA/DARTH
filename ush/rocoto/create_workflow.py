#!/usr/local/env python
# create_workflow.py
# setup rocoto workflow for DARTH
# cory.r.martin@noaa.gov
import yaml
import rocoto
import argparse
import sys
import workflow_utils as wfu

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
    strings = []
    strings.append('\n')
    strings.append('\t<!-- Experiment parameters such as name, starting, ending dates -->\n')
    strings.append('\t<!ENTITY PSLOT "DARTH">\n')
    strings.append('\t<!ENTITY SDATE "%s">\n' % yamlconfig['DARTH']['sdate'])
    strings.append('\t<!ENTITY EDATE "%s">\n' % yamlconfig['DARTH']['edate'])
    strings.append('\t<!ENTITY INTERVAL "%02d:00:00">\n' % interval)
    strings.append('\t<!ENTITY TOPYAML "%s">\n' % yamlconfig['mypath'])
    strings.append('\t<!ENTITY COMROT "%s">\n' % yamlconfig['DARTH']['comrot'])
    strings.append('\t<!ENTITY CDUMP "%s">\n' % yamlconfig['DARTH']['dump'])
    strings.append('\t<!ENTITY HOMEDARTH "%s">\n' % yamlconfig['paths']['rootdir'])
    strings.append('\t<!-- Machine related entities -->\n')
    strings.append('\t<!ENTITY ACCOUNT    "%s">\n' % yamlconfig['account'])
    strings.append('\t<!ENTITY QUEUE      "%s">\n' % yamlconfig['queue'])
    strings.append('\t<!ENTITY SCHEDULER  "%s">\n' % scheduler)
    strings.append('\t<!ENTITY ROOTWORK "%s">\n' % yamlconfig['paths']['rootdir'])
    strings.append('\n')
    strings.append('\t<!-- ROCOTO parameters that control workflow -->\n')
    strings.append('\t<!ENTITY CYCLETHROTTLE "3">\n')
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
    strings.append('\t<!ENTITY QUEUE_%s     "%s">\n' % (task, '&QUEUE;'))
    strings.append('\t<!ENTITY WALLTIME_%s  "%s">\n' % (task, wtimestr))
    strings.append('\t<!ENTITY RESOURCES_%s "%s">\n' % (task, resstr))
    strings.append('\t<!ENTITY NATIVE_%s    "%s">\n' % (task, natstr))
    return ''.join(strings)

def get_workflow_header():
    strings = []
    strings.append('\n')
    strings.append(']>\n')
    strings.append('\n')
    strings.append('<workflow realtime="F" scheduler="&SCHEDULER;" cyclethrottle="&CYCLETHROTTLE;" taskthrottle="&TASKTHROTTLE;">\n')
    strings.append('\n')
    strings.append('\t<log verbosity="10"><cyclestr>&COMROT;/logs/@Y@m@d@H.log</cyclestr></log>\n')
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
    envars.append(rocoto.create_envar(name='COMROT', value='&COMROT;'))
    envars.append(rocoto.create_envar(name='HOMEDARTH', value='&HOMEDARTH;'))
    envars.append(rocoto.create_envar(name='TOPYAML', value='&TOPYAML;'))
    envars.append(rocoto.create_envar(name='CDUMP', value='&CDUMP;')
    envars.append(rocoto.create_envar(name='CDATE', value='<cyclestr>@Y@m@d@H</cyclestr>'))
    envars.append(rocoto.create_envar(name='PDY', value='<cyclestr>@Y@m@d</cyclestr>'))
    envars.append(rocoto.create_envar(name='cyc', value='<cyclestr>@H</cyclestr>'))

    dict_tasks = OrderedDict()
    for task in tasks:
        if task == 'prep':
            deps = []
            data = '&COMROT/&CDUMP.@Y@m@d/@H/atmos/gdas.t@Hz.atmf006.nc'
            dep_dict = {'type': 'data', 'data': data, 'offset': '-&INTERVAL;'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('prep', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHprep'] = task
        elif task == 'gsiobserver':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHprep'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('gsiobserver', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHgsiobserver'] = task
        elif task == 'gsiiodaconv':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep=deps)
            task = wfu.create_wf_task('gsiiodaconv', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHgsiiodaconv'] = task
        elif task == 'jedihofx':
            if 'gsiiodaconv' in tasks:
                deps = []
                dep_dict = {'type': 'task', 'name': 'DARTHgsiiodaconv'}
                deps.append(rocoto.add_dependency(dep_dict))
                dependencies = rocoto.create_dependency(dep=deps)
                task = wfu.create_wf_task('jedihofx', cdump='DARTH', envar=envars, dependency=dependencies)
                dict_tasks['DARTHjedihofx'] = task
            else:
                deps = []
                dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
                deps.append(rocoto.add_dependency(dep_dict))
                dependencies = rocoto.create_dependency(dep=deps)
                task = wfu.create_wf_task('jedihofx', cdump='DARTH', envar=envars, dependency=dependencies)
                dict_tasks['DARTHjedihofx'] = task
        elif task == 'post':
            deps = []
            dep_dict = {'type': 'task', 'name': 'DARTHgsiobserver'}
            deps.append(rocoto.add_dependency(dep_dict))
            dep_dict = {'type': 'task', 'name': 'DARTHjedihofx'}
            deps.append(rocoto.add_dependency(dep_dict))
            dependencies = rocoto.create_dependency(dep_condition='and', dep=deps)
            task = wfu.create_wf_task('post', cdump='DARTH', envar=envars, dependency=dependencies)
            dict_tasks['DARTHpost'] = task
        else:
            print(task+' is not supported')
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
    xmlfile.append(dict_to_strings(get_tasks_xml(tasks)))
    xmlfile.append(workflow_footer)


    # Write the XML file
    fh = open(xmlpath, 'w')
    fh.write(''.join(xmlfile))
    fh.close()

    return


if __name__ == '__main__':
    main()
    sys.exit(0)
