# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'fig-behavioral.py'
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
import svgutils as svgu
from os import path as op
from scipy.stats import ttest_1samp, ttest_rel
from expyfun import analyze as efa
from ast import literal_eval
from convenience_functions import use_font, sort_desc

# flags
plt.ioff()
savefig = True
plot_type = 'swarm'  # box, strip, swarm
notch = False
ttest = False

# file I/O
work_dir = '..'
data_dir = 'data-behavioral'
data_fnames = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv']
rt_data_fnames = ['rev-behdata-xlongform.tsv', 'voc-behdata-xlongform.tsv']

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']

# plot styles
thin = 0.5
plt.rcdefaults()
plt.rc('xtick', top=True)
style_dict = {'ytick.major.size': 3, 'lines.solid_capstyle': 'butt',
              'axes.linewidth': thin, 'ytick.linewidth': thin}
sns.set_style('white', style_dict)
sns.set_context('paper')
use_font('mplus')

# plot params
qrtp = dict(color='none', facecolor='0.7')                    # quartile box
whsp = dict(color='k', linestyle='solid')                     # whisker
medp = dict(color='w', linewidth=1.6)                         # median line
sigp = dict(color='r', linewidth=0.8)                         # signif. bracket
ptsp = dict(size=4, color='k', linewidth=thin, edgecolor='0.5')  # data pts
boxp = dict(showcaps=False, showfliers=False, boxprops=qrtp, medianprops=medp,
            width=0.5)
# hide whiskers if overplotting all data points
wp = whsp if plot_type == 'box' else dict(linewidth=0)
boxp.update(dict(whiskerprops=wp))
if notch:
    boxp.update(dict(notch=True, bootstrap=10000))
# things we want consistent across plots
axis_lab_dp = u'within-subject difference in d\u2032'
axis_lab_rt = u'within-subject difference in RT (ms)'
ylim_dp = np.array([-2, 2])  # np.array([0, 5]) if not doing differences
ytick_dp = range(ylim_dp[0], ylim_dp[1] + 1)
ylim_rt = np.array([[-0.21, 0.11], [-0.32, 0.12]])
ytick_rt = [np.linspace(-0.2, 0.1, 4), np.linspace(-0.3, 0.1, 5)]
exts_dp = dict(bottom=0.1, top=0.8, right=0.98)
exts_rt = dict(bottom=0.1, top=0.8, right=0.98, left=0.153)
exts_dp_threeway = dict(bottom=0.1, top=0.8, right=0.88)
exts_rt_threeway = dict(bottom=0.1, top=0.8, right=0.88, left=0.153)


# functions
def read_data(data_fname, parse_presses=True):
    longform = pd.read_csv(op.join(work_dir, data_dir, data_fname), sep='\t')
    if parse_presses:
        longform['press_times'] = longform['press_times'].apply(literal_eval)
    return longform


def _agg(data, aggvars, datavars, aggfunc):
    agg = data[aggvars + datavars]
    if datavars == ['reax_time', 'targ']:
        agg = agg[~np.isnan(data['reax_time']) & data['targ']]
    agg = agg.groupby(aggvars).aggregate(aggfunc)
    if datavars == hmfc:
        agg['dprime'] = efa.dprime(agg[hmfc])
    if 'voc_chan' in agg.index.names:
        # convert int to str
        ix = agg.index.names.index('voc_chan')
        agg.index.set_levels(agg.index.levels[ix].astype(str), level=ix,
                             inplace=True)
        # sort voc_chan backwards
        agg = sort_desc(agg, 'voc_chan', axis=0)
    return agg


def _make_wide_and_long(agg, aggvars, diff, datalabel):
    df_long = agg.reset_index([x for x in aggvars if x != 'subj'])
    df_wide = agg.unstack('subj').T
    if 'voc_chan' in df_wide.columns.names:
        df_wide = sort_desc(df_wide, 'voc_chan', axis=1)
    if diff is not None:
        df_diff = agg.unstack(diff)
        if diff == 'voc_chan':
            df_diff = sort_desc(df_diff, diff, axis=1)
        diffarray = np.subtract(*df_diff.T.values)
        newname = u'\u2009\u2212\u2009'.join(df_diff.columns)
        columns = pd.Index([newname], name=df_diff.columns.name)
        df_wide = pd.DataFrame(diffarray, index=df_diff.index, columns=columns)
        idvars = [x for x in df_diff.index.names if x != 'subj']
        idvals = df_diff.reset_index(idvars)
        datadict = {var: idvals[var] for var in idvars}
        datadict.update({datalabel: diffarray, df_diff.columns.name: newname})
        df_long = pd.DataFrame(datadict, index=idvals.index)
        while len(df_wide.index.names) > 1:
            df_wide = df_wide.unstack()
    return df_wide, df_long


def agg_dprime(data, aggvars, datavars=hmfc, datalabel='dprime', diff=None):
    agg = _agg(data, aggvars, datavars, np.sum)[datalabel]
    df_wide, df_long = _make_wide_and_long(agg, aggvars, diff, datalabel)
    return df_wide, df_long


def agg_rt(data, aggvars, datavars=['reax_time', 'targ'],
           datalabel='reax_time', diff=None):
    agg = _agg(data, aggvars, datavars, efa.rt_chisq)[datalabel]
    df_wide, df_long = _make_wide_and_long(agg, aggvars, diff, datalabel)
    return df_wide, df_long


def box_and_swarm_plot(data, contrast, aggfunc, datalabel, xlabel=None,
                       ylabel=None, signif=[], diff=None, fig=None, hue=None,
                       ax=None, despine_y=False, ylim=None, ytick=None,
                       sec_to_ms=False):
    # load / parse / aggregate data  # hue=df_wide.columns.names[1]
    df_wide, df_long = aggfunc(data, contrast, diff=diff, datalabel=datalabel)
    data_kwargs = dict(x=df_wide.columns.names[-1], y=datalabel, hue=hue,
                       data=df_long)
    # initialize figure
    fig = plt.figure(figsize=(1.25, 2.5)) if fig is None else fig
    ax = fig.add_subplot(111, top_margin=0.25) if ax is None else ax
    # must set axis lims before plotting (at least for swarmplot)
    bracket_offset = (0. if signif is None and not ttest else
                      np.abs(np.diff(ylim)) / 25.)
    ax.set_ylim(*(ylim + [0, 2.5 * bracket_offset]))
    # plot underlying boxplot
    box_kwargs = data_kwargs.copy()
    box_kwargs.update(boxp)
    ax = sns.boxplot(ax=ax, **box_kwargs)
    # overplot data points
    overplot_kwargs = data_kwargs.copy()
    overplot_kwargs.update(ptsp)
    if hue is not None:
        overplot_kwargs.update(dict(palette=['0.8', '0.2']))
    if plot_type == 'strip':
        ax = sns.stripplot(ax=ax, jitter=True, **overplot_kwargs)
    elif plot_type == 'swarm':
        ax = sns.swarmplot(ax=ax, split=True, **overplot_kwargs)
    # handle legends
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles[2:], labels[2:], bbox_to_anchor=(0.88, 1), loc=2,
               borderaxespad=0.)
    # calc significance (if not provided manually)
    if ttest:
        if df_wide.shape[1] == 1:
            tval, pval = ttest_1samp(df_wide.values, 0)
        elif df_wide.shape[1] == 2:
            tval, pval = ttest_rel(*df_wide.T.values)
        elif diff:
            # 3-way interaction with diff
            _df = df_long.set_index(contrast[1:], append=True)
            _ix = _df.index.names.index(contrast[-2])
            _lv = _df.index.levels[_ix]
            vals = [df_wide.xs(lev, axis=1, level=_ix).values for lev in _lv]
            tval, pval = ttest_rel(*np.array(vals).T)
        else:
            # 2-way interaction w/o diff
            _df = df_long.set_index(contrast[1:], append=True).unstack()
            tval, pval = ttest_rel(*_df.T.values)
        signif = efa.format_pval(pval, latex=False, scheme='stars')
    # draw significance brackets
    signif = np.atleast_1d(signif)
    _max = df_long[datalabel].max()
    brack = np.tile(_max, 3) + np.array([1.2, 2., 2.2]) * bracket_offset
    for _ix, _s in enumerate(signif):
        if _s:
            star_y = brack[0]
            star_x = (ax.xaxis.get_ticklocs().mean() if data_kwargs['hue']
                      is None else ax.xaxis.get_ticklocs()[_ix])
            brac_x = (0.5 if data_kwargs['hue'] is None else
                      boxp['width'] / 4.)
            if len(contrast) > 2 or not diff:
                _l = star_x - brac_x
                _r = star_x + brac_x
                ax.plot([_l, _l], brack[:2], **sigp)
                ax.plot([_r, _r], brack[:2], **sigp)
                ax.plot([_l, _r], 2 * [brack[1]], **sigp)
                star_y = brack[2]
            ax.annotate(_s, xy=(star_x, star_y), ha='center',
                        color=sigp['color'])
    # garnishes
    if despine_y:
        sns.despine(bottom=True, left=True, ax=ax)
        ax.yaxis.set_label_text('')
        ax.yaxis.set_ticks([])
    else:
        sns.despine(bottom=True, ax=ax)
        ax.yaxis.set_ticks(ytick)
        if sec_to_ms:
            ax.yaxis.set_ticklabels([int(np.round(1000 * x, 0)) for x in
                                     ytick])
        ax.yaxis.set_label_text(ylabel)
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
all_rt_signif = [['*', '**', '***'], ['', '**', '***']]

# plot main effects
for (data_fname, rt_data_fname, contrasts, groupnames, signifs, rt_signifs,
     rty, rtcky) in zip(data_fnames, rt_data_fnames, all_contrasts,
                        all_groupnames, all_signif, all_rt_signif, ylim_rt,
                        ytick_rt):
    # init figure
    figname = 'fig-{}-main.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(**exts_dp)
    # load beh data
    data = read_data(data_fname)
    ylab = axis_lab_dp
    ylim = ylim_dp
    ytick = ytick_dp
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='dprime',
                                 xlabel=groupname, ylabel=ylab,
                                 diff=contrast[-1], fig=fig, signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_dprime,
                                 ylim=ylim, ytick=ytick)
    # savefig
    if savefig:
        plt.savefig(figname)

    # init RT figure
    figname = 'fig-{}-main-rt.svg'.format(rt_data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(**exts_rt)
    # load RT data
    data = read_data(rt_data_fname, False)
    ylab = axis_lab_rt
    ylim = rty
    ytick = rtcky
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, rt_signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='reax_time',
                                 xlabel=groupname, ylabel=ylab,
                                 diff=contrast[-1], fig=fig, signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_rt,
                                 ylim=ylim, ytick=ytick, sec_to_ms=True)
    # savefig
    if savefig:
        plt.savefig(figname)


# setup subplot info for two-way interactions
all_contrasts = [[['subj', 'attn', 'reverb'],
                  ['subj', 'reverb', 'gender'],
                  ['subj', 'gender', 'attn']],
                 [['subj', 'attn', 'voc_chan'],
                  ['subj', 'gap_len', 'voc_chan'],
                  ['subj', 'gap_len', 'attn']]]
all_groupnames = [[u'attn.\u2009\u00D7\u2009revb.',
                   u'attn.\u2009\u00D7\u2009gend.',
                   u'revb.\u2009\u00D7\u2009gend.'],
                  [u'attn.\u2009\u00D7\u2009voc.ch.',
                   u'attn.\u2009\u00D7\u2009gap dur.',
                   u'voc.ch.\u2009\u00D7\u2009gap dur.']]
all_signif = [['', '**', ''], ['', '***', '***']]
all_rt_signif = [['', '', ''], ['', '', '']]
boxp.update(dict(width=0.7))

# plot two-way interactions
for (data_fname, rt_data_fname, contrasts, groupnames, signifs, rt_signifs,
     rty, rtcky) in zip(data_fnames, rt_data_fnames, all_contrasts,
                        all_groupnames, all_signif, all_rt_signif, ylim_rt,
                        ytick_rt):
    # init figure
    figname = 'fig-{}-twoway.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(**exts_dp)
    # load data
    data = read_data(data_fname)
    ylab = axis_lab_dp
    ylim = ylim_dp
    ytick = ytick_dp
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='dprime',
                                 ylabel=ylab,  # xlabel=groupname,
                                 diff=contrast[1], fig=fig, signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_dprime,
                                 ylim=ylim, ytick=ytick)
    # savefig
    if savefig:
        plt.savefig(figname)
    # init RT figure
    figname = 'fig-{}-twoway-rt.svg'.format(rt_data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    plt.subplots_adjust(**exts_rt)
    # load RT data
    data = read_data(rt_data_fname, False)
    ylab = axis_lab_rt
    ylim = rty
    ytick = rtcky
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, rt_signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='reax_time',
                                 ylabel=ylab,  # xlabel=groupname,
                                 diff=contrast[1], fig=fig,  # signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_rt,
                                 ylim=ylim, ytick=ytick, sec_to_ms=True)
    # savefig
    if savefig:
        plt.savefig(figname)

# setup subplot info for three-way interactions
all_contrasts = [[['subj', 'gender', 'attn', 'reverb']],
                 [['subj', 'gap_len', 'voc_chan', 'attn']]]
all_groupnames = [[u'\u2009\u00D7\u2009'.join(['attn.', 'revb.', 'gend.'])],
                  [u'\u2009\u00D7\u2009'.join(['attn.', 'voc.ch.',
                                               'gap dur.'])]]
all_signif = [[''], ['*']]
all_rt_signif = [[''], ['']]
boxp.update(dict(width=0.8))

# plot three-way interactions
for (data_fname, rt_data_fname, contrasts, groupnames, signifs, rt_signifs,
     rty, rtcky) in zip(data_fnames, rt_data_fnames, all_contrasts,
                        all_groupnames, all_signif, all_rt_signif, ylim_rt,
                        ytick_rt):
    # init figure
    figname = 'fig-{}-threeway.svg'.format(data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    axs = np.atleast_1d(axs)
    plt.subplots_adjust(**exts_dp_threeway)
    # load data
    data = read_data(data_fname)
    ylab = axis_lab_dp
    ylim = ylim_dp
    ytick = ytick_dp
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='dprime',
                                 ylabel=ylab,  # xlabel=groupname,
                                 diff=contrast[1], fig=fig, signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_dprime,
                                 ylim=ylim, ytick=ytick, hue=contrast[-1])
    # savefig
    if savefig:
        plt.savefig(figname)
    # init RT figure
    figname = 'fig-{}-threeway-rt.svg'.format(rt_data_fname[:3])
    fig, axs = plt.subplots(1, len(contrasts), figsize=(3.5, 2.5))
    axs = np.atleast_1d(axs)
    plt.subplots_adjust(**exts_rt_threeway)
    # load RT data
    data = read_data(rt_data_fname, False)
    ylab = axis_lab_rt
    ylim = rty
    ytick = rtcky
    # iterate over (sub)plots
    for ix, (contrast, groupname, signif, ax) in \
            enumerate(zip(contrasts, groupnames, rt_signifs, axs)):
        ax.patch.set_alpha(0)
        fig = box_and_swarm_plot(data, contrast, datalabel='reax_time',
                                 ylabel=ylab,  # xlabel=groupname,
                                 diff=contrast[1], fig=fig, signif=signif,
                                 ax=ax, despine_y=ix, aggfunc=agg_rt,
                                 ylim=ylim, ytick=ytick, hue=contrast[-1],
                                 sec_to_ms=True)
    # savefig
    if savefig:
        plt.savefig(figname)

# combine figs
if savefig:
    for exp in ['voc', 'rev']:
        for rt in ['', '-rt']:
            fig = svgu.transform.SVGFigure('3in', '5.75in')
            for kind, ypos, txt in zip(['main', 'twoway', 'threeway'],
                                       [0, 175, 350], ['a)', 'b)', 'c)']):
                fname = 'fig-{}-{}{}.svg'.format(exp, kind, rt)
                subfig = svgu.transform.fromfile(fname).getroot()
                subfig.moveto(10, ypos, scale=3/3.2)
                args = dict(size=12, font='Source Sans Pro', weight='normal')
                text = svgu.transform.TextElement(4, ypos + 12, txt, **args)
                fig.append(subfig)
                fig.append(text)
            fig.save('fig-beh-{}{}.svg'.format(exp, rt))
else:
    plt.ion()
    plt.show()
