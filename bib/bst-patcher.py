# -*- coding: utf-8 -*-
import sys

infile = sys.argv[-2]
outfile = sys.argv[-1]

with open(infile, 'r') as f, open(outfile, 'w') as g:
    # main loop
    for line in f:
        # see http://tex.stackexchange.com/a/112278/19160
        line = line.replace('", " swap$ * *', '", " *')
        # use unicode quotes
        line = line.replace('{\\enquote}[1]{``#1\'\'}', '{\\enquote}[1]{“#1”}')
        # no URL prefix
        line = line.replace('{\\urlprefix}{URL }', '{\\urlprefix}{}')
        g.write(line)
