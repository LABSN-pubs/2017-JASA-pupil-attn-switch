# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'post-hoc-analyses.py'
===============================================================================

This script runs a few post-hoc analyses for the vocoder/switch-gap
and gender/reverb experiments.
"""
# @author: Dan McCloy  (drmccloy@uw.edu)
# Created on Wed Jan 13 16:40:10 2016
# License: BSD (3-clause)

from __future__ import division, print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
# import seaborn as sns
from os import path as op
import scipy.stats as ss
from scipy.special import logit
from expyfun import analyze as efa
from ast import literal_eval
from convenience_functions import use_font

# file I/O
work_dir = '..'
data_dir = 'data-behavioral'
rt_data_fnames = ['rev-behdata-xlongform.tsv', 'voc-behdata-xlongform.tsv']

# column selector shorthand
hmfc = ['hits', 'misses', 'false_alarms', 'corr_rej']
hmfc2 = ['hit', 'miss', 'fals', 'crej']

# plot params
pd.set_option('display.width', 160)
plt.ion()
use_font('mplus')


# functions
def read_data(data_fname, parse_presses=False):
    longform = pd.read_csv(op.join(work_dir, data_dir, data_fname), sep='\t')
    if parse_presses:
        longform['press_times'] = longform['press_times'].apply(literal_eval)
    return longform


def chsq_rt(x):
    # peak of chi squared distribution fit to data
    y = np.array(x).ravel()
    y = y[np.logical_not(np.isnan(y))]
    if y.size == 0:
        return np.nan
    else:
        return efa.rt_chisq(y)


def plot_hist_chsq(x, bins, ax, color, linsp, lcolor=None, histalpha=0.25,
                   label='', ltyp=(None, None), **kwargs):
    histcol = mplc.hex2color(color) + (histalpha,)
    if lcolor is None:
        lcolor = color
    ax.hist(x, bins, normed=True, color=histcol, histtype='stepfilled',
            **kwargs)
    df, loc, scale = ss.chi2.fit(x, floc=0)
    pdf = ss.chi2.pdf(linsp, df, scale=scale)
    l = ax.plot(linsp, pdf, color=lcolor, linewidth=2, label=label)
    l[0].set_dashes(ltyp)
    l[0].set_dash_capstyle('round')


# load data
longform_rev = read_data(rt_data_fnames[0])
longform_voc = read_data(rt_data_fnames[1])
datas = [longform_rev, longform_voc]
exps = ['reverb', 'vocoder']


# distribution of targets by slot
print('PERCENTAGE OF TARGETS BY TIMING SLOT')
for exp, data in zip(exps, datas):
    byslot = data.groupby(['slot']).aggregate(dict(targ=np.sum))
    print('  {} experiment:'.format(exp))
    print(byslot / byslot.sum(), end='\n\n')


# is RT difference localized by slot?
print('P-VALUES FOR REACTION TIME BY TIMING SLOT')
for exp, data, var in zip(exps, datas,
                          [['attn', 'reverb', 'gender'],
                           ['attn', 'voc_chan', 'gap_len']]):
    print('  {} experiment:'.format(exp))
    fig, axs = plt.subplots(1, 3, sharey=True)
    n_ttests = 12
    for main_eff, ax in zip(var, axs):
        nonans = data.dropna()
        gb = nonans.groupby(['slot', main_eff])
        n_resp = gb.agg(dict(reax_time=lambda x:
                             np.sum(np.logical_not(np.isnan(x)))))
        means = gb.agg(dict(reax_time=np.mean))
        stdev = gb.agg(dict(reax_time=np.std))
        print('    {}:'.format(main_eff))
        pvals = list()
        for slot in range(4):
            rts = list()
            conds = means.index.levels[1].values
            for cond in conds:
                reaxtimes = nonans.loc[(nonans['slot'] == slot) &
                                       (nonans[main_eff] == cond)]['reax_time']
                rts.append(reaxtimes)
            tval, pval = ss.ttest_ind(rts[0], rts[1], equal_var=False)
            pvals.append(pval)
            star = efa.format_pval(n_ttests * pval, False, 'stars')
            print('      slot {}: {:.6f} {}'.format(slot + 1, pval, star))
        # plot
        signifs = np.where(np.array(pvals) < 0.05 / n_ttests)[0]
        grps = [(0, 1), (2, 3), (4, 5), (6, 7)]
        brks = [tuple(x) for x in np.array(grps)[signifs]]
        strs = efa.format_pval(n_ttests * np.array(pvals), latex=False,
                               scheme='stars')[signifs]
        ax, bar = efa.barplot(means.values, err_bars=stdev.values, ax=ax,
                              groups=grps, brackets=brks, bracket_text=strs,
                              bar_names=conds.tolist() * 4,
                              group_names=['slot {}'.format(x + 1)
                                           for x in range(4)])
        _ = ax.set_title(main_eff)
    _ = fig.suptitle('{} experiment'.format(exp))
    if exp == 'vocoder':
        means = means.unstack()
        means['long-short'] = means.diff(axis=1)['reax_time']['short']
        print('\n{}'.format(means), end='\n\n')
print()


# distribution of reaction times for hits
bins = np.arange(0.1, 1., 0.025)
lsp = np.linspace(0.1, 1.1, 100)
fig, axs = plt.subplots(1, 2, figsize=(7, 3))
for exp, data, ax, col in zip(exps, datas, axs, ['#aa4499', '#44aa99']):
    hit_rts = data[data['targ'] & (data['reax_time'] > 0)]
    plot_hist_chsq(hit_rts['reax_time'].values, bins, ax, color=col,
                   linsp=lsp, edgecolor='none', label='rev_hits')
    _ = ax.set_title(exp)
    tk = np.linspace(0, 1.1, 12)
    _ = ax.set_xticks(tk)
    _ = ax.set_xticklabels([str(round(x, 1)) for x in tk],
                           fontdict=dict(size=8))


# is elevated pupil signal in switch condition just an artifact of more
# button presses in those trials?
print('DISTRIBUTION OF BUTTON PRESSES BY ATTENTIONAL CONDITION')
for exp, data in zip(exps, datas):
    presses = data.loc[data['press']].groupby(['attn']).count()['reax_time']
    targ_resps = data.loc[data['hit']].groupby(['attn']).count()['reax_time']
    foil_resps = data.loc[data['frsp']].groupby(['attn']).count()['reax_time']
    non_targ = presses - targ_resps
    non_targ_pct = non_targ / presses
    summary = pd.concat([presses, targ_resps, foil_resps, non_targ,
                         non_targ_pct], axis=1)
    summary.columns = ['all_presses', 'targ', 'foil', 'non_targ',
                       'non_targ_pct']
    summary['non_foil_fa'] = summary['non_targ'] - summary['foil']
    print('  {} experiment:'.format(exp))
    print(summary, end='\n\n')
# NO: there are actually more responses in the maintain condition.


# attn x foil response rate by slot
print('FOIL RESPONSE RATE x ATTENTIONAL CONDITION x SLOT')
print('(t-test applied to logit-transformed response rates)')
for exp, data in zip(exps, datas):
    foils = data.loc[data['foil']].groupby(['attn', 'slot']).count()
    foil_rate = (foils['reax_time'] / foils['trial']).unstack()
    print('  {} experiment:'.format(exp))
    print(foil_rate)
    # t-tests (maint vs switch) by slot, across subjects
    foils = data.loc[data['foil']].groupby(['attn', 'slot', 'subj']).count()
    foil_rate = (foils['reax_time'] / foils['trial']).unstack(1).unstack(0)
    foil_rate[foil_rate == 0] = 1e-12  # avoid -np.inf from logit transform
    foil_rate = logit(foil_rate)
    print('----------------------------------------------')
    print('p-val.', end='  ')
    for slot in range(4):
        tval, pval = ss.ttest_rel(foil_rate[slot]['maint.'],
                                  foil_rate[slot]['switch'])
        print('{:.6f}'.format(pval), end='  ')
    print('', end='\n\n')


# vocoder: 2-way targ detection interactions by slot
print('HIT RATE x SLOT FOR VOCODER EXPERIMENT')
n_ttests = 8
aggfuncs = dict(targ=np.sum, hit=np.sum)  # foil=np.sum, frsp=np.sum
level_dict = dict(gap_len=['long', 'short'], attn=['maint.', 'switch'],
                  voc_chan=[20, 10])
for interact in [['gap_len', 'voc_chan'], ['gap_len', 'attn']]:
    cols = ['slot'] + interact + ['subj']
    twoway = longform_voc.groupby(cols).agg(aggfuncs)
    twoway['hitrate'] = twoway['hit'] / twoway['targ']
    hr = twoway.unstack(0)['hitrate']
    # avoid np.inf after logit
    hr[hr == 1] = 1 - 1e-12
    hr[hr == 0] = 1e-12
    hr = logit(hr)
    first_diff = (hr.loc[level_dict[interact[0]][0]] -
                  hr.loc[level_dict[interact[0]][1]])
    tval, pval = ss.ttest_rel(first_diff.loc[level_dict[interact[1]][0]],
                              first_diff.loc[level_dict[interact[1]][1]])
    star = efa.format_pval(n_ttests * pval, False, 'stars')
    ix, iy = np.mgrid[0:2, 0:2]
    levs = [level_dict[interact[x]][y] for x, y in zip(ix.flat, iy.flat)]
    print('{} minus {}, {} vs {}'.format(*levs))
    for slot in range(4):
        print('  slot {}: {:.6f} {}'.format(slot + 1, pval[slot], star[slot]))
