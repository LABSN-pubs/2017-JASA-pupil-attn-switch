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

"""
# vocoder 3-way targ detection interaction by slot
n_ttests = 4
cols = ['slot', 'gap_len', 'voc_chan', 'attn', 'subj']
threeway = longform_voc.groupby(cols).agg(aggfuncs)
threeway['hitrate'] = threeway['hit'] / threeway['targ']
hr = threeway.unstack(0)['hitrate']
first_diff = (hr.loc['long'] - hr.loc['short'])
second_diff = first_diff.loc[20] - first_diff.loc[10]
tval, pval = ss.ttest_rel(second_diff.loc['maint.'], second_diff.loc['switch'])
star = efa.format_pval(n_ttests * pval, False, 'stars')
print('long minus short, 20 minus 10, maint. vs switch')
for slot in range(4):
    print('  slot {}: {:.6f} {}'.format(slot + 1, pval[slot], star[slot]))
"""


raise RuntimeError
# vocoder experiment: distribution of foil response rate by slot
aggfuncs = dict(frsp=np.sum, hit=np.sum, targ=np.sum, foil=np.sum)
vocbyslot = longform_voc.groupby(['slot', 'gap_len', 'subj']).agg(aggfuncs)
vocbyslot['foilrate'] = vocbyslot.frsp / vocbyslot.foil
vocbyslot = vocbyslot.unstack([0, 1])['foilrate']
pvals = list()
for slot in range(4):
    _long = vocbyslot[slot, 'long']
    _short = vocbyslot[slot, 'short']
    tval, pval = ss.ttest_ind(_long, _short, equal_var=False)
    pvals.append(pval)
print(pvals)
ax, bar = efa.barplot(vocbyslot.values, axis=0, err_bars='se',
                      groups=[(0, 1), (2, 3), (4, 5), (6, 7)],
                      brackets=[(2, 3), (4, 5)], bracket_text=['*', '**'],
                      bar_names=['long', 'short'] * 4,
                      group_names=['slot {}'.format(x + 1) for x in range(4)])


attn_x_gap = longform_voc.groupby(['attn', 'slot', 'gap_len',
                                   'subj']).agg(aggfuncs)
attn_x_gap['foilrate'] = attn_x_gap.frsp / attn_x_gap.foil
attn_x_gap['hitrate'] = attn_x_gap.hit / attn_x_gap.targ
attn_x_gap['resprate'] = ((attn_x_gap.hit + attn_x_gap.frsp) /
                          (attn_x_gap.targ + attn_x_gap.foil))
maint_minus_switch = attn_x_gap.loc['maint.'] - attn_x_gap.loc['switch']
hits = maint_minus_switch.unstack([0, 1])['hit']  # last slot
hitrate = maint_minus_switch.unstack([0, 1])['hitrate']  # last slot
foilrate = maint_minus_switch.unstack([0, 1])['foilrate']  # no sign. diffs.
pvals = list()
for slot in range(4):
    _long = hits[slot, 'long']
    _short = hits[slot, 'short']
    tval, pval = ss.ttest_ind(_long, _short, equal_var=False)
    pvals.append(pval)
print(pvals)


# vocoder: 3-way sensitivity interaction (foils)
three_way = longform_voc.groupby(['slot', 'gap_len', 'voc_chan', 'attn',
                                  'subj']).agg(aggfuncs)
three_way['foilrate'] = three_way.frsp / three_way.foil
three_way['hitrate'] = three_way.hit / three_way.targ
three_way['resprate'] = ((three_way.hit + three_way.frsp) /
                         (three_way.targ + three_way.foil))
hitrate = three_way.unstack([0, 1, 2, 3])['hitrate']
foilrate = three_way.unstack([0, 1, 2, 3])['foilrate']
pvals = list()
for rate in [hitrate, foilrate]:
    for slot in range(4):
        for dur in ['long', 'short']:
            for chan in [10, 20]:
                maint = rate[slot, dur, chan, 'maint.']
                switch = rate[slot, dur, chan, 'switch']
                tval, pval = ss.ttest_ind(maint, switch, equal_var=False)
                pvals.append(pval)
    print(pvals)
    colors = (['0.5', '0.7'] * 2 + ['0.6', '0.8'] * 2 +
              ['g', 'y'] * 2 + ['b', 'c'] * 2) * 2
    ax, bar = efa.barplot(rate.values, axis=0, err_bars='se',
                          groups=np.arange(rate.shape[1]).reshape(-1, 2),
                          # brackets=[(0, 1), (2, 3), (6, 7)],
                          # bracket_text=['***', '*', '*'],
                          bar_names=['m.', 's.'] * (rate.shape[1] // 2),
                          group_names=['10', '20'] * (rate.shape[1] // 4),
                          bar_kwargs=dict(color=colors))


# is RT generally different by slot?  YES
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
