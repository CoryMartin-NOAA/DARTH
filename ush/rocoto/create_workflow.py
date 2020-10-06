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


if __name__ == '__main__':
    main()
    sys.exit(0)
