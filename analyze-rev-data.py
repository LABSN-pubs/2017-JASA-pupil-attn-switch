# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'Analyze reverb data'
===============================================================================

This script cleans and epochs pupillometry data for the reverb/gender
experiment.
"""
# @author: Eric Larson (larsoner@uw.edu)
# @author: Dan McCloy  (drmccloy@uw.edu)
# Created on Thu Sep 17 15:47:08 2015
# License: BSD (3-clause)


from __future__ import print_function
import time
from os import getcwd
from os import path as op
import numpy as np
from scipy.io import loadmat
from pyeparse import read_raw, Epochs
from pyeparse.utils import pupil_kernel
from pupil_helper_functions import (parse_run_indices, get_onset_times,
                                    get_pupil_data_file_list,
                                    extract_event_codes, reorder_epoched_data,
                                    restructure_dims, do_continuous_deconv,
                                    get_gaze_angle)


# flags
downsample = False
run_continuous_deconv = False
n_jobs = 4  # for parallelizing epochs.resample and epochs.deconvolve

# file I/O
data_dir = 'data-reverb'
work_dir = getcwd()
param_file = op.join(data_dir, 'orderMain.mat')

# params
subjects = ['1', '2', '3', '4', '5', '6', '7', '10',
            '11', '13', '14', '15', '16', '18', '20', '91']
n_blocks = 10
t_min, t_max = -0.5, 6.05  # trial epoch extents
deconv_time_pts = None
t_peak = 0.512  # t_max of pupil response kernel estimated at LABS^N; see
                # http://dx.doi.org/10.1121/1.4943787    (analysis:ignore)
fs_in = 1000.0
fs_out = 25.  # based on characterize-freq-content.py; no appreciable energy
              # above 3 Hz in average z-score data or kernel  (analysis:ignore)
fs_out = fs_out if downsample else fs_in

# physical details of the eyetracker/screen setup
# (for calculating gaze deviation from fixation cross in degrees)
screenprops = dict(dist_cm=50., width_cm=53., height_cm=29.8125,
                   width_px=1920, height_px=1080)

# load trial info
bm = loadmat(param_file)
run_inds = bm['runInds']
stim_indices, bands = parse_run_indices(run_inds, n_blocks)
'''
comment from MATLAB (makeSoundFiles.m, line 133) about bigMat:
bigMat = []; % Attn switch (0=no, 1=yes), midGapInd,
               initial target (talker index), inital masker (talker index),
               cueType, TargMod, MaskMod, Mask Multiplier, Targ pos, Mask pos
'''
big_mat = bm['bigMat']

# construct event dict (mapping between trial parameters and integer IDs)
event_dict = dict()
for sn, sw in zip([100, 200], ['M', 'S']):        # maintain / switch
    for gn, gs in zip([10, 20], ['MM', 'MF']):    # gender match / mismatch
        for bn, bs in zip([1, 2], ['Reverb', 'Anechoic']):  # reverberation
            event_dict.update({'x'.join([sw, gs, bs]): sn + gn + bn})

# init some containers
zscores = list()
zscores_structured = list()
fits = list()
fits_structured = list()
fits_continuous = list()
gaze_angles = list()  # relative to fixation cross

# pre-calculate kernel
kernel = pupil_kernel(fs_out, t_max=t_peak, dur=2.0)

for subj in subjects:
    t0 = time.time()
    raws = list()
    events = list()
    print('Subject {}...'.format(subj))
    # load stim times from MAT file of trial params / behavioral responses
    stim_onset_times = get_onset_times(subj, data_dir)
    # find files for this subj
    fnames = get_pupil_data_file_list(subj, data_dir)
    print('  Loading block', end=' ')
    for ri, fname in enumerate(fnames):
        print(str(ri + 1), end=' ')
        raw = read_raw(fname)
        assert raw.info['sfreq'] == fs_in
        raw.remove_blink_artifacts()
        raws.append(raw)
        # get the stimulus numbers presented in this block
        this_stim_nums = stim_indices[ri]
        # extract event codes from eyelink data
        event = extract_event_codes(raw, this_stim_nums, stim_onset_times, ri)
        # convert event IDs; cf. lines 250-251 of vocExperiment_v2.m
        # showing which dimensions correspond to gap & attn
        band_num = bands[ri]
        gap_num = 10 * big_mat[this_stim_nums, 1]
        attn_num = 100 * big_mat[this_stim_nums, 0]
        event[:, 1] = band_num + gap_num + attn_num
        events.append(event)

    print('\n  Epoching...')
    epochs = Epochs(raws, events, event_dict, t_min, t_max)
    if downsample:
        print('  Downsampling...')
        epochs.resample(fs_out, n_jobs=n_jobs)
    # compute gaze angles (in degrees)
    angles = get_gaze_angle(epochs, screenprops)
    # put zscored pupil size in same order as big_mat
    # (sequential by stimulus ID)
    zscore = epochs.pupil_zscores()
    zscore_ord = reorder_epoched_data(zscore, big_mat, bands, stim_indices,
                                      epochs.n_times)
    # now reshape by condition (trial, gap, attn, bands, time)
    zscore_struct = restructure_dims(zscore_ord, big_mat, bands,
                                     epochs.n_times)
    # init some containers
    kernel_fits = list()
    kernel_zscores = list()
    kernel_fits_continuous = list()

    print('  Deconvolving...')
    deconv_kwargs = dict(kernel=kernel, n_jobs=n_jobs, acc=1e-3)
    if deconv_time_pts is not None:
        deconv_kwargs.update(dict(spacing=deconv_time_pts))
    fit, time_pts = epochs.deconvolve(**deconv_kwargs)
    if deconv_time_pts is None:
        deconv_time_pts = time_pts
    assert np.array_equal(deconv_time_pts, time_pts)
    # put deconvolved pupil size in same order as big_mat
    # (sequential by stimulus ID)
    fit_ord = reorder_epoched_data(fit, big_mat, bands, stim_indices,
                                   len(deconv_time_pts))
    # now reshape by condition (trial, gap, attn, bands, time)
    fit_struct = restructure_dims(fit_ord, big_mat, bands,
                                  len(deconv_time_pts))
    # continuous deconvolution
    if run_continuous_deconv:
        (cont_deconv_struct,
         cont_deconv_times) = do_continuous_deconv(zscore_struct, kernel,
                                                   epochs.times)
        fits_continuous.append(cont_deconv_struct)
    # append this subject's data to global vars
    fits.append(fit)
    zscores.append(zscore)
    gaze_angles.append(angles)
    fits_structured.append(fit_struct)
    zscores_structured.append(zscore_struct)
    print('  Done: {} sec.'.format(str(round(time.time() - t0, 1))))
# convert to arrays
fits_array = np.array(fits)
fits_struct_array = np.array(fits_structured)
zscores_array = np.array(zscores)
zscores_struct_array = np.array(zscores_structured)
gaze_angles = np.array(gaze_angles)

# params to output for all kernels
out_dict = dict(fs=fs_out, subjects=subjects, t_fit=deconv_time_pts,
                kernel=kernel, fits=fits_array, zscores=zscores_array,
                fits_struct=fits_struct_array, angles=gaze_angles,
                zscores_struct=zscores_struct_array, times=epochs.times)
if run_continuous_deconv:
    fits_continuous_array = np.array(fits_continuous)
    out_dict.update(dict(cont_fits_struct=fits_continuous_array,
                         cont_deconv_times=cont_deconv_times))

np.savez_compressed(op.join(work_dir, 'rev_data.npz'), **out_dict)
