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
from os import path as op
from expyfun import analyze as efa
from matplotlib import pyplot as plt
from ast import literal_eval
from convenience_functions import use_font

# flags
plt.ioff()
savefig = True
plot_type = 'swarm'  # box, strip, swarm

# file I/O
work_dir = '..'
data_dir = 'data-behavioral'
data_fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# plot styles
plt.rcdefaults()
use_font('source')
style_dict = {'ytick.major.size': 3, 'lines.solid_capstyle': 'butt'}
sns.set_style('white', style_dict)
sns.set_context('paper')

# plot params
qrtp = dict(color='none', facecolor='0.7')                    # quartile box
medp = dict(color='w', linewidth=1.5)                         # median line
whsp = dict(color='k', linestyle='solid')                     # whisker
sigp = dict(color='0.5', linewidth=0.8)                       # signif. bracket
ptsp = dict(size=4, color='0.2', linewidth=0.5,               # data points
            edgecolor='0.7')
boxp = dict(showcaps=False, showfliers=False, boxprops=qrtp, medianprops=medp)

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']


# functions
def aggregate_df(df, aggvars, datavars=hmfc):
    agg = df[aggvars + datavars]
    agg = agg.groupby(aggvars)
    agg = agg.aggregate(np.sum)
    agg['dprime'] = efa.dprime(agg[hmfc])
    dpr = agg['dprime'].unstack(0).T
    df = pd.melt(dpr, value_name='d-prime', value_vars=dpr.columns.tolist())
    return (agg, dpr, df)


def remove_legend(ax):
    try:
        ax.legend_.remove()
    except AttributeError:
        pass


# loop over experiments
for ix, data_fname in enumerate(data_fnames):
    longform = pd.read_csv(op.join(work_dir, data_dir, data_fname), sep='\t')
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
    contrasts = [main_eff, two_way]  # three_way
    # specify group names
    main_gr = [['reverberation', 'talker gender', 'attention'],
               ['vocoder channels', 'gap length', 'attention']][ix]
    two_way_gr = [[u'attention × reverberation', u'attention × gender',
                   u'reverberation × gender'],
                  [u'attention × vocoder channels', u'attention × gap length',
                   u'vocoder channels × gap length']][ix]
    three_way_gr = [[u'attn. × reverb × gender'],
                    [u'attn. × voc. chan. × gap len.']][ix]
    groupnames = [main_gr, two_way_gr]  # three_way_gr
    # specify significance (from mixed model LRTs)
    main_sig = [['**', '***', '***'], ['***', '***', '*']][ix]
    two_way_sig = [['', '', '**'], ['', '***', '***']][ix]
    three_way_sig = [[''], ['*']][ix]
    signifs = [main_sig, two_way_sig]  # three_way_sig
    # figure names
    fignames = [['fig-reverb-main.svg', 'fig-vocoder-main.svg'][ix],
                ['fig-reverb-twoway.svg', 'fig-vocoder-twoway.svg'][ix]]
                # ['fig-reverb-threeway.svg', 'fig-vocoder-threeway.svg'][ix]]
    for contrast, groupname, signif, figname \
            in zip(contrasts, groupnames, signifs, fignames):
        # initialize figure
        if len(contrast) > 1:
            fig, axs = plt.subplots(1, len(contrast), figsize=(7.5, 2.5),
                                    squeeze=False)
            axs = axs[0]  # only ever one row
            plt.subplots_adjust(wspace=0.5, bottom=0.25)
        else:
            fig, axs = [None], [None]
        # loop over subplots / contrasts
        for ax, agg, gn, sig in zip(axs, contrast, groupname, signif):
            # aggregate
            _, dpr, df = aggregate_df(longform, agg)
            # must set axis lims before plotting (at least for swarmplot)
            ylims = np.array([0, 5])
            bracket_offset = np.abs(np.diff(ylims)) / 20.
            try:
                ax.set_ylim(*(ylims + [0, 2.5 * bracket_offset]))
                ax.yaxis.set_ticks(range(0, 6))
            except AttributeError:
                pass
            # common args to the various plotting functions
            aggnames = list(dpr.columns.names)
            data_kwargs = dict(x=aggnames[0], y='d-prime', data=df)
            if len(aggnames) > 1:
                data_kwargs.update(dict(hue=aggnames[1]))
            wp = whsp if plot_type == 'box' else dict(linewidth=0)
            boxp.update(dict(whiskerprops=wp))
            # plot
            dk = data_kwargs.copy()
            dk.update(boxp)
            ax = sns.boxplot(ax=ax, **dk)
            data_kwargs.update(ptsp)
            if plot_type == 'strip':
                sns.stripplot(ax=ax, jitter=True, **data_kwargs)
            elif plot_type == 'swarm':
                sns.swarmplot(ax=ax, split=True, **data_kwargs)
            # garnishes
            remove_legend(ax)
            sns.despine()
            ax.xaxis.set_label_text(gn)
            # informative tick names
            ticknames = dpr.columns.tolist()
            if len(ticknames) > 2:
                tn = np.array(ticknames)
                ticknames = ['\n'.join(['   '.join(tn[:2, 1]), tn[0, 0]]),
                             '\n'.join(['   '.join(tn[2:, 1]), tn[2, 0]])]
            ax.xaxis.set_ticklabels(ticknames)
            # significance brackets
            _max = dpr.max().max()
            spine = np.tile(_max, 3) + np.array([1.2, 2, 2.2]) * bracket_offset
            if sig:
                ax.plot([0, 0], spine[:2], **sigp)
                ax.plot([1, 1], spine[:2], **sigp)
                ax.plot([0, 1], 2 * [spine[1]], **sigp)
                ax.annotate(sig, xy=(0.5, spine[2]), ha='center',
                            color=sigp['color'])

        plt.tight_layout()
        if savefig:
            plt.savefig(figname)
        else:
            plt.ion()
            plt.show()

"""
            if len(aggnames) > 2:
                dk.update(dict(col=aggnames[2]))
                grid = sns.factorplot(ax=ax, kind='box', **dk)
                fig = grid.fig
                data_kwargs.update(ptsp)
                for ax, (nix, data) in zip(grid.axes[0], grid.facet_data()):
                    data_kwargs.update(data=data)
                    sns.swarmplot(ax=ax, split=True, **data_kwargs)
                    remove_legend(ax)

"""
