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

def genDataRow(valuelist, minlist, maxlist):
    # create a row of a table in HTML
    # format color of row depending on value/content of column

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
