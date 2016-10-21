# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'fig-2.py'
===============================================================================

This script plots pupil size & significance tests for the vocoder experiment.
"""
# @author: Dan McCloy (drmccloy@uw.edu)
# Created on Fri Sep 25 11:15:34 2015
# License: BSD (3-clause)

import os.path as op
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter as cc
from scipy.stats import distributions
from mne.stats import spatio_temporal_cluster_1samp_test, ttest_1samp_no_p
from convenience_functions import (box_off, use_font, tick_label_size,
                                   hatch_between)
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
continuous_deconv = False

# file I/O
work_dir = '..'
voc_file = op.join(work_dir, 'rev_data.npz')
vv = np.load(voc_file)
data_deconv, t_fit, subjects = vv['fits'], vv['t_fit'], vv['subjects']
data_zscore, fs, kernel = vv['zscores'], vv['fs'], vv['kernel']
if continuous_deconv:
    data_cont, t_cont = vv['fits_cont'], vv['t_cont']
'''
data_zscore.shape
16,   40,      2,          2,            2,         6550
subj  trials   200/600gap  maint/switch  10/20chan  samples
'''

# params
stim_times = np.array([0, 0.5, 1.5, 2.0, 2.5, 3.0])  # gap not included (yet)
stim_dur = 0.47  # really 0.5, but leave a tiny gap
peak = np.where(kernel == kernel.max())[0][0] / float(fs)
t_min, t_max = -0.5, 6. - peak
t_zs = t_min + np.arange(data_zscore.shape[-1]) / float(fs)
stat_fun = partial(ttest_1samp_no_p, sigma=1e-3)

# colors
cue, msk, blu, red = '0.5', '0.75', '#332288', '#aa4499'
grn, yel = '#44aa99', '#ddcc77'
signifcol = '0.9'
axiscol = '0.8'
tickcol = '0.8'
axislabcol = '0.3'
ticklabcol = '0.5'

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
            ha = ['right', 'right', 'left'][jj]
            xtxt = [0, 0, 4.4][jj]
            ytxt = [stim_ymax, stim_ymin][kk]
            xytxt = [(-6, 0), (-6, 0), (6, 0)][jj]
            _ = ax.annotate(labels[kk], (xtxt, ytxt), xytext=xytxt,
                            textcoords='offset points', color=linecol,
                            ha=ha, va='center', fontsize=9,
                            fontstyle='italic')
        # cue label
        _ = ax.annotate('cue', xy=(stim_times[1], stim_ymax + thk),
                        xytext=(0, 1.5), textcoords='offset points',
                        fontsize=9, fontstyle='italic', ha='center',
                        va='bottom', color=cue)
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
        yl = 'Effort (a.u.)' if use_deconv else 'Pupil size (z-score)'
        yo = 1 - np.diff(ytck) / np.diff(ylim) / 2.
        ax.set_ylabel(yl, y=yo, color=axislabcol)
        ax.set_xlabel('Time (s)', color=axislabcol)

        box_off(ax, ax_linewidth=0.5)
        ax.patch.set_facecolor('none')
#fig.tight_layout(w_pad=2., rect=(0.02, 0, 1, 1))
fig.tight_layout()
fig.text(0.01, 0.98, 'a)')
fig.text(0.01, 0.66, 'b)')
fig.text(0.01, 0.34, 'c)')

if savefig:
    fig.savefig('pupil-fig-rev.pdf')
else:
    plt.ion()
    plt.show()
