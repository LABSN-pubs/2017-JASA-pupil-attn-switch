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
plt.ioff()
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


def plot_hist_chsq(x, bins, fig, color, linsp, lcolor=None, histalpha=0.25,
                   label='', ltyp=(None, None), **kwargs):
    histcol = mplc.hex2color(color) + (histalpha,)
    if lcolor is None:
        lcolor = color
    plt.hist(x, bins, normed=True, color=histcol, histtype='stepfilled',
             **kwargs)
    df, loc, scale = ss.chi2.fit(x, floc=0)
    pdf = ss.chi2.pdf(linsp, df, scale=scale)
    l = plt.plot(linsp, pdf, color=lcolor, figure=fig, linewidth=2,
                 label=label)
    l[0].set_dashes(ltyp)
    l[0].set_dash_capstyle('round')


# load data
longform = read_data(rt_data_fnames[0])
longform_voc = read_data(rt_data_fnames[1])

# distribution of targets by slot
byslot = longform.groupby(['slot']).aggregate(dict(targ=np.sum))
print(byslot / byslot.sum())
byslot = longform_voc.groupby(['slot']).aggregate(dict(targ=np.sum))
print(byslot / byslot.sum())

# voc exp foil responses by slot
foilbyslot = longform_voc.groupby(['slot', 'gap_len']).agg(dict(frsp=np.sum))
# voc exp hits by slot
hitbyslot = longform_voc.groupby(['slot', 'gap_len']).agg(dict(hit=np.sum))

# is RT generally different by slot?  YES
nonans = longform.dropna()
slot0 = nonans.loc[nonans.slot == 0]['reax_time']
slot1 = nonans.loc[nonans.slot == 1]['reax_time']
slot2 = nonans.loc[nonans.slot == 2]['reax_time']
slot3 = nonans.loc[nonans.slot == 3]['reax_time']
f_val, aov_p_val = ss.f_oneway(slot0, slot1, slot2, slot3)
comps = [(slot0, slot1), (slot0, slot2), (slot0, slot3),
         (slot1, slot2), (slot1, slot3), (slot2, slot3)]
print(f_val, aov_p_val)
for comp in comps:
    t_val, p_val = ss.ttest_ind(*comp, equal_var=False)
    p_val = p_val / len(comps)  # bonferroni
    print([slot.mean() for slot in comp])
    print([slot.std() for slot in comp])
    print(p_val)


# is maint/switch RT difference localized by slot?  YES
gb = longform.groupby(['slot', 'attn'])
n_resp = gb.agg(dict(reax_time=lambda x: np.sum(np.logical_not(np.isnan(x)))))
means = gb.agg(dict(reax_time=np.mean))
stdev = gb.agg(dict(reax_time=np.std))

pvals = list()
for slot in range(4):
    maint = nonans.loc[np.logical_and(nonans.slot == slot,
                                      nonans.attn == 'maint.')]['reax_time']
    switch = nonans.loc[np.logical_and(nonans.slot == slot,
                                       nonans.attn == 'switch')]['reax_time']
    tval, pval = ss.ttest_ind(maint, switch, equal_var=False)
    pvals.append(pval)
print(pvals)
"""
ax, bar = efa.barplot(means.values, err_bars=stdev.values,
                      groups=[(0, 1), (2, 3), (4, 5), (6, 7)],
                      brackets=[(4, 5), (6, 7)], bracket_text=['***', '*'],
                      bar_names=['maint.', 'switch'] * 4,
                      group_names=['slot {}'.format(x + 1) for x in range(4)])
"""

# is elevated pupil signal in switch condition just an artifact of more
# button presses in those trials? NO: there are actually more responses
# in the maintain condition.
presses = longform.loc[longform.press].groupby(['attn']).count()['reax_time']
targ_resps = longform.loc[longform.hit].groupby(['attn']).count()['reax_time']

# # # # # # # # # # # # # # # # # #
# REACTION TIME HISTOGRAM BY SLOT #
# # # # # # # # # # # # # # # # # #
bins = np.arange(0.1, 1., 0.025)
lsp = np.linspace(0.1, 1.1, 100)

# plot
fig = plt.figure(figsize=(3.4, 3))
plot_hist_chsq(slot0, bins, fig, color='#aa4499', linsp=lsp, edgecolor='none',
               label='slot 1')
plot_hist_chsq(slot1, bins, fig, color='#44aa99', linsp=lsp, edgecolor='none',
               label='slot 2', ltyp=[8, 4])
plot_hist_chsq(slot2, bins, fig, color='#999933', linsp=lsp, edgecolor='none',
               label='slot 3', ltyp=[2, 4])
plot_hist_chsq(slot3, bins, fig, color='#cc6677', linsp=lsp, edgecolor='none',
               label='slot 4', ltyp=[1, 3])

ax = fig.gca()
_ = ax.set_xlim(0.15, 1.05)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params('both', top=False, left=False, right=False, direction='out')
_ = ax.yaxis.set_ticklabels([])
_ = ax.xaxis.set_ticks(np.arange(0.2, 1.1, 0.2))
_ = ax.set_xlabel('Response time (s)')
_ = ax.set_ylabel('Proportion of responses')
lgnd = ax.legend(loc='upper right', frameon=False, fontsize='small',
                 bbox_to_anchor=(1.05, 1.1), handlelength=2.3)
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig('fig-rt-hist.pdf', bbox_extra_artists=(lgnd,))
