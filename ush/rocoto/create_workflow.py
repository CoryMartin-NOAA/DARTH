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
    strings = []
    strings.append('\n')
    strings.append('\t<!-- Experiment parameters such as name, starting, ending dates -->\n')
    strings.append('\t<!ENTITY PSLOT "DARTH">\n')
    strings.append('\t<!ENTITY SDATE "%s">\n' % yamlconfig['DARTH']['sdate'])
    strings.append('\t<!ENTITY EDATE "%s">\n' % yamlconfig['DARTH']['edate'])
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

def create_workflow(yamlpath, xmlpath):
    # read in YAML file for configuration
    with open(yamlpath, 'r') as stream:
        yamlconfig = yaml.safe_load(stream)
    darthconfig = yamlconfig['DARTH']
    # get list of tasks
    tasks = darthconfig['steps']
    # loop through tasks
    for task in tasks:
        taskresources = yamlconfig[task]


    # setup the XML
    preamble = get_preamble()
    workflow_footer = get_workflow_footer()
    xmlfile = []
    xmlfile.append(preamble)
    xmlfile.append(create_entities(yamlconfig))
    xmlfile.append(workflow_footer)

    # Write the XML file
    fh = open(xmlpath, 'w')
    fh.write(''.join(xmlfile))
    fh.close()

    return


if __name__ == '__main__':
    main()
    sys.exit(0)
