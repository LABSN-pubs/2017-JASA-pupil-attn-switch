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
min_rt = 0.1  # minimum reaction time, 100 ms
max_rt = 1.0

# file I/O
data_dir = 'data-behavioral'
data_subdirs = ['reverb-raw', 'vocoder-raw']
param_subdirs = ['data-reverb', 'data-vocoder']
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
        # respList is the button press times
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
                                      falseAlarms) # from respDataHeader
        """
        this_resps[:, :, 1] -= 1  # convert runInd to 0-indexed
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
              'press_times']
    longform = pd.DataFrame(rows, columns=header)
    longform['corr_rej'] = 4 - longform['hits'] - longform['false_alarms']
    longform['attn'] = np.array(['maint.', 'switch']
                                )[(longform['maint1_switch2'] == 2
                                   ).values.astype(int).tolist()]
    if ix:
        longform['voc_chan'] = longform['band']
        longform['gap_len'] = np.array(['long', 'short']
                                       )[(longform['cue_1u_2d'] == 1
                                          ).values.astype(int).tolist()]
    else:
        longform['reverb'] = np.array(['anech.', 'reverb']
                                      )[(longform['band'] == 10
                                         ).values.astype(int).tolist()]
        longform['gender'] = np.array(['MF', 'MM']
                                      )[(longform['cue_1u_2d'] == 1
                                         ).values.astype(int).tolist()]
    # load letter presentations
    mat = loadmat(op.join(work_dir, param_subdirs[ix], 'orderMain.mat'))
    letters = [str(lett) for lett in mat['alphaList'][0]]
    letter_ixs = mat['fillSeq'].T - 1  # 160 trials, 2 talkers, 4 letters
    letter_mat = np.array(letters)[letter_ixs]
    targ_letts = letter_mat[:, 0]
    mask_letts = letter_mat[:, 1]
    target_letter = ['O', 'O'][ix]  # same for both experments
    targ_lett = targ_letts[longform['run_index']]
    mask_lett = mask_letts[longform['run_index']]
    n_targs = (targ_lett == target_letter).sum(axis=-1)
    assert np.array_equal(n_targs, longform['hits'] + longform['misses'])
    longform['targ_letters'] = [x for x in targ_lett]
    longform['mask_letters'] = [x for x in mask_lett]
    # save files
    output_columns = (['subj', 'block', 'trial', 'run_index'] +
                      [['reverb', 'gender'], ['voc_chan', 'gap_len']][ix] +
                      ['attn', 'hits', 'misses', 'false_alarms', 'corr_rej',
                       'press_times', 'targ_letters', 'mask_letters'])
    fname = ['rev-behdata-longform.tsv', 'voc-behdata-longform.tsv'][ix]
    longform[output_columns].to_csv(op.join(work_dir, data_dir, fname),
                                    sep='\t', index=False)
    # make extra-long-form (1 row per timeslot)
    gaps = [0.6, np.array([0.2, 0.6])][ix]
    gap = (np.tile(gaps[(longform['gap_len'] == 'long').astype(int)][:, None],
                   (1, 2)) if ix else np.tile(gaps, (longform.shape[0], 2)))
    slots = np.tile(np.arange(0, 4), (longform.shape[0], 1))
    onsets = np.tile(np.linspace(0, 2, 4, endpoint=False),
                     (longform.shape[0], 1))
    onsets[:, 2:] += gap
    longform['onsets'] = [x for x in onsets]
    # TODO: next line broken; searchsorted won't work, look for lowest index(?)
    # where (o + min_rt) < p < (o + max_rt)
    longform['press_indices'] = [np.searchsorted(o + min_rt, p) - 1
                                 for o, p in zip(longform['onsets'],
                                                 longform['press_times'])]
    slots_df = pd.DataFrame(dict(attn_lett=targ_lett.ravel(),
                                 mask_lett=mask_lett.ravel(),
                                 onset=onsets.ravel(), slot=slots.ravel(),
                                 subj=np.repeat(longform['subj'].values, 4),
                                 block=np.repeat(longform['block'].values, 4),
                                 trial=np.repeat(longform['trial'].values, 4)))
    slots_df['targ'] = slots_df['attn_lett'] == target_letter
    xlongform = pd.merge(slots_df, longform, on=['subj', 'block', 'trial'],
                         how='left')
    # distribute press times to appropriate slots
    slot_press_match = np.array([s in p for s, p in
                                 zip(xlongform['slot'],
                                     xlongform['press_indices'])])
    slot_press_ix = [np.where(p == s)[0][0] for s, p in
                     zip(xlongform['slot'][slot_press_match],
                         xlongform['press_indices'][slot_press_match])]
    temp = np.zeros(xlongform.shape[0]) * np.nan
    temp[slot_press_match] = [t[i] for t, i in
                              zip(xlongform['press_times'][slot_press_match],
                                  slot_press_ix)]
    xlongform['press_time'] = temp  # temp avoids pandas SettingWithCopy error
    xlongform['reax_time'] = xlongform['press_time'] - xlongform['onset']
    # distribute hit/miss/fa counts to appropriate slots
    xlongform['hit'] = (xlongform['targ'] & (xlongform['reax_time'] <= 1.) &
                        ~np.isnan(xlongform['press_time']))  # analysis:ignore
    xlongform['miss'] = (xlongform['targ'] & ((xlongform['reax_time'] > 1.) |
                                              np.isnan(xlongform['press_time'])
                                              ))
    assert np.all(xlongform['hits'][xlongform['hit']] > 0)
    assert np.all(xlongform['misses'][xlongform['miss']] > 0)
    assert xlongform['hit'].sum() == longform['hits'].sum()
    raise RuntimeError
    temp = np.zeros(xlongform.shape[0], dtype=int)
    temp[slot_press_match] = [t[i] for t, i in
                              zip(xlongform['press_times'][slot_press_match],
                                  slot_press_ix)]
    """
    assert np.array_equal(xlongform['hit'],
                          np.logical_and(~np.isnan(xlongform['press_time']),
                                         xlongform['targ']))
    """
    # save extra-long form
    output_columns = (['subj', 'block', 'trial', 'run_index'] +
                      [['reverb', 'gender'], ['voc_chan', 'gap_len']][ix] +
                      ['attn', 'hits', 'misses', 'false_alarms', 'corr_rej',
                       'slot', 'attn_lett', 'mask_lett', 'targ', 'onset',
                       'press_time', 'reax_time'])
    fname = ['rev-behdata-xlongform.tsv', 'voc-behdata-xlongform.tsv'][ix]
    xlongform[output_columns].to_csv(op.join(work_dir, data_dir, fname),
                                     sep='\t', index=False)
