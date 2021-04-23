import glob
import os
import shutil
import datetime

ozdiag = ['omps_npp']  # fill out later

def genNavPanel(cyclelist, templatefile, outfile):
    # read in template and generate NavPanel
    with open(templatefile) as htmlin:
        cycleconvtable = ''
        cycleconvplots = ''
        cycleradtable = ''
        cycleradplots = ''
        for cycle in cyclelist:
            cycleconvtable = cycleconvtable + f'<OPTION VALUE="{cycle}_convtable.html" selected >{cycle}</option>\n'
            cycleconvplots = cycleconvplots + f'<OPTION VALUE="{cycle}_convplots.html" selected >{cycle}</option>\n'
            cycleradtable = cycleradtable + f'<OPTION VALUE="{cycle}_radtable.html" selected >{cycle}</option>\n'
            cycleradplots = cycleradplots + f'<OPTION VALUE="{cycle}_radplots.html" selected >{cycle}</option>\n'
        replacements = {
            '{{CYCLECONVTABLE}}': cycleconvtable,
            '{{CYCLECONVPLOTS}}': cycleconvplots,
            '{{CYCLERADTABLE}}': cycleradtable,
            '{{CYCLERADPLOTS}}': cycleradplots,
        }
        with open(outfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src,target)
                htmlout.write(line)

def genMainPanel(cyclelist, templatefile, outfile, expname):
    # read in template and generate main homepage panel
    with open(templatefile) as htmlin:
        cyclehtml = ''
        for cycle in cyclelist:
            cyclehtml = cyclehtml + f'{cycle}<br>\n'
        timestr = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        replacements = {
            '{{CYCLES}}': cyclehtml,
            '{{EXPERIMENT}}': expname,
            '{{GENTIME}}': timestr,
        }
        with open(outfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src,target)
                htmlout.write(line)

def genDataRow(valuelist, minlist, maxlist):
    # create a row of a table in HTML
    # format color of row depending on value/content of column
    print(valuelist)

def genConvTable(cycle, ConvDict, outpath):
    # generate HTML table of info on conventional data
    htmlstr = ''
    htmlstr = htmlstr + f'<html><h1>Conventional Data Summary for {cycle}</h1>\n'
    htmlstr = htmlstr + '<style>table, th, td { border: 1px solid black; border-collapse: collapse;}</style>'
    ## create massive table here from input dictionary
    for ConvType, TypeDict in ConvDict.items():
        # ConvType being sondes, sfc, etc.
        # new table for each type
        newline = f'<h2>{ConvType}</h2>\n'
        htmlstr = ''.join((htmlstr, newline))
        columns = TypeDict['columns']
        minlist = TypeDict['threshold_min']
        maxlist = TypeDict['threshold_max']
        newline = '<table style="width:90%"><tr>\n'
        htmlstr = ''.join((htmlstr, newline))
        for col in columns:
            htmlstr = htmlstr + f'<th>{col}</th>\n'
        htmlstr = htmlstr + '</tr>\n'
        for row, rowvalues in TypeDict.items():
            if row in ['columns', 'threshold_min', 'threshold_max']:
                continue
            newline = genDataRow(rowvalues, minlist, maxlist)
            htmlstr = htmlstr + newline
        htmlstr = htmlstr + '</table>'
    htmlstr = htmlstr + '</html>'
    outfile = f'{outpath}/html/{cycle}_convtable.html'
    with open(outfile, 'w') as htmlout:
        htmlout.write(htmlstr)

def genConvPlotPage(cycledir, outfile):
    # find all conventional plots in this directory, group them properly,
    # and put them into a basic HTML page for viewing/clicking
    cycle = os.path.basename(cycledir)
    # get list of all png files
    all_figs = glob.glob(os.path.join(cycledir,'*.png'))
    sensors = []
    for fig in all_figs:
        figbase = os.path.basename(fig).split('_')
        obtype = '_'.join(figbase[0:figbase.index('hofx')])
        if len(obtype.split('_')) == 1:
            if obtype not in sensors:
                sensors.append(obtype)
    # create initial header of HTML file
    htmlstr = ''
    htmlstr = htmlstr + f'<html><h1>Conventional observation figures for {cycle}</h1>\n'
    # loop over sensors and types of figures and put into page
    for sensor in sensors:
        htmlstr = htmlstr + f'<br><h2>{sensor}</h2><br>\n'
        # loop over types
        for ptype in ['hofx']:
            # get all figs matching
            my_figs = sorted(glob.glob(os.path.join(cycledir,f'{sensor}_{ptype}_*.png')))
            # start creating HTML
            htmlstr = htmlstr + f'<h3>{ptype}</h3>\n'
            nrow = 3
            irow = 0
            for fig in my_figs:
                relpath = f'figs/{cycle}/{os.path.basename(fig)}'
                href = f'<a href="{relpath}"><img src="{relpath}" style="width:300px; height:220px" title="{os.path.basename(fig)}"></a>\n'
                htmlstr = htmlstr + href
                irow = irow + 1
                if irow == nrow:
                    htmlstr = htmlstr + '<br>\n'
                    irow = 0
    # html footer
    htmlstr = htmlstr + '</html>'
    with open(outfile, 'w') as htmlout:
        htmlout.write(htmlstr)

def genRadPlotPage(cycledir, outfile):
    # find all radiance plots in this directory, group them properly,
    # and put them into a basic HTML page for viewing/clicking
    cycle = os.path.basename(cycledir)
    # get list of all png files
    all_figs = glob.glob(os.path.join(cycledir,'*.png'))
    sensors = []
    for fig in all_figs:
        figbase = os.path.basename(fig).split('_')
        obtype = '_'.join(figbase[0:figbase.index('hofx')])
        if len(obtype.split('_')) > 1:
            if obtype not in ozdiag:
                if obtype not in sensors:
                    sensors.append(obtype)
    # create initial header of HTML file
    htmlstr = ''
    htmlstr = htmlstr + f'<html><h1>Radiance observation figures for {cycle}</h1>\n'
    # loop over sensors and types of figures and put into page
    for sensor in sensors:
        htmlstr = htmlstr + f'<br><h2>{sensor}</h2><br>\n'
        # loop over types
        for ptype in ['hofx']:
            # get all figs matching
            my_figs = glob.glob(os.path.join(cycledir,f'{sensor}_{ptype}_*.png'))
            # sort by channel
            chans = [int(os.path.basename(c).split('_')[-2]) for c in my_figs]
            my_figs = [x for _, x in sorted(zip(chans, my_figs))]
            # start creating HTML
            htmlstr = htmlstr + f'<h3>{ptype}</h3>\n'
            nrow = 3
            irow = 0
            for fig in my_figs:
                relpath = f'figs/{cycle}/{os.path.basename(fig)}'
                href = f'<a href="{relpath}"><img src="{relpath}" style="width:300px; height:220px" title="{os.path.basename(fig)}"></a>\n'
                htmlstr = htmlstr + href
                irow = irow + 1
                if irow == nrow:
                    htmlstr = htmlstr + '<br>\n'
                    irow = 0
    # html footer
    htmlstr = htmlstr + '</html>'
    with open(outfile, 'w') as htmlout:
        htmlout.write(htmlstr)

def genSite(htmldir, templatedir, expname='evaltest'):
    # generate HTML for DARTH site depending on what figures, etc. are in htmldir
    # get list of cycles
    cycledirs = glob.glob(os.path.join(htmldir, 'figs', '*'))
    cycles = [os.path.basename(c) for c in cycledirs]
    # create index.html if it does not exist
    index_html = os.path.join(htmldir,'index.html')
    if os.path.exists(index_html):
        os.remove(index_html)
    shutil.copy(os.path.join(templatedir,'index.html'), index_html)
    templatefile = os.path.join(templatedir, 'navtemplate.html')
    outfile = os.path.join(htmldir, 'panel.html')
    genNavPanel(cycles, templatefile, outfile)
    outfile = os.path.join(htmldir, 'main.html')
    templatefile = os.path.join(templatedir, 'maintemplate.html')
    genMainPanel(cycles, templatefile, outfile, expname)
    for cycle, cycledir in zip(cycles, cycledirs):
        outfile = os.path.join(htmldir, f'{cycle}_radplots.html')
        genRadPlotPage(cycledir, outfile)
        outfile = os.path.join(htmldir, f'{cycle}_convplots.html')
        genConvPlotPage(cycledir, outfile)
