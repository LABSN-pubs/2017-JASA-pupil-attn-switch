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
data_dir = 'data-behavioral'
work_dir = getcwd()
fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# rcparams
rcp = {'font.sans-serif': ['M+ 1c'], 'font.style': 'normal',
       'font.size': 14, 'font.variant': 'normal', 'font.weight': 'medium',
       'pdf.fonttype': 42}
plt.rcdefaults()
rcParams.update(rcp)

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
    fig, axs = plt.subplots(3, 1, figsize=(2.5, 5.5))
    aggv = [['subj', ['reverb', 'voc_chan'][ix]],
            ['subj', ['gender', 'gap_len'][ix]],
            ['subj', 'attn']]
    gn = [['reverberation', 'talker gender', 'attention'],
          ['vocoder channels', 'gap length', 'attention']][ix]
    sg = [['***', '*', '***'], ['***', '', '*']][ix]
    br = [[(0, 1)], [[(0, 1)], None][ix], [(0, 1)]]
    for ax, aggvar, groupname, brack, signif in zip(axs, aggv, gn, br, sg):
        agg = longform[aggvar + hmfc]
        agg = agg.groupby(aggvar)
        agg = agg.aggregate(np.sum)
        agg['dprime'] = efa.dprime(agg[hmfc])
        dpr = agg['dprime'].unstack(0)
        ax, bar = efa.barplot(dpr, err_bars='se', ax=ax, groups=[[0, 1]],
                              group_names=groupname, brackets=brack,
                              bracket_text=[signif], bracket_inline=True)
        _ = ax.set_ylim(0, 3.25)
        _ = ax.yaxis.set_ticks(range(0, 4))
        _ = ax.yaxis.set_label_text('d-prime')
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.6, bottom=0.1)
    fname = ['reverb.svg', 'vocoder.svg'][ix]
    plt.savefig(fname)

"""
# main effect of gender / gap length
aggv = ['subj', ['gender', 'gap_len'][ix]]
agg_attn = longform[aggv + hmfc]
agg_attn = agg_attn.groupby(aggv)
agg_attn = agg_attn.aggregate(np.sum)
agg_attn['dprime'] = efa.dprime(agg_attn[hmfc])
dp_attn = agg_attn['dprime'].unstack(0)
ax, bar = efa.barplot(dp_attn, err_bars='se',
                      bar_names=['maintain', 'switch'])

# main effect of attention
aggv = ['subj', 'attn']
agg_attn = longform[aggv + hmfc]
agg_attn = agg_attn.groupby(aggv)
agg_attn = agg_attn.aggregate(np.sum)
agg_attn['dprime'] = efa.dprime(agg_attn[hmfc])
dp_attn = agg_attn['dprime'].unstack(0)
ax, bar = efa.barplot(dp_attn, err_bars='se',
                      bar_names=['maintain', 'switch'])
agg = longform[aggvars + hmfc]
agg = agg.groupby(aggvars)
agg = agg.aggregate(np.sum)
agg['dprime'] = efa.dprime(agg[hmfc])
dpmat = agg['dprime'].unstack(0)
gr = [[0, 1], [2, 3], [4, 5], [6, 7]]

bar_names = 4 * [['MF', 'MM'], ['long', 'short']][ix]
gr1_names = 2 * [['anechoic', 'reverberant'],
                 ['10 channel', '20 channel']][ix]
gr2_names = ['maintain', 'switch']
ax, bar = efa.barplot(dpmat, err_bars='se', groups=gr,
                             bar_names=bar_names, group_names=gr1_names)

_ = ax.yaxis.set_label_text('d-prime')
gr2_x = np.mean([[bar.patches[1].xy[0] + bar.patches[1].get_width(),
                  bar.patches[2].xy[0]],
                 [bar.patches[5].xy[0] + bar.patches[5].get_width(),
                  bar.patches[6].xy[0]]], axis=-1)
_ = [ax.text(x, -0.45, name, ha='center')
     for name, x in zip(gr2_names, gr2_x)]
#_ = ax.yaxis.set_tick_params('major', labelsize=12)
"""
