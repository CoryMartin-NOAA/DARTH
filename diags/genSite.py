#!/usr/bin/env python
import DARTHsite
import argparse
import pathlib
import os

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    # get working/processing path from command line
    ap.add_argument(
        '-d',
        '--htmldir',
        help='path to where figs/ dir is and where HTML will be saved to',
        required=True
    )
    # get optional experiment name from command line
    ap.add_argument(
        '-e',
        '--expname',
        help='name of this experiment',
        default='',
        required=False,
    )
    # get templatedir from my path
    my_dir = pathlib.Path(__file__).parent.absolute()
    template_dir = os.path.join(my_dir, 'webcontent')
    # parse the args
    args = ap.parse_args()
    DARTHsite.gen_site(args.htmldir, template_dir, expname=args.expname)
    print(f'HTML written to {args.htmldir}')
