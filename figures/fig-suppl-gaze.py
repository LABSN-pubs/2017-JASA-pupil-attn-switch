#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 15:39:57 2017

@author: drmccloy
"""

from __future__ import print_function
import numpy as np
import os.path as op
import matplotlib.pyplot as plt
import seaborn as sns

plt.ioff()
sns.set_style('white')

work_dir = '..'
out_dir = op.join(work_dir, 'results')
voc_file = op.join(work_dir, 'voc_data.npz')
rev_file = op.join(work_dir, 'rev_data.npz')

for exp_file in [rev_file, voc_file]:
    exp_name = op.basename(exp_file)[:3]
    # load data
    ff = np.load(exp_file)
    pupil_size = ff['zscores']
    gaze_angle = ff['angles']
    subjects = ff['subjects']
    del ff
    # see what percent of gaze angles exceed various thresholds
    print('{} experiment'.format(exp_name))
    thresholds = [1, 2, 5, 10]
    pcts = list()
    ga = gaze_angle[np.isfinite(gaze_angle)]  # flatten & exclude NaNs
    for th in thresholds:
        goods = np.sum(ga < th)
        pct = 100 * goods / float(ga.size)
        print('{}% of fixations < {} deg. from fixation cross'.format(pct, th))
        pcts.append(pct)
    # plot each subject
    fig, axs = plt.subplots(4, 4, figsize=(7, 8), sharex=True, sharey=True)
    for subj, gazedata, ax in zip(subjects, gaze_angle, axs.ravel()):
        gd = gazedata[np.isfinite(gazedata)]  # flatten array and exclude NaNs
        sns.distplot(gd, ax=ax, hist=False)
        sns.despine()
        ax.set_xticks([0, 10, 20, 30, 40])
        ax.set_title('subj. {}'.format(subj))
        if ax in axs[-1]:  # bottom row
            ax.set_xlabel('gaze angle (degrees)')
    # fig.suptitle('distribution of gaze deviations from fixation cross')
    plt.tight_layout()
    fig.savefig('{}-gaze-distribution.pdf'.format(exp_name))
    outfile = op.join(out_dir, '{}-gaze-pcts.tsv'.format(exp_name))
    with open(outfile, 'w') as out:
        out.write('threshold\tpercent\n')
        for t, p in zip(thresholds, pcts):
            out.write('{}\t{}\n'.format(t, p))
