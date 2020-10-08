#!/usr/bin/env python
# link_fv3jedi_hofx_obs.py
# link observations to working directory
# given two input YAML configuration files
import argparse
import yaml

def main(hofxyamlfile, configyamlfile):
    

parser = argparse.ArgumentParser(description='Link IODA observations to working directory'+\
                                ' given two input YAML config files')
parser.add_argument('-h','--hofxyaml', type=str, help='path of YAML used by H(x) application', required=True)
parser.add_argument('-c','--configyaml', type=str, help='path of high level YAML configuration file', required=True)
args = parser.parse_args()

main(args.hofxyaml, args.configyaml)
