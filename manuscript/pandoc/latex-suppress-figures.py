#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
This script excises figures from a LaTeX source document.
'''

from __future__ import print_function
import sys
infile = sys.argv[-2]
outfile = sys.argv[-1]
fig = False
fignum = 1

figs = dict()

# create a dict of figure names / numbers
with open(infile, 'r') as f:
    for line in f:
        if '\\begin{figure}' in line:
            fig = True
        if fig and '\\label' in line:
            figname = line.split('label{')[-1].split('}')[0]
            figs[figname] = str(fignum)
        if '\\end{figure}' in line:
            fig = False
            fignum += 1

print('\n'.join(['{}: {}'.format(k, v) for k, v in figs.items()]))
fignum = 1
# read input file & write output file line by line
with open(infile, 'r') as f, open(outfile, 'w') as g:
    for line in f:
        # replace figure references with figure numbers
        if '\\ref{' in line:
            for figname in figs.keys():
                ref = '\\ref{{{}}}'.format(figname)
                if ref in line:
                    line = line.replace(ref, figs[figname])
        # replace figure code / caption with placeholder
        if '\\begin{figure}' in line:
            fig = True
            g.write(('\\begin{{center}}\\bfseries [Insert Figure {} about here]'
                     '\\end{{center}}\n').format(fignum))
        if not fig:
            g.write(line)
        if '\\end{figure}' in line:
            fig = False
            fignum += 1
