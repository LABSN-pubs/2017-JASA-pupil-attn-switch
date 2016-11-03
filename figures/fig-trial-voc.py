# -*- coding: utf-8 -*-
"""
===============================================================================
Script 'fig-1.py'
===============================================================================

This script plots a trial diagram for the pupil vocoder switching task.
"""
# @author: Dan McCloy (drmccloy@uw.edu)
# Created on Wed Sep 23 16:57:41 2015
# License: BSD (3-clause)

# this is needed for embedding OpenType font in postscript output (which then
# gets converted to EPS by ps2eps in the makefile)
# import matplotlib
# matplotlib.use('cairo')

from numpy import linspace, tile
import matplotlib.pyplot as plt
from convenience_functions import use_font

plt.ioff()
use_font('source')

# set up figure
fig = plt.figure(figsize=(6.5, 1.75))
ax = plt.Axes(fig, [0.025, 0.225, 0.9, 0.825])
ax.axis('off')
fig.add_axes(ax)

# color defs
gapcol = '#999933'
slotcol = '#44aaaa'
malecol = '0.5'
femalecol = '0.7'
cuecol = 'w'
maintcol = '#332288'
switchcol = '#aa4499'
lettercol = 'w'
slashcol = 'k'

# maint / switch lines
ax.plot((1, 4.5), (2.1, 2.1), color=maintcol, linewidth=3.5,
        solid_capstyle='butt')
ax.plot((1, 2.5, 2.7, 4.5), (1.9, 1.9, 0, 0), color=switchcol,
        linewidth=3.5, linestyle='--')
ax.text(4.6, 2.1, 'maintain', color=maintcol, ha='left', va='center')
ax.text(4.6, 0, 'switch', color=switchcol, ha='left', va='center')

# boxes & letters
centers_x = [0.23, 0.75, 1.75, 2.25, 2.95, 3.45, 1.75, 2.25, 2.95, 3.45]
centers_y = [2] * 6 + [0] * 4
box_x = [(0, 0, 1, 1)] + [(1.5, 1.5, 2.5, 2.5), (2.7, 2.7, 3.7, 3.7)] * 2
box_y = [(1.5, 2.5, 2.5, 1.5)] * 3 + [(-0.5, 0.5, 0.5, -0.5)] * 2
ghost_x = [(3.1, 3.1, 4.1, 4.1)] * 2
ghost_y = [(1.3, 2.3, 2.3, 1.3), (-0.7, 0.3, 0.3, -0.7)]
# cue AB target O foils DEGPUV
box_l = ['AA', 'AU', 'E', 'O', 'P', 'O', 'P', 'V', 'D', 'E']
color = [maintcol, switchcol] + [lettercol] * 8
bcolor = [cuecol] + [malecol] * 2 + [femalecol] * 2
ecolor = ['k'] + ['none'] * 4
wt = ['normal'] * 2 + ['bold'] * 8
ha = ['left', 'right'] + ['center'] * 8
for x, y in zip(ghost_x, ghost_y):
    ax.fill(x, y, '0.95', edgecolor='0.6', alpha=0.85, zorder=3, linewidth=0.6,
            linestyle='dashed')
for x, y, b, e in zip(box_x, box_y, bcolor, ecolor):
    ax.fill(x, y, b, alpha=1, zorder=4, edgecolor=e, linewidth=0.5)
for x, y, s, c, h, w in zip(centers_x, centers_y, box_l, color, ha, wt):
    ax.text(x, y - 0.04, s, ha=h, va='center', color=c, weight=w, zorder=5)
ax.vlines([2., 3.2], ymin=-0.5, ymax=2.5, zorder=5, color='w', linewidth=1)
ax.text(0.5, 2, '/', color=slashcol, ha='center', va='center', zorder=5)

# params for ghost elements
ghost = dict(alpha=0.6, linestyle='dashed', zorder=1, clip_on=False)

# switch gap 1 (long)
bot = -3.15
ht = 1.15
top = bot + ht
lwd = 0.6
rect = plt.Rectangle((2.5, bot), width=0.6, height=ht, fill=False,
                     linewidth=lwd, edgecolor=gapcol, **ghost)
yy = tile([bot + ht, bot], (6, 1))
xx = [(x, x + 0.1) for x in linspace(2.5, 3., 6)]
_ = [plt.plot(x, y, linewidth=lwd, color=gapcol, solid_capstyle='butt',
              **ghost) for x, y in zip(xx, yy)]
ax.add_artist(rect)
# switch gap 2 (short)
rect = plt.Rectangle((2.5, bot), width=0.2, height=ht, zorder=4, fill=False,
                     linewidth=lwd, edgecolor=gapcol, clip_on=False)
yy = tile([bot + ht, bot], (6, 1))
xx = [(x, x + 0.1) for x in (2.5, 2.6)]
_ = [plt.plot(x, y, linewidth=lwd, color=gapcol, solid_capstyle='butt',
              zorder=4, clip_on=False) for x, y in zip(xx, yy)]
ax.add_artist(rect)
ax.set_clip_on(False)
ax.text(2.525, -4.8, 'variable-length\nswitch gap', ha='left', va='bottom',
        fontsize=10, color=gapcol)

# timing slots
h = 0.55
w = 0.9
y = -2.85
for ix, x in enumerate([3.2, 3.7]):
    y_offset = -0.2 * (ix % 2)
    h_offset = 0.04 * (1 - ix % 2)
    rect = plt.Rectangle((x, y + y_offset), width=w, height=h + h_offset,
                         fill=False, linewidth=lwd, edgecolor=slotcol, **ghost)
    ax.add_artist(rect)
for ix, x in enumerate([1.6, 2.1, 2.8, 3.3]):
    y_offset = -0.2 * (ix % 2)
    rect = plt.Rectangle((x, y + y_offset), width=w, height=h, zorder=3,
                         facecolor=slotcol, alpha=0.5, edgecolor='none',
                         fill=True, clip_on=False)
    ax.text(x + 0.05, y + y_offset + 0.225, str(ix + 1), ha='left',
            va='center', weight='bold', fontsize=7.5, color='w', zorder=4)
    ax.add_artist(rect)
ax.text(1.6, -4.8, 'response\ntiming slots', ha='left', va='bottom',
        fontsize=10, color=slotcol, zorder=4)

# captions
ax.text(0.5, 3.5, 'Cue', color='k', fontsize=11, ha='center', va='center')
ax.text(2.8, 3.5, 'Concurrent target and masker streams', color='k',
        fontsize=11, ha='center', va='center', weight='normal')
ax.text(1.5, 2.55, 'male', color=malecol, fontsize=9, ha='left', va='baseline',
        weight='bold')
ax.text(1.5, 0.55, 'female', color=femalecol, fontsize=9, ha='left',
        va='baseline', weight='bold')

# timeline
arr_y = -2.3
arr_xmax = 4.7
tcklen = 0.25
ticktimes = [0, 1, 1.5, 2.0, 2.5, 2.7, 3.2, 3.7]
ticklabels = [str(tt) for tt in ticktimes]
tickcols = ['k'] * len(ticktimes)
ticksizes = [9] * len(ticktimes)
_ = ax.vlines(ticktimes, arr_y - tcklen, arr_y + tcklen, linewidths=0.5,
              zorder=5, colors=tickcols)
_ = [ax.text(x, y, s, ha='center', va='baseline', fontsize=z, color=c)
     for x, y, s, c, z in zip(ticktimes, [arr_y + 2 * tcklen] * len(ticktimes),
                              ticklabels, tickcols, ticksizes)]
arr = ax.arrow(-0.2, arr_y, arr_xmax, 0, head_width=0.4, head_length=0.15,
               fc='k', ec='k', linewidth=0.5, zorder=5)
plt.annotate('time (s)', (arr_xmax, arr_y),  xytext=(3, 0), fontsize=9,
             textcoords='offset points', ha='left', va='center')
# finalize
plt.ylim(-2.8, 4.8)
plt.xlim(-0.1, 5)
fig.savefig('fig-trial-voc.pdf')
