# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'fig-pupil-rev'
===============================================================================

This script plots pupil size & significance tests for the reverb experiment.
"""
# @author: Dan McCloy (drmccloy@uw.edu)
# Created on Fri Sep 25 11:15:34 2015
# License: BSD (3-clause)

import yaml
import os.path as op
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from matplotlib.colors import colorConverter as cc
from scipy.stats import distributions
from mne.stats import spatio_temporal_cluster_1samp_test, ttest_1samp_no_p
from convenience_functions import (box_off, use_font, tick_label_size,
                                   hatch_between, read_data)
from functools import partial

# mostly rcParams stuff
plt.ioff()
use_font('source')
tick_label_size(10)

# flags
plot_stderr = True
plot_signif = True
show_pval = False
savefig = True
use_deconv = True
only_perfect = False

# file I/O
work_dir = '..'
out_dir = op.join(work_dir, 'results')
voc_file = op.join(work_dir, 'rev_data.npz')
perfect_filename = '-perfect' if only_perfect else ''
vv = np.load(voc_file)
data_deconv, t_fit, subjects = vv['fits_struct'], vv['t_fit'], vv['subjects']
data_zscore, fs, kernel = vv['zscores_struct'], vv['fs'], vv['kernel']
'''
data_zscore.shape
16,   40,      2,          2,            2,           6550
subj  trials   mm/mf       maint/switch  reverb/anech samples
(similar for data_deconv, with fewer samples along last dimension)
'''

# params
stim_times = np.array([0, 0.5, 1.5, 2.0, 2.5, 3.0])  # gap not included (yet)
stim_dur = 0.47  # really 0.5, but leave a tiny gap to visually distinguish
t_kernel_peak = np.where(kernel == kernel.max())[0][0] / float(fs)
t_min, t_max = -0.5, 6. - t_kernel_peak
t_zs = t_min + np.arange(data_zscore.shape[-1]) / float(fs)
stat_fun = partial(ttest_1samp_no_p, sigma=1e-3)

# colors
cue, msk, blu, red = '0.75', '0.75', '#332288', '#cc6677'
signifcol = '0.9'
axiscol = '0.8'
tickcol = '0.8'
axislabcol = '0.3'
ticklabcol = '0.5'

# get behavioral data
if only_perfect:
    path = op.join(work_dir, 'data-behavioral', 'rev-behdata-longform.tsv')
    beh_data = read_data(path, parse_presses=False)
    beh_data['perfect'] = np.logical_and(beh_data['misses'] == 0,
                                         beh_data['false_alarms'] == 0)
    cols = ['subj', 'reverb', 'attn', 'gender']
    beh_data = beh_data.sort_values(by=cols)
    dims = [len(beh_data[c].unique()) for c in cols]
    dims.insert(1, -1)
    perfect_ix = beh_data['perfect'].reshape(dims)
    mm_ix = (beh_data['gender'] == 'MM').reshape(dims)
    mf_ix = (beh_data['gender'] == 'MF').reshape(dims)
    reverb_ix = (beh_data['reverb'] == 'reverb').reshape(dims)
    anech_ix = (beh_data['reverb'] == 'anech.').reshape(dims)
    maint_ix = (beh_data['attn'] == 'maint.').reshape(dims)
    switch_ix = (beh_data['attn'] == 'switch').reshape(dims)

# set up figure
fig, axs = plt.subplots(3, 1, figsize=(3, 6.5))
xlim = [t_min, t_max]

times = [t_fit] if use_deconv else [t_zs]
datas = [data_deconv] if use_deconv else [data_zscore]
for t, data in zip(times, datas):
    # collapse across trials and experimental contrasts
    # axis 1 is trials, 2 is mm/mf, 3 is maint/switch, 4 is reverb/anechoic
    revb_vs_anech = np.nanmean(data, axis=(1, 2, 3))
    mm_vs_mf = np.nanmean(data, axis=(1, 3, 4))
    maint_vs_switch = np.nanmean(data, axis=(1, 2, 4))
    # if only analyzing trials with perfect behavioral response, recompute
    # the per-subject mean pupil resp. by condition using only those trials
    # (a bit awkward because of potentially unequal counts)
    if only_perfect:
        # temporarily set these to infinite values (to check later that they
        # got properly re-assigned)
        revb_vs_anech = np.full_like(revb_vs_anech, np.inf)
        mm_vs_mf = np.full_like(mm_vs_mf, np.inf)
        maint_vs_switch = np.full_like(maint_vs_switch, np.inf)
        # keep track of how many correct trials per condition
        n_perfect_trials = dict()
        for ix, subj in enumerate(subjects):
            sj = np.zeros_like(perfect_ix)
            sj[ix] = True
            mm = np.logical_and(perfect_ix, mm_ix)
            mf = np.logical_and(perfect_ix, mf_ix)
            rv = np.logical_and(perfect_ix, reverb_ix)
            an = np.logical_and(perfect_ix, anech_ix)
            mn = np.logical_and(perfect_ix, maint_ix)
            sw = np.logical_and(perfect_ix, switch_ix)
            mm_vs_mf[ix] = np.array([np.nanmean(data[sj & mm], axis=0),
                                     np.nanmean(data[sj & mf], axis=0)])
            revb_vs_anech[ix] = np.array([np.nanmean(data[sj & rv], axis=0),
                                          np.nanmean(data[sj & an], axis=0)])
            maint_vs_switch[ix] = np.array([np.nanmean(data[sj & mn], axis=0),
                                            np.nanmean(data[sj & sw], axis=0)])
            # bookkeeping for n_perfect_trials
            conds = dict()
            conds['gend'] = {'mm': np.logical_and(mm, sj).sum(),
                             'mf': np.logical_and(mf, sj).sum()}
            conds['rev'] = {'reverb': np.logical_and(rv, sj).sum(),
                            'anech': np.logical_and(an, sj).sum()}
            conds['attn'] = {'maint': np.logical_and(mn, sj).sum(),
                             'switch': np.logical_and(sw, sj).sum()}
            n_perfect_trials[subj] = conds
        assert np.all(np.isfinite(mm_vs_mf))
        assert np.all(np.isfinite(revb_vs_anech))
        assert np.all(np.isfinite(maint_vs_switch))

    # axis limits
    ymax = np.max(np.mean(np.nanmean(data, axis=1), axis=0))  # ceil
    ymax = 10 ** np.trunc(np.log10(ymax)) if ymax < 1 else np.ceil(ymax)
    ylim = [-0.6 * ymax, ymax]
    # y values for stim timecourse diagram
    stim_ymin = ymax * -0.45
    stim_ymax = ymax * -0.3
    for jj, (contrast, ax) in enumerate(zip([revb_vs_anech, mm_vs_mf,
                                             maint_vs_switch], axs)):
        # within-subject difference between conditions
        contr_diff = (contrast[:, 1, :] - contrast[:, 0, :])[:, :, np.newaxis]
        # collapse across subjects (only for plotting, not stats)
        contr_std = np.std(contrast, axis=0) / np.sqrt(len(contrast) - 1)
        contr_mean = np.mean(contrast, axis=0)
        # vars for trial timecourse
        gaps = [[0.6, 0.6], [0.2, 0.6], [0.6, 0.6]][jj]
        labels = [['reverb', 'anechoic'], ['male/male', 'male/female'],
                  ['maintain', 'switch']][jj]
        colors = [[cue, cue], [cue, cue], [blu, red]][jj]
        # plot curves
        for kk, (cond, se) in enumerate(zip(contr_mean, contr_std)):
            col = colors[kk]
            linecol = [blu, red][kk]
            tcol = cc.to_rgb(linecol) + (0.4,)  # add alpha channel
            tcol_hex = '#' + ''.join('%02x' % int(x * 255) for x in tcol)
            zord = [2, 0][kk]
            # plot standard error bands
            if plot_stderr:
                _ = ax.fill_between(t, cond-se, cond+se, color=tcol,
                                    edgecolor='none', zorder=zord + 2)
            # plot mean lines
            _ = ax.plot(t, cond, color=linecol, linewidth=1.2, zorder=zord + 3)
            # TRIAL TIMECOURSE
            thk = 0.04 * ymax
            off = 0.15 * ymax
            loff = 0.01 * ymax
            stim_y = [stim_ymin, stim_ymax][kk]
            label_y = [stim_ymax, stim_ymax-off][kk]
            # lines beneath stim boxes
            if kk:  # "switch" line
                xnodes = (1, 2.5, 3.1, 4.4)
                ynodes = (stim_y-loff, stim_y-loff,
                          stim_y-off+loff, stim_y-off+loff)
                ax.plot(xnodes, ynodes, color=col, linewidth=1.,
                        linestyle='--', zorder=7)
            else:  # "maintain" line
                ynodes = (stim_ymax+loff, stim_ymax+loff)
                ax.plot((1, 4.4), ynodes, color=col, linewidth=1.,
                        solid_capstyle='butt', zorder=7)
            # boxes
            gap_offsets = np.array([0] * 4 + [gaps[kk]] * 2)
            stim_t = stim_times + gap_offsets
            box_x = np.r_[stim_t, stim_t[2:]]
            box_y = np.array([stim_ymax] * 6 + [stim_ymin] * 4)
            box_u = np.array([thk] * 10)
            box_d = np.array([thk] * 10)
            # colors must be tuples (not hex strings) for alpha to work
            box_c = [cc.to_rgba(x) for x in [cue] * 2 + [msk] * 8]
            if kk:
                for x, y, c, u, d in zip(box_x, box_y, box_c, box_u, box_d):
                    c = cc.to_rgba_array(c)
                    ax.fill_between((x, x+stim_dur), y+u, y-d, color=c,
                                    edgecolor='none', zorder=9)
            # timecourse labels
            xtxt = [-0.1, -0.1, 4.4][jj]
            ytxt = [[0.09, 0.075], [0.09, 0.075],
                    [stim_ymax, stim_ymin]][jj][kk]
            xytxt = [(0, 0), (0, 0), (5, 0)][jj]
            _ = ax.annotate(labels[kk], (xtxt, ytxt), xytext=xytxt,
                            textcoords='offset points', color=linecol,
                            ha='left', va='center', fontsize=9)
        # cue label
        _ = ax.annotate('cue', xy=(stim_times[1], stim_ymax + thk),
                        xytext=(0, 1.5), textcoords='offset points',
                        fontsize=9, fontstyle='italic', ha='center',
                        va='bottom', color='0.5')
        # stats
        if plot_signif:
            thresh = -1 * distributions.t.ppf(0.05 / 2, len(contr_diff) - 1)
            result = spatio_temporal_cluster_1samp_test(
                contr_diff, threshold=thresh, stat_fun=stat_fun, n_jobs=6,
                buffer_size=None, n_permutations=np.inf)
            tvals, clusters, cluster_pvals, H0 = result
            signif = np.where(np.array([p <= 0.05 for p in cluster_pvals]))[0]
            signif_clusters = [clusters[s] for s in signif]
            signif_cluster_pvals = cluster_pvals[signif]
            # we only need x[0] in clusters because this is 1-D data; x[1] in
            # clusters is just a list of all zeros (no spatial connectivity).
            # All the hacky conversions to float, int, and list are because
            # yaml doesn't understand numpy dtypes.
            pupil_signifs = dict(thresh=float(thresh),
                                 n_clusters=len(clusters),
                                 clusters=[[int(y) for y in x[0]]
                                           for x in clusters],
                                 tvals=tvals.tolist(),
                                 pvals=cluster_pvals.tolist())
            label = '_vs_'.join([l.replace('/', '-') for l in labels])
            fname = 'rev_cluster_signifs_{}.yaml'.format(label)
            with open(op.join(out_dir, fname), 'w') as f:
                yaml.dump(pupil_signifs, stream=f)
            # plot stats
            for clu, pv in zip(signif_clusters, signif_cluster_pvals):
                '''
                # this index tells direction of tval, hence could be used to
                # decide which color to draw the significant cluster region
                # based on which curve is higher:
                idx = (np.sign(tvals[clu[0][0], 0]).astype(int) + 1) // 2
                '''
                clu = clu[0]
                cluster_ymin = ylim[0] * np.ones_like(t[clu])
                cluster_ymax = np.max(contr_mean[:, clu], axis=0)  # under top
                pval_x = t[int(np.mean(clu[[0, -1]]))]
                pval_y = -0.1 * ylim[1]
                pval_ord = np.trunc(np.log10(pv)).astype(int)

                hatch_between(ax, 9, t[clu], cluster_ymin,
                              cluster_ymax, linewidth=1.25,
                              color=signifcol, zorder=1)
                if show_pval:
                    pval_txt = '$p < 10^{{{}}}$'.format(pval_ord)
                    ax.text(pval_x, pval_y, pval_txt, ha='center',
                            va='baseline', fontdict=dict(size=10))
            # vertical lines
            if len(signif):
                for ix in (0, -1):
                    ax.plot((t[clu][ix], t[clu][ix]),
                            (cluster_ymin[ix], cluster_ymax[ix]),
                            linestyle=':', color=axiscol, linewidth=1)
        # set axis limits
        xlim[1] = 1.001 * xlim[1]
        ylim[1] = 1.001 * ylim[1]
        ax.set_ylim(*ylim)
        ax.set_xlim(*xlim)
        ax.xaxis.set_ticks(np.arange(np.ceil(xlim[1])))
        # remove yaxis / ticks / ticklabels near bottom
        ytck = [-0.1 * ymax, 1.001 * ymax]
        ytl = ax.yaxis.get_ticklocs()
        ax.spines['left'].set_bounds(*ytck)
        for sp in ['left', 'bottom']:
            ax.spines[sp].set_color(axiscol)
        ax.yaxis.set_ticks(ytl[ytl > ytck[0]])
        ax.set_ylim(*ylim)  # have to do this twice
        ax.tick_params(color=tickcol, width=0.5, labelcolor=ticklabcol)

        # annotations
        yl = u'“Effort” (a.u.)' if use_deconv else 'Pupil size (z-score)'
        yo = 1 - np.diff(ytck) / np.diff(ylim) / 2.
        ax.set_ylabel(yl, y=yo, color=axislabcol)
        ax.set_xlabel('Time (s)', color=axislabcol)

        box_off(ax, ax_linewidth=0.5)
        ax.patch.set_facecolor('none')
# fig.tight_layout(w_pad=2., rect=(0.02, 0, 1, 1))
fig.tight_layout()
fig.text(0.01, 0.98, 'a)')
fig.text(0.01, 0.66, 'b)')
fig.text(0.01, 0.34, 'c)')

if savefig:
    fig.savefig('pupil-fig-rev{}.pdf'.format(perfect_filename))
else:
    plt.ion()
    plt.show()

if only_perfect:
    df = DataFrame.from_dict(n_perfect_trials, orient='index')
    df.to_csv(op.join(out_dir, 'rev_perfect_trials.csv'))
