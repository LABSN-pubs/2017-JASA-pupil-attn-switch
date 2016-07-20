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
import matplotlib.pyplot as plt
import seaborn as sns
from os import path as op
from expyfun import analyze as efa
from ast import literal_eval
from convenience_functions import use_font

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
use_font('source')
style_dict = {'ytick.major.size': 3, 'lines.solid_capstyle': 'butt',
              'axes.linewidth': thin, 'ytick.linewidth': thin}
sns.set_style('white', style_dict)
sns.set_context('paper')

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


def aggregate_df(df, aggvars, datavars=hmfc, diff=False):
    agg = df[aggvars + datavars]
    agg = agg.groupby(aggvars).aggregate(np.sum)
    agg['dprime'] = efa.dprime(agg[hmfc])
    df_wide = agg['dprime'].unstack()
    if 'voc_chan' in df_wide.columns.names:
        df_wide.rename(columns=lambda x: str(x), inplace=True)
        df_wide.sortlevel(axis=1, ascending=False, inplace=True)
    if diff:
        data = {'dprime': np.subtract(*df_wide.T.values),
                df_wide.columns.name: u' \u2212 '.join(df_wide.columns)}
        df_long = pd.DataFrame(data, index=df_wide.index)
        name = list(set(df_long.columns.tolist()) - set(['dprime']))
        df_wide = df_long.set_index(name, append=True, inplace=False)
        df_wide = df_wide.unstack(0).T
    df_long = pd.melt(df_wide, value_name='dprime',
                      value_vars=df_wide.columns.tolist())
    return (agg, df_wide, df_long)


def plot_main_effect(data_fname, contrast, xlabel, signif=None, diff=True,
                     fig=None, ax=None, despine_y=False):
    # load / parse / aggregate data  # hue=df_wide.columns.names[1]
    longform = read_data(data_fname)
    _, df_wide, df_long = aggregate_df(longform, contrast, diff=diff)
    data_kwargs = dict(x=df_wide.columns.names[0], y='dprime', data=df_long)
    # initialize figure
    fig = plt.figure(figsize=(1.25, 2.5)) if fig is None else fig
    ax = fig.add_subplot(111, top_margin=0.25) if ax is None else ax
    # must set axis lims before plotting (at least for swarmplot)
    yrange = np.array([-1.25, 1.5]) if diff else np.array([0, 5])
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
        yticks = range(-1, 2) if diff else range(0, 6)
        ax.yaxis.set_ticks(yticks)
        ax.yaxis.set_label_text(u'difference in d\u2032')
        ax.yaxis.labelpad = 1
        # draw line at zero across all 3 subplots
        xmax = fig.transFigure.transform([0.98, 0])
        xmax = ax.transAxes.inverted().transform(xmax)[0]
        ax.axhline(color='k', linewidth=thin, xmax=xmax, clip_on=False)
    ax.set_title(xlabel, y=1.1)
    ax.xaxis.set_label_text('')
    ax.xaxis.tick_top()
    return fig


def plot_twoway(data_fname, contrast, xlabel, signif=None, diff=True,
                fig=None, ax=None, despine_y=False):
    # load / parse / aggregate data  # hue=df_wide.columns.names[1]
    longform = read_data(data_fname)
    _, df_wide, df_long = aggregate_df(longform, contrast, diff=diff)
    data_kwargs = dict(x=df_long.index.names[-1], y='dprime', data=df_long)
    # initialize figure
    fig = plt.figure(figsize=(1.25, 2.5)) if fig is None else fig
    ax = fig.add_subplot(111, top_margin=0.25) if ax is None else ax
    # must set axis lims before plotting (at least for swarmplot)
    yrange = np.array([-1.25, 1.5]) if diff else np.array([0, 5])
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
        yticks = range(-1, 2) if diff else range(0, 6)
        ax.yaxis.set_ticks(yticks)
        ax.yaxis.set_label_text(u'difference in d\u2032')
        ax.yaxis.labelpad = 1
        # draw line at zero across all 3 subplots
        xmax = fig.transFigure.transform([0.98, 0])
        xmax = ax.transAxes.inverted().transform(xmax)[0]
        ax.axhline(color='k', linewidth=thin, xmax=xmax, clip_on=False)
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
    # init figure
    figname = 'fig-{}-main.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(top=0.8, right=0.98)
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = plot_main_effect(data_fname, contrast, groupname,  # signif,
                               diff=True, fig=fig, ax=ax, despine_y=ix)
    # finish
    if savefig:
        plt.savefig(figname)
    else:
        plt.ion()
        plt.show()


# setup subplot info for two-way interactions
all_contrasts = [[['subj', 'attn', 'reverb'],
                  ['subj', 'attn', 'gender'],
                  ['subj', 'reverb', 'gender']],
                 [['subj', 'attn', 'voc_chan'],
                  ['subj', 'attn', 'gap_len'],
                  ['subj', 'voc_chan', 'gap_len']]]
all_groupnames = [[u'attn. \u00D7 reverb.',
                   u'attn. \u00D7 gender',
                   u'reverb. \u00D7 gender'],
                  [u'attn. \u00D7 vocoder ch.',
                   u'attn. \u00D7 gap dur.',
                   u'vocoder ch. \u00D7 gap dur.']]
# all_signif = [['***', '**', '***'], ['*', '***', '***']]

# plot two-way interactions
for data_fname, contrasts, groupnames, signifs in \
        zip(data_fnames, all_contrasts, all_groupnames, all_signif):
    # init figure
    figname = 'fig-{}-twoway.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(top=0.8, right=0.98)
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = plot_main_effect(data_fname, contrast, groupname,  # signif,
                               diff=True, fig=fig, ax=ax, despine_y=ix)
    # finish
    if savefig:
        plt.savefig(figname)
    else:
        plt.ion()
        plt.show()
