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
import seaborn as sns
from os import getcwd
from os import path as op
from expyfun import analyze as efa
from matplotlib import rcParams
from matplotlib import pyplot as plt
# from matplotlib.colors import colorConverter as cc
from ast import literal_eval


# flags
plt.ioff()
savefig = False
plot_type = 'strip'  # box, bar, strip, violin

# file I/O
work_dir = getcwd()
data_dir = 'data-behavioral'
fig_dir = 'figures'
fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# rcparams
rcp = {'font.sans-serif': ['M+ 1c'], 'font.style': 'normal',
       'font.size': 14, 'font.variant': 'normal', 'font.weight': 'medium',
       'pdf.fonttype': 42, 'xtick.top': False, 'ytick.right': False}
plt.rcdefaults()
rcParams.update(rcp)
sns.set_style("white", {'ytick.major.size': 3})

# plot params
bp = dict(color='none', facecolor='0.7')
mp = dict(color='w', linewidth=1.5)
wp = dict(color='k', linestyle='solid')
fp = dict(color='0.5', markeredgecolor='none', marker='.')

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# loop over experiments
for ix, fname in enumerate(fnames):
    aggvars = ['subj', 'attn', ['reverb', 'voc_chan'][ix],
               ['gender', 'gap_len'][ix]]
    longform = pd.read_csv(op.join(data_dir, fname), sep='\t')
    longform['press_times'] = longform['press_times'].apply(literal_eval)
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
        df = pd.melt(dpr.T, value_vars=dpr.index.tolist(),
                     value_name='d-prime')
        if plot_type in ['box', 'strip']:
            wp2 = wp if plot_type == 'box' else dict(linewidth=0)
            ax = sns.boxplot(x=dpr.index.name, y='d-prime', data=df,
                             ax=ax, showcaps=False, showfliers=False,
                             boxprops=bp, medianprops=mp, whiskerprops=wp2)
            if plot_type == 'strip':
                ax = sns.stripplot(x=dpr.index.name, y='d-prime', data=df,
                                   jitter=True, size=3, color='k', linewidth=0,
                                   ax=ax)
        elif plot_type == 'violin':
            sns.violinplot(x=dpr.index.name, y='d-prime', data=df,
                           palette="Set3", bw=0.5, cut=0.5,
                           linewidth=1, ax=ax, inner='point')
        if plot_type in ['box', 'strip', 'violin']:
            ax.xaxis.set_label_text(groupname)
            ax.xaxis.set_ticklabels(dpr.index.tolist())
            ax.set_ylim(0, 5)
            ax.yaxis.set_ticks(range(0, 6))
            sns.despine()
        else:
            ax, bar = efa.barplot(dpr, err_bars='se', ax=ax, groups=[[0, 1]],
                                  group_names=groupname, brackets=brack,
                                  bracket_text=[signif], bracket_inline=False)
            ax.set_ylim(0, 3.25)
            ax.yaxis.set_ticks(range(0, 4))
        if iix:
            pass
            #ax.yaxis.set_visible(False)
            #ax.spines['left'].set_visible(False)
        else:
            ax.yaxis.set_label_text('d-prime')
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.5, bottom=0.25)
    if savefig:
        fname = ['reverb_beh.svg', 'vocoder_beh.svg'][ix]
        plt.savefig(op.join(fig_dir, fname))
    else:
        plt.ion()
        plt.show()
