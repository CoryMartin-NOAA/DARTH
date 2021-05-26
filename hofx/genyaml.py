from solo.logger import Logger
from solo.configuration import Configuration
from solo.template import TemplateConstants, Template
import click
import os
import pathlib

mydir = pathlib.Path(__file__).parent.absolute()

config_dict = {
    'hofx': ['base', 'hofx', 'cycle'],
    'stageObs': ['base', 'hofx', 'cycle'],
    'stageBkg': ['base', 'hofx', 'cycle'],
    'stageFV3JEDI': ['base'],
    'archHofX': ['base', 'hofx', 'cycle'],
}

logger = Logger('genYAML')

@click.command()
@click.argument('task', required=True)
@click.argument('expdir', required=True)
@click.argument('yamlout', required=True)
def run_gen_yaml(task, expdir, yamlout):
    # wrapper to call main function
    gen_yaml(task, expdir, yamlout)

def gen_yaml(task, expdir, yamlout=None, quiet=False):
    # parse, concatenate, replace vars in YAML and write a new
    # YAML file for the specified task/executable/script
    # get list of config YAMLs to read
    config_list = get_config_list(task)
    # read all experiment configs
    config = Configuration(os.path.join(expdir,'base.yaml'))
    for yamlfile in config_list:
        yamlpath = os.path.join(expdir,f'{yamlfile}.yaml')
        if not quiet:
            logger.info(f'Reading {yamlpath}')
        tmp_config = Configuration(yamlpath)
        config.update(tmp_config)
    # read in template
    template_yaml = os.path.join(mydir, 'templates', f'{task}.yaml')
    config_temp = Configuration(template_yaml)
    config_out = Configuration(template_yaml)
    # combine template with input config
    config_out.update(config)
    # replace variables in config
    config_out = replace_vars(config_out)
    # add 'includes' to config
    config_out = include_yaml(config_out)
    # do another find/replace with the includes
    config_out = replace_vars(config_out)
    # clean the YAML
    config_out = clean_yaml(config_out, config_temp)
    if yamlout:
        # write YAML file for this task
        target_dir = os.path.dirname(yamlout)
        target_name = os.path.basename(yamlout)
        config_out.save(target_dir=target_dir, target_name=target_name)
        if not quiet:
            logger.info(f'YAML for task {task} written to {yamlout}')
    return config_out

def get_config_list(task):
    # for the specified task, return a list of YAML files
    # that need to be 'sourced'
    config_list = config_dict[task]
    return config_list

def replace_vars(config):
    # use SOLO to replace variables in the configuration dictionary
    # as appropriate with either other dictionary key/value pairs
    # or environment variables
    config = Template.substitute_structure_from_environment(config)
    config = Template.substitute_with_dependencies(config, TemplateConstants.DOLLAR_PARENTHESES)
    config = Template.substitute_structure(config, TemplateConstants.DOUBLE_CURLY_BRACES, config.get)
    return config

def include_yaml(config):
    # look for the include yaml string and if it exists
    # 'include' that YAML in the config dictionary
    incstr = '$<<'
    for rootkey, rootval in config.items():
        if type(rootval) is list:
            # handle lists in the dictionary
            newlist = []
            for item in rootval:
                if incstr in item:
                    incpath = item.replace(incstr, '').strip()
                    newconfig = Configuration(incpath)
                    newlist.append(newconfig)
                else:
                    newlist.append(item) # keeps something in the list if it is not an include
            config[rootkey] = newlist
        else:
            # handle single includes
            if incstr in rootval:
                incpath = rootval.replace(incstr, '').strip()
                newconfig = Configuration(incpath)
                config[rootkey] = newconfig
    return config

def clean_yaml(config_out, config_template):
    # remove top level keys in config_out if they do not appear in config_template
    keys_to_del = []
    for key, value in config_out.items():
        if key not in config_template:
            keys_to_del.append(key)
    for key in keys_to_del:
        del config_out[key]
    return config_out

if __name__ == '__main__':
    run_gen_yaml()
