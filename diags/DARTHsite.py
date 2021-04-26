import glob
import os
import shutil
import datetime

ozdiag = ['omps_npp']  # fill out later

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

def genRadPage(htmlfile, templatefile, cycles, sensor):
    # generate main html page for each individual sensor
    with open(templatefile) as htmlin:
        # create javascript for all available cycles
        cychtml = ''
        for cyc in cycles:
            cychtml = cychtml + f'validtimes.push({{displayName: "{cyc}", name: "{cyc}"}});\n'
        # create javascript for all channels
        chanhtml = ''
        chans = []
        for ch in chans:
            chanhtml = chanhtml + f'channels.push({{displayName: "{ch}", name: "{ch}"}});\n'
        replacements = {
            '{{SENSOR}}': sensor,
            '{{CYCLEPUSH}}': cychtml,
            '{{CHANNELPUSH}}': chanhtml,
            '{{CYCLE1}}': cycles[0],
        }
        with open(htmlfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src,target)
                htmlout.write(line)

def genRootIndex(htmldir, templatefile, cycledirs, expname):
    # create index.html for the top level page from a template
    with open(templatefile) as htmlin:
        # get list of all sensors in the cycledirs
        sensors = []
        for cycle in cycledirs:
            dirs = glob.glob(os.path.join(cycle, '*'))
            for sdir in dirs:
                sensor = os.path.basename(sdir)
                if sensor not in sensors:
                    sensors.append(sensor)
        # get list of rad, conv, oz sensors for menus
        radlist = []
        convlist = []
        ozlist = []
        for obtype in sensors:
            if len(obtype.split('_')) > 1:
                radlist.append(obtype) if obtype not in ozdiag else ozlist.append(obtype)
            else:
                convlist.append(obtype)
        # create HTML to replace in template
        rad_html = ''
        conv_html = ''
        oz_html = ''
        for rad in radlist:
            rad_html = rad_html + f'<a href="rad/{rad}/index.html">{rad.upper()}</a>\n'
        for conv in convlist:
            conv_html = conv_html + f'<a href="conv/{conv}/index.html">{conv.upper()}</a>\n'
        for oz in ozlist:
            oz_html = oz_html + f'<a href="oz/{oz}/index.html">{oz.upper()}</a>\n'
        # find and replace in template
        replacements = {
            '{{EXPNAME}}': expname,
            '{{RADLIST}}': rad_html,
            '{{CONVLIST}}': conv_html,
            '{{OZLIST}}': oz_html,
            '{{CONTENTHTML}}': 'main.html',
            '{{HOMEPATH}}': '',
        }
        outfile = os.path.join(htmldir, 'index.html')
        with open(outfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src,target)
                htmlout.write(line)
    return radlist, convlist, ozlist

def genSensorIndex(htmlfile, templatefile, expname, mysensor, radlist, convlist, ozlist):
    # creates index.html for the individual ob type pages
    with open(templatefile) as htmlin:
        # create HTML to replace in template
        rad_html = ''
        conv_html = ''
        oz_html = ''
        for rad in radlist:
            rad_html = rad_html + f'<a href="../../rad/{rad}/index.html">{rad.upper()}</a>\n'
        for conv in convlist:
            conv_html = conv_html + f'<a href="../../conv/{conv}/index.html">{conv.upper()}</a>\n'
        for oz in ozlist:
            oz_html = oz_html + f'<a href="../../oz/{oz}/index.html">{oz.upper()}</a>\n'
        # find and replace in template
        replacements = {
            '{{EXPNAME}}': expname,
            '{{RADLIST}}': rad_html,
            '{{CONVLIST}}': conv_html,
            '{{OZLIST}}': oz_html,
            '{{CONTENTHTML}}': f'{mysensor}.html',
            '{{HOMEPATH}}': '../../index.html'
        }
        with open(htmlfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src,target)
                htmlout.write(line)

def genSite(htmldir, templatedir, expname='evaltest'):
    # generate HTML for DARTH site depending on what figures, etc. are in htmldir
    # get list of cycles
    cycledirs = glob.glob(os.path.join(htmldir, 'figs', '*'))
    cycles = [os.path.basename(c) for c in cycledirs]
    # just copy main.html if it does not exist
    main_html = os.path.join(htmldir,'main.html')
    if os.path.exists(main_html):
        os.remove(main_html)
    shutil.copy(os.path.join(templatedir,'main.html'), main_html)
    # create top level index.html
    radlist, convlist, ozlist = genRootIndex(htmldir,
                                os.path.join(templatedir,'index.html'),
                                cycledirs,
                                expname,
                                )
    # now for each rad, conv, oz sensor, make a directory/html pages
    # if not os.path.exists(os.path.join(htmldir, 'rad')):
    #     os.makedirs(os.path.join(htmldir, 'rad'))
    # if not os.path.exists(os.path.join(htmldir, 'conv')):
    #     os.makedirs(os.path.join(htmldir, 'conv'))
    # if not os.path.exists(os.path.join(htmldir, 'oz')):
    #     os.makedirs(os.path.join(htmldir, 'oz'))
    for rad in radlist:
        if not os.path.exists(os.path.join(htmldir, 'rad', rad)):
            os.makedirs(os.path.join(htmldir, 'rad', rad))
        genSensorIndex(os.path.join(htmldir, 'rad', rad, 'index.html'),
                       os.path.join(templatedir,'index.html'),
                       expname, rad, radlist, convlist, ozlist)
        genRadPage(os.path.join(htmldir, 'rad', rad, f'{rad}.html'),
                   os.path.join(templatedir,'radmain.html'),
                   cycles, rad)
    for conv in convlist:
        if not os.path.exists(os.path.join(htmldir, 'conv', conv)):
            os.makedirs(os.path.join(htmldir, 'conv', conv))
        genSensorIndex(os.path.join(htmldir, 'conv', conv, 'index.html'),
                       os.path.join(templatedir,'index.html'),
                       expname, conv, radlist, convlist, ozlist)
    for oz in ozlist:
        if not os.path.exists(os.path.join(htmldir, 'oz', oz)):
            os.makedirs(os.path.join(htmldir, 'oz', oz))
        genSensorIndex(os.path.join(htmldir, 'oz', oz, 'index.html'),
                       os.path.join(templatedir,'index.html'),
                       expname, oz, radlist, convlist, ozlist)
