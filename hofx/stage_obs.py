from solo.logger import Logger
from solo.basic_files import mkdir
from r2d2 import fetch
from genyaml import gen_yaml as get_config
import click

logger = Logger('stageObs')
@click.command()
@click.argument('expdir', required=True)
def stage_obs(expdir):
    # stage observations based on environment vars
    # and vars set in config YAMLs in experiment dir
    # get config
    config = get_config('stageObs', expdir, quiet=True)
    logger.info(f"Preparing to stage observations for {config['window begin']}")
    mkdir(config['obs_dir'])
    for ob in config['observations']:
        obname = ob['obs space']['name'].lower()
        outfile = ob['obs space']['obsdatain']['obsfile']
        # try to grab obs
        fetch(
            type='ob',
            provider=config['obs_src'],
            experiment=config['obs_dump'],
            date=config['window begin'],
            obs_type=obname,
            time_window=config['window length'],
            target_file=outfile,
            ignore_missing=True,
            database=config['obs_db'],
            #full_report  = 'yes',
            #report = f"fetch_{obname}_{config['window begin']}.yaml",
        )
        # try to grab bias correction files too
        if 'obs bias' in ob:
            satbias = ob['obs bias']['input file']
            fetch(
                type='bc',
                provider=config['bc_src'],
                experiment=config['bc_dump'],
                date=config['cycle'],
                obs_type=obname,
                target_file=satbias,
                file_type='satbias',
                ignore_missing=True,
                database=config['obs_db'],
                #full_report  = 'yes',
                #report = f"fetch_satbias_{obname}_{config['window begin']}.yaml",
            )
            # below is lazy but good for now...
            tlapse = satbias.replace('satbias.nc4', 'tlapse.txt')
            fetch(
                type='bc',
                provider=config['bc_src'],
                experiment=config['bc_dump'],
                date=config['cycle'],
                obs_type=obname,
                target_file=tlapse,
                file_type='tlapse',
                ignore_missing=True,
                database=config['obs_db'],
                #full_report  = 'yes',
                #report = f"fetch_tlapse_{obname}_{config['window begin']}.yaml",
            )


if __name__ == '__main__':
    stage_obs()
