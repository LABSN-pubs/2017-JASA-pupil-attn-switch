# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'plot-behavioral-data.py'
===============================================================================

This script cleans and analyzes behavioral data for the vocoder/switch-gap
and gender/reverb experiments.
"""
# @author: Dan McCloy  (drmccloy@uw.edu)
# Created on Wed Jan 13 16:40:10 2016
# License: BSD (3-clause)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from os import path as op
from expyfun import analyze as efa
from ast import literal_eval
from convenience_functions import use_font, sort_desc

# flags
plt.ioff()
savefig = True
plot_type = 'swarm'  # box, strip, swarm
notch = False

# file I/O
work_dir = '..'
data_dir = 'data-behavioral'
data_fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# plot styles
thin = 0.5
gray = '0.7'
plt.rcdefaults()
plt.rc('xtick', top=True)
style_dict = {'ytick.major.size': 3, 'lines.solid_capstyle': 'butt',
              'axes.linewidth': thin, 'ytick.linewidth': thin}
sns.set_style('white', style_dict)
sns.set_context('paper')
use_font('mplus')

# plot params
qrtp = dict(color='none', facecolor=gray)                     # quartile box
whsp = dict(color='k', linestyle='solid')                     # whisker
medp = dict(color='w', linewidth=1.5)                         # median line
sigp = dict(color='r', linewidth=0.8)                         # signif. bracket
ptsp = dict(size=4, color='k', linewidth=thin, edgecolor=gray)  # data pts
boxp = dict(showcaps=False, showfliers=False, boxprops=qrtp, medianprops=medp,
            width=0.4)
# hide whiskers if overplotting all data points
wp = whsp if plot_type == 'box' else dict(linewidth=0)
boxp.update(dict(whiskerprops=wp))
if notch:
    boxp.update(dict(notch=True, bootstrap=10000))


# functions
def read_data(data_fname):
    longform = pd.read_csv(op.join(work_dir, data_dir, data_fname), sep='\t')
    longform['press_times'] = longform['press_times'].apply(literal_eval)
    return longform


def _agg(df, aggvars, datavars):
    agg = df[aggvars + datavars]
    agg = agg.groupby(aggvars).aggregate(np.sum)
    agg['dprime'] = efa.dprime(agg[hmfc])
    if 'voc_chan' in agg.index.names:
        # convert int to str
        ix = agg.index.names.index('voc_chan')
        agg.index.set_levels(agg.index.levels[ix].astype(str), level=ix,
                             inplace=True)
        # sort voc_chan backwards
        agg = sort_desc(agg, 'voc_chan', axis=0)
    return agg


def aggregate_dprime(df, aggvars, datavars=hmfc, diff=None):
    agg = _agg(df, aggvars, datavars)['dprime']
    df_long = agg.reset_index([x for x in aggvars if x != 'subj'])
    df_wide = agg.unstack('subj').T
    if 'voc_chan' in df_wide.columns.names:
        df_wide = sort_desc(df_wide, 'voc_chan', axis=1)
    if diff is not None:
        df_diff = agg.unstack(diff)
        if diff == 'voc_chan':
            df_diff = sort_desc(df_diff, diff, axis=1)
        dpdiff = np.subtract(*df_diff.T.values)
        newname = u'\u2009\u2212\u2009'.join(df_diff.columns)
        columns = pd.Index([newname], name=df_diff.columns.name)
        df_wide = pd.DataFrame(dpdiff, index=df_diff.index, columns=columns)
        idvars = [x for x in df_diff.index.names if x != 'subj']
        idvals = df_diff.reset_index(idvars)
        datadict = {var: idvals[var] for var in idvars}
        datadict.update({'dprime': dpdiff, df_diff.columns.name: newname})
        df_long = pd.DataFrame(datadict, index=idvals.index)
        while len(df_wide.index.names) > 1:
            df_wide = df_wide.unstack()
    return df_wide, df_long


def box_and_swarm_plot(data, contrast, xlabel=None, signif=None,
                       diff=None, fig=None, ax=None, despine_y=False):
    # load / parse / aggregate data  # hue=df_wide.columns.names[1]
    df_wide, df_long = aggregate_dprime(data, contrast, diff=diff)
    data_kwargs = dict(x=df_wide.columns.names[-1], y='dprime', data=df_long)
    # initialize figure
    fig = plt.figure(figsize=(1.25, 2.5)) if fig is None else fig
    ax = fig.add_subplot(111, top_margin=0.25) if ax is None else ax
    # must set axis lims before plotting (at least for swarmplot)
    yrange = np.array([-2, 2]) if diff else np.array([0, 5])
    bracket_offset = np.abs(np.diff(yrange)) / 25.
    ax.set_ylim(*(yrange + [0, 2.5 * bracket_offset]))
    # plot underlying boxplot
    box_kwargs = data_kwargs.copy()
    box_kwargs.update(boxp)
    ax = sns.boxplot(ax=ax, **box_kwargs)
    # overplot data points
    overplot_kwargs = data_kwargs.copy()
    overplot_kwargs.update(ptsp)
    if plot_type == 'strip':
        sns.stripplot(ax=ax, jitter=True, **overplot_kwargs)
    elif plot_type == 'swarm':
        sns.swarmplot(ax=ax, split=True, **overplot_kwargs)
    # significance brackets
    _max = df_long['dprime'].max()
    brack = np.tile(_max, 3) + np.array([1.2, 2., 2.2]) * bracket_offset
    if signif:
        if not diff:
            ax.plot([0, 0], brack[:2], **sigp)
            ax.plot([1, 1], brack[:2], **sigp)
            ax.plot([0, 1], 2 * [brack[1]], **sigp)
        star_y = brack[0] if diff else brack[2]
        ax.annotate(signif, xy=(ax.xaxis.get_ticklocs().mean(), star_y),
                    ha='center', color=sigp['color'])
    # garnishes
    if despine_y:
        sns.despine(bottom=True, left=True, ax=ax)
        ax.yaxis.set_label_text('')
        ax.yaxis.set_ticks([])
    else:
        sns.despine(bottom=True, ax=ax)
        yticks = range(-2, 3) if diff else range(0, 6)
        ax.yaxis.set_ticks(yticks)
        ax.yaxis.set_label_text(u'within-subject difference in d\u2032')
        ax.yaxis.labelpad = 2
        # draw line at zero across all 3 subplots
        xmax = fig.transFigure.transform([0.98, 0])
        xmax = ax.transAxes.inverted().transform(xmax)[0]
        ax.axhline(color='k', linewidth=thin, xmax=xmax, clip_on=False)
    if xlabel is None:
        ix = df_wide.columns.names.index(diff)
        xlabel = df_wide.columns.levels[ix][0]
    ax.set_title(xlabel, y=1.1)
    ax.xaxis.set_label_text('')
    ax.xaxis.tick_top()
    return fig


# setup subplot info for main effects
all_contrasts = [[['subj', 'attn'], ['subj', 'reverb'], ['subj', 'gender']],
                 [['subj', 'attn'], ['subj', 'voc_chan'], ['subj', 'gap_len']]]
all_groupnames = [['attention', 'reverberation', 'talker genders'],
                  ['attention', 'vocoder channels', 'gap duration']]
all_signif = [['***', '**', '***'], ['*', '***', '***']]

# plot main effects
for data_fname, contrasts, groupnames, signifs in \
        zip(data_fnames, all_contrasts, all_groupnames, all_signif):
    # load data
    data = read_data(data_fname)
    # init figure
    figname = 'fig-{}-main.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(top=0.8, right=0.98)
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, groupname, signif,
                                 diff=contrast[-1], fig=fig, ax=ax,
                                 despine_y=ix)
    # finish
    if savefig:
        plt.savefig(figname)
    else:
        plt.ion()
        plt.show()


# setup subplot info for two-way interactions
all_contrasts = [[['subj', 'attn', 'reverb'],
                  ['subj', 'reverb', 'gender'],
                  ['subj', 'gender', 'attn']],
                 [['subj', 'attn', 'voc_chan'],
                  ['subj', 'voc_chan', 'gap_len'],
                  ['subj', 'gap_len', 'attn']]]
#all_groupnames = [[u'attn.\u2009\u00D7\u2009revb.',
#                   u'attn.\u2009\u00D7\u2009gend.',
#                   u'revb.\u2009\u00D7\u2009gend.'],
#                  [u'attn.\u2009\u00D7\u2009voc.ch.',
#                   u'attn.\u2009\u00D7\u2009gap dur.',
#                   u'voc.ch.\u2009\u00D7\u2009gap dur.']]
all_signif = [['', '**', ''], ['', '***', '***']]
boxp.update(dict(width=0.6))

# plot two-way interactions
for data_fname, contrasts, groupnames, signifs in \
        zip(data_fnames, all_contrasts, all_groupnames, all_signif):
    # load data
    data = read_data(data_fname)
    # init figure
    figname = 'fig-{}-twoway.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(top=0.8, right=0.98)
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, signif=signif,  # groupname
                                 diff=contrast[1], fig=fig, ax=ax,
                                 despine_y=ix)
    # finish
    if savefig:
        plt.savefig(figname)
    else:
        plt.ion()
        plt.show()
