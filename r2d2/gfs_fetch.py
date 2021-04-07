from solo.date import Hour, DateIncrement
from solo.logger import Logger
from solo.configuration import Configuration
from solo.basic_files import mkdir
from r2d2 import fetch, date_sequence


logger = Logger('gfs-fetch')
config = Configuration('gfs-config.yaml')
dates = date_sequence(config.start, config.end, config.step)

logger.info('preparing to copy files from local database')
for date in dates:

    ymdh = Hour(date).format('%Y%m%d%H')
    ymd = Hour(date).format('%Y%m%d')
    hh = Hour(date).format('%H')

    directory = f'{config.stage}/{ymdh}/{config.cdump}.{ymd}/{hh}/atmos/RESTART'
    mkdir(directory)

    # Fetch the metadata (coupler.res)
    fetch(
        type='fc',
        model='gfs_metadata',
        experiment=config.experiment,
        date=date,
        step=config.forecast_steps,
        resolution=config.resolution,
        user_date_format=config.user_date_format,
        fc_date_rendering=config.fc_date_rendering,
#        database=config.database,
        target_file=f'{directory}/$(valid_date).coupler.res',
        full_report='yes',
        report=f'fetch_meta_{date}.yaml'
        )

    # Fetch the tile files
    fetch(
        type='fc',
        model='gfs',
        experiment=config.experiment,
        date=date,
        step=config.forecast_steps,
        resolution=config.resolution,
        user_date_format=config.user_date_format,
        fc_date_rendering=config.fc_date_rendering,
#        database=config.database,
        file_type=['fv_core.res', 'fv_srf_wnd.res', 'fv_tracer.res', 'phy_data', 'sfc_data'],
        tile=config.tiles,
        target_file=f'{directory}/$(valid_date).$(file_type).tile$(tile).nc',
        full_report='yes',
        report=f'fetch_{date}.yaml'
        )
