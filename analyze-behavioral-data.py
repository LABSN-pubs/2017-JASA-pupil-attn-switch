# -*- coding: utf-8 -*-
"""
===============================================================================
Script ''
===============================================================================

This script cleans and analyzes behavioral data for the vocoder/switch-gap
and gender/reverb experiments.
"""
# @author: Dan McCloy  (drmccloy@uw.edu)
# Created on Wed Jan 13 16:40:10 2016
# License: BSD (3-clause)

import numpy as np
import pandas as pd
from os import getcwd
from os import path as op
from expyfun import analyze as efa
from matplotlib import rcParams
from matplotlib import pyplot as plt

# file I/O
work_dir = getcwd()
data_dir = 'data-behavioral'
fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# rcparams
rcp = {'font.sans-serif': ['M+ 1c'], 'font.style': 'normal',
       'font.size': 14, 'font.variant': 'normal', 'font.weight': 'medium',
       'pdf.fonttype': 42}
plt.rcdefaults()
rcParams.update(rcp)

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# loop over experiments
for ix, fname in enumerate(fnames):
    aggvars = ['subj', 'attn', ['reverb', 'voc_chan'][ix],
               ['gender', 'gap_len'][ix]]
    longform = pd.read_csv(op.join(data_dir, fname), sep='\t')
    longform['corr_rej'] = 4 - longform['hits'] - longform['false_alarms']
    longform['attn'] = np.array(['maint.', 'switch']
                                )[(longform['maint1_switch2'] == 2
                                   ).values.astype(int).tolist()]
    if ix:
        longform['voc_chan'] = longform['band']
        longform['gap_len'] = np.array(['long', 'short']
                                       )[(longform['cue_1u_2d'] == 1
                                          ).values.astype(int).tolist()]
    else:
        longform['reverb'] = np.array(['anech.', 'reverb']
                                      )[(longform['band'] == 10
                                         ).values.astype(int).tolist()]
        longform['gender'] = np.array(['MF', 'MM']
                                      )[(longform['cue_1u_2d'] == 1
                                         ).values.astype(int).tolist()]

    # loop over manipulations
    fig, axs = plt.subplots(1, 3, figsize=(7.5, 2.5))
    aggv = [['subj', ['reverb', 'voc_chan'][ix]],
            ['subj', ['gender', 'gap_len'][ix]],
            ['subj', 'attn']]
    gn = [['reverberation', 'talker gender', 'attention'],
          ['vocoder channels', 'gap length', 'attention']][ix]
    sg = [['***', '*', '***'], ['***', '', '*']][ix]
    br = [[(0, 1)], [[(0, 1)], None][ix], [(0, 1)]]
    for iix, (ax, aggvar, groupname, brack, signif) in \
            enumerate(zip(axs, aggv, gn, br, sg)):
        agg = longform[aggvar + hmfc]
        agg = agg.groupby(aggvar)
        agg = agg.aggregate(np.sum)
        agg['dprime'] = efa.dprime(agg[hmfc])
        dpr = agg['dprime'].unstack(0)
        if aggvar[-1] == 'voc_chan':
            dpr = dpr.sort_index(0, ascending=False)
        ax, bar = efa.barplot(dpr, err_bars='se', ax=ax, groups=[[0, 1]],
                              group_names=groupname, brackets=brack,
                              bracket_text=[signif], bracket_inline=True)
        _ = ax.set_ylim(0, 3.25)
        _ = ax.yaxis.set_ticks(range(0, 4))
        if iix:
            _ = ax.yaxis.set_visible(False)
            _ = ax.spines['left'].set_visible(False)
        else:
            _ = ax.yaxis.set_label_text('d-prime')
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.5, bottom=0.25)
    fname = ['reverb.svg', 'vocoder.svg'][ix]
    plt.savefig(fname)
