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
from convenience_functions import use_font

# flags
plt.ioff()
savefig = False
plot_type = 'swarm'  # box, bar, strip, violin, swarm

# file I/O
work_dir = getcwd()
data_dir = 'data-behavioral'
fig_dir = 'figures'
fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# rcparams
use_font('source')
#rcp = {'font.sans-serif': ['M+ 1c'], 'font.style': 'normal',
#       'font.size': 14, 'font.variant': 'normal', 'font.weight': 'medium',
#       'pdf.fonttype': 42, 'xtick.top': False, 'ytick.right': False}
plt.rcdefaults()
#rcParams.update(rcp)
style_dict = {'ytick.major.size': 3, 'lines.solid_capstyle': u'butt'}
sns.set_style("white", style_dict)

# plot params
boxp = dict(color='none', facecolor='0.7')
medp = dict(color='w', linewidth=1.5)
whsp = dict(color='k', linestyle='solid')
flyp = dict(color='0.5', markeredgecolor='none', marker='.')
sigp = dict(color='k', linewidth=0.8)

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# loop over experiments
for ix, fname in enumerate(fnames):
    longform = pd.read_csv(op.join(data_dir, fname), sep='\t')
    longform['press_times'] = longform['press_times'].apply(literal_eval)
    # specify contrasts
    main_eff = [['subj', ['reverb', 'voc_chan'][ix]],
                ['subj', ['gender', 'gap_len'][ix]],
                ['subj', 'attn']]
    two_way = [['subj', 'attn', ['reverb', 'voc_chan'][ix]],
               ['subj', 'attn', ['gender', 'gap_len'][ix]],
               ['subj', ['reverb', 'voc_chan'][ix], ['gender', 'gap_len'][ix]]]
    three_way = [['subj', 'attn', ['reverb', 'voc_chan'][ix],
                  ['gender', 'gap_len'][ix]]]
    contrasts = main_eff + two_way + three_way
    # specify group names
    main_gr = [['reverberation', 'talker gender', 'attention'],
               ['vocoder channels', 'gap length', 'attention']][ix]
    two_way_gr = [[u'attn. × reverb', u'attn. × gender', u'reverb × gender'],
                  [u'attn. × voc. chan.', u'attn. × gap len.',
                   u'voc. chan. × gap len.']][ix]
    three_way_gr = [[u'attn. × reverb × gender'],
                    [u'attn. × voc. chan. × gap len.']][ix]
    groupnames = main_gr + two_way_gr + three_way_gr
    # specify significance (from mixed model LRTs)
    main_sig = [['**', '***', '***'], ['***', '***', '*']][ix]
    two_way_sig = [['', '', '**'], ['', '***', '***']][ix]
    three_way_sig = [[''], ['*']][ix]
    # brackets
    br = [[(0, 1)], [[(0, 1)], None][ix], [(0, 1)]]
    # initialize figure
    fig, axs = plt.subplots(1, 3, figsize=(7.5, 2.5))
    plt.subplots_adjust(wspace=0.5, bottom=0.25)
    # loop over contrasts / garnishes
    for iix, (ax, aggvar, groupname, brack, signif) in \
            enumerate(zip(axs, main_eff, main_gr, br, main_sig)):
        stars = list()
        agg = longform[aggvar + hmfc]
        agg = agg.groupby(aggvar)
        agg = agg.aggregate(np.sum)
        agg['dprime'] = efa.dprime(agg[hmfc])
        dpr = agg['dprime'].unstack(0).T
        if aggvar[-1] == 'voc_chan':
            dpr = dpr.sort_index(0, ascending=False)
        df = pd.melt(dpr, value_name='d-prime',
                     value_vars=dpr.columns.tolist())
        # plot
        if plot_type == 'bar':
            ax, bar = efa.barplot(dpr, err_bars='se', ax=ax, groups=[[0, 1]],
                                  group_names=groupname, brackets=brack,
                                  bracket_text=[signif], bracket_inline=False)
            ax.set_ylim(0, 3.25)
            ax.yaxis.set_ticks(range(0, 4))
        else:
            # must set axis lims before plotting (at least for swarmplot)
            sns.set_context('paper')
            ylims = np.array([0, 5])
            bracket_offset = np.abs(np.diff(ylims)) / 20.
            ax.set_ylim(*(ylims + [0, 2 * bracket_offset]))
            ax.yaxis.set_ticks(range(0, 6))
            data_kwargs = dict(x=dpr.columns.name, y='d-prime', data=df)
            if plot_type == 'violin':
                sns.violinplot(ax=ax, inner='point', bw=0.5, cut=0.5,
                               linewidth=1, **data_kwargs)
            else:
                wp = whsp if plot_type == 'box' else dict(linewidth=0)
                ax = sns.boxplot(ax=ax, showcaps=False, showfliers=False,
                                 boxprops=boxp, medianprops=medp,
                                 whiskerprops=wp, **data_kwargs)
                if plot_type == 'strip':
                    ax = sns.stripplot(ax=ax, jitter=True, size=3,  color='k',
                                       linewidth=0, **data_kwargs)
                elif plot_type == 'swarm':
                    ax = sns.swarmplot(ax=ax, size=4, color='0.2',
                                       linewidth=0.5, edgecolor='0.7',
                                       **data_kwargs)
            # garnishes
            sns.despine()
            ax.xaxis.set_label_text(groupname)
            ax.xaxis.set_ticklabels(dpr.columns.tolist())
            # significance brackets
            _max = dpr.max().max()
            spine = np.array(3 * [_max]) + np.array([1.2, 2, 2.2]) * bracket_offset
            if signif:
                ax.plot([0, 0], spine[:2], **sigp)
                ax.plot([1, 1], spine[:2], **sigp)
                ax.plot([0, 1], 2 * [spine[1]], **sigp)
                star = ax.annotate(signif, xy=(0.5, spine[2]), ha='center')
            stars.append(star)

    plt.tight_layout()
    if savefig:
        fname = ['reverb_beh.svg', 'vocoder_beh.svg'][ix]
        plt.savefig(op.join(fig_dir, fname))
    else:
        plt.ion()
        plt.show()
