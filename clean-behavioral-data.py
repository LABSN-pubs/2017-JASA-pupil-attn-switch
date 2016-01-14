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
from glob import glob
from os import getcwd
from os import path as op
from scipy.io import loadmat

# params
rev_subjects = ['1', '2', '3', '4', '5', '6', '7', '10',
                '11', '13', '14', '15', '16', '18', '20', '91']
voc_subjects = ['01', '02', '04', '55', '6', '7', '8', '10',
                '11', '12', '13', '14', '96', '97', '98', '99']

# file I/O
data_dir = 'data-behavioral'
data_subdirs = ['reverb-raw', 'vocoder-raw']
work_dir = getcwd()

longforms = list()
for ix, subdir in enumerate(data_subdirs):
    times = list()
    resps = list()
    reaxs = list()
    indir = op.join(work_dir, data_dir, subdir)
    subjects = [rev_subjects, voc_subjects][ix]
    for subj in subjects:
        matfile = glob(op.join(indir, 'subj{}_*.mat'.format(subj)))
        assert len(matfile) == 1
        mat = loadmat(matfile[0])
        """ mat.keys():
        ['timeStopped', 'singleData', 'trialNum', 'timeVecs', 'nTrains',
         '__header__', '__globals__', 'timeVecsHeader', 'respData', 'respList',
         '__version__', 'blockNum', 'respDataHeader']
        """
        for key in ['timeVecs', 'respData', 'respList']:
            assert mat[key][0][0].shape == (1, 0)  # empty header
            assert np.all([x[0].shape[0] == 10
                           for x in mat[key][1:4]])  # training blocks
            assert np.all([x[0].shape[0] == 32
                           for x in mat[key][4:]])  # test blocks
        this_times = np.squeeze([x[0] for x in mat['timeVecs'][4:]])
        """ this_times.shape
        (10, 32, 4)  # block, trial, (tStart, tSound, tRespCheckDone, tDone)
        """
        this_resps = np.squeeze([x[0] for x in mat['respData'][4:]])
        """ this_resps.shape
        (10, 32, 8)  # block, trial, (training, runInd, band, cue(1=U,2=D),
                                      attn(1=stay,2=switch), hits, misses,
                                      falseAlarms)
        """
        this_reaxs = list()
        for block in mat['respList'][4:]:
            trials = list()
            # the [0]s on next 2 lines index into 1-element object arrays
            for trial in block[0]:
                reax = np.squeeze(trial[0]).tolist()
                reax = [reax] if not isinstance(reax, list) else reax
                trials.append(reax)
            this_reaxs.append(trials)
        # save out
        times.append(this_times)
        resps.append(this_resps)
        reaxs.append(this_reaxs)
    times = np.array(times)
    resps = np.array(resps)

    rows = list()
    for subj, t, r, x in zip(subjects, times, resps, reaxs):
        for block, (tt, rr, xx) in enumerate(zip(t, r, x)):
            for trial, (ttt, rrr, xxx) in enumerate(zip(tt, rr, xx)):
                row = [subj, block, trial] + ttt.tolist() + rrr.tolist() \
                    + [xxx]
                rows.append(row)
    header = ['subj', 'block', 'trial', 't_start', 't_audio', 't_resp_check',
              't_done', 'is_training', 'run_index', 'band', 'cue_1u_2d',
              'maint1_switch2', 'hits', 'misses', 'false_alarms',
              'reax_times']
    longform = pd.DataFrame(rows, columns=header)
    fname = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv'][ix]
    longform.to_csv(op.join(work_dir, data_dir, fname), sep='\t', index=False)
