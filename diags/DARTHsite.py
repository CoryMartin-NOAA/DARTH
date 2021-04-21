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
