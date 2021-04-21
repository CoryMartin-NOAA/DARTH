#!/usr/bin/env python
import os
import datetime as dt
import subprocess
import csv
import shutil
import glob

StartTime = dt.datetime(2020,12,14,18)
EndTime = dt.datetime(2021,1,13,6)
#EndTime = dt.datetime(2020,12,15,0)
RootIn = '/work/noaa/da/cmartin/noscrub/UFO_eval/GFS/v15ops/'
RootWork = '/work/noaa/stmp/cmartin/satbias/'
MyDir = '/work/noaa/da/Cory.R.Martin/noscrub/UFO_eval/DARTH/gsibc/'
YAMLtemplate = os.path.join(MyDir,'satbias_converter.yaml')
Exe = '/work/noaa/da/cmartin/noscrub/UFO_eval/ioda-bundle/build/bin/satbias2ioda.x'

NowTime = StartTime
while NowTime <= EndTime:
    # create temp directory for this cycle
    WorkDir = os.path.join(RootWork, NowTime.strftime('%Y%m%d%H'))
    os.makedirs(WorkDir, exist_ok=True)
    # link files needed from GSI
    DARTHTime = NowTime + dt.timedelta(hours=6)
    MyIn = os.path.join(RootIn, DARTHTime.strftime('%Y%m%d%H'),
                                NowTime.strftime('gdas.%Y%m%d'),
                                NowTime.strftime('%H'))
    abias_path = os.path.join(MyIn, NowTime.strftime('gdas.t%Hz.abias'))
    abias_pc_path = os.path.join(MyIn, NowTime.strftime('gdas.t%Hz.abias_pc'))
    if os.path.exists(os.path.join(WorkDir, 'satbias_crtm_in')):
        os.unlink(os.path.join(WorkDir, 'satbias_crtm_in'))
        os.unlink(os.path.join(WorkDir, 'satbias_crtm_pc'))
    if os.path.exists(os.path.join(WorkDir, 'satbias2ioda.x')):
        os.unlink(os.path.join(WorkDir, 'satbias2ioda.x'))
    os.symlink(abias_path, os.path.join(WorkDir, 'satbias_crtm_in'))
    os.symlink(abias_pc_path, os.path.join(WorkDir, 'satbias_crtm_pc'))
    # open the text file to get a list of satellite/sensors to process
    satlist = []
    with open(os.path.join(WorkDir, 'satbias_crtm_in')) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            splitrow = row[0].split()
            if splitrow[1] not in satlist:
                try:
                    a = float(splitrow[1])
                except:
                    if len(splitrow[1]) > 0:
                        satlist.append(splitrow[1])
    # too lazy to do the grep thing in python, using subprocess instead
    os.symlink(Exe, os.path.join(WorkDir, 'satbias2ioda.x'))
    for sat in satlist:
        cmd = f'grep -i {sat} satbias_crtm_in | awk \'{{print $2" "$3" "$4}}\' > {sat}_tlapmean.txt'
        p = subprocess.Popen(cmd, shell=True, cwd=WorkDir)
    # create YAML from satlist
    satYAML = os.path.join(WorkDir, 'satbias_converter.yaml')
    shutil.copy(YAMLtemplate, satYAML)
    with open(satYAML, 'a') as yamlfile:
        for sat in satlist:
            yamlfile.write(f'- sensor: {sat}\n')
            yamlfile.write(f'  output file: {sat}_satbias.nc4\n')
            yamlfile.write('  predictors: *default_preds\n')
    cmd = f'./satbias2ioda.x satbias_converter.yaml'
    p = subprocess.Popen(cmd, shell=True, cwd=WorkDir)
    p.communicate()
    # copy output files to original directory
    ncfiles = glob.glob(WorkDir+'/*.nc4')
    txtfiles = glob.glob(WorkDir+'/*.txt')
    try:
        os.makedirs(os.path.join(MyIn, 'gsibc'))
    except:
        pass
    for f in ncfiles:
        shutil.move(f, os.path.join(MyIn, 'gsibc', os.path.basename(f)))
    for f in txtfiles:
        shutil.move(f, os.path.join(MyIn, 'gsibc', os.path.basename(f)))
    # advance to next cycle
    NowTime = NowTime + dt.timedelta(hours=6)
