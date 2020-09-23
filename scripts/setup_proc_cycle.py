#!/usr/bin/env python
# setup_proc_cycle.py
# generate YAML, other scripts, etc. needed
# to process a global analysis cycle and produce output
# cory.r.martin@noaa.gov

import argparse
import yaml

def gen_batch(yamlconfig):
    """
    Use YAML input to generate batch job submission scripts
    """

def main(yamlconfig):
    gen_batch(yamlconfig)

parser = argparse.ArgumentParser(description='Generate YAML, other scripts, etc.'+\
                                ' to process a global analysis cycle and produce output')
parser.add_argument('-y', '--yaml', type=str,
                    help='path to YAML file for this analysis cycle', required=True)
args = parser.parse_args()
YAML = args.yaml
with open(YAML, 'r') as stream:
    yamlconfig = yaml.safe_load(stream)

main(yamlconfig)
