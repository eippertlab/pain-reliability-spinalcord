#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
numpy version: 1.23.3
matplotlib version: 3.6.3
pingouin version: 0.5.3
"""

#%% Import Modules
import pandas as pd
import seaborn as sns
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as patches
import glob
from pathlib import Path
import pingouin as pg

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/ReliabilityRun/physio/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Import data
data = [] 
x = np.linspace(-1, 10, num=1100)  
# Subjects to exclude
excluded_subjects = {16, 39}

# Loop over subjects
for subject in range(1, 41):
    if subject in excluded_subjects:
        continue
    sub = f'sub-{str(subject).zfill(2)}'
    print('subject: ', sub)
    for session in range(1, 3):
        ses = f'ses-{str(session).zfill(2)}'
        print('session: ', ses)
        # Define directory and files
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/physio/scr/'
        file_pattern = f'{data_dir}{sub}_{ses}_scr_epochs_ReliabilityRun.csv'
        files = glob.glob(file_pattern)
        for file in files:
            tmp = pd.read_csv(file, header=None)
            tmp['sub'] = sub
            tmp['ses'] = ses
            tmp['epoch'] = tmp.index
            tmp['x'] = x[:len(tmp)]
            tmp2 = tmp.melt(id_vars=['sub', 'ses', "epoch", 'x'], var_name="trial")
            data.append(tmp2)

# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
# store as variables to avoid loading every time
pd.to_pickle(data, f'{out_dir}scr_ReliabilityRun.pickle')

#%% Load variables    
data = pd.read_pickle(f'{out_dir}scr_ReliabilityRun.pickle')
ids = data["sub"].unique()
sub_n = len(ids)
epochs = data.epoch.unique()

#%% Prep the data
overall_max = data.value.max()
data['val_scaled'] = data.value/overall_max;

data_session_sub = data.groupby(["sub","ses", "epoch"],as_index=False).mean().reset_index()
data_epoch = data_session_sub.groupby(["sub","epoch"],as_index=False).mean().reset_index()
data_overall = data_epoch.groupby(["epoch"]).mean().reset_index()
data_overall['sd'] = data_epoch.groupby(["epoch"], as_index=False).std().val_scaled
data_overall['sem'] = data_overall['sd']/sqrt(sub_n)

data_session = data_session_sub.groupby(["epoch", "ses"], as_index=False).mean().reset_index()
data_session['sd'] = data_session_sub.groupby(["epoch", "ses"], as_index=False).std().val_scaled
data_session['sem'] = data_session['sd']/sqrt(sub_n)

#%% Reliability and ttest between peaks,
#for scr look for peak between 0 and 8s relative to heat onset
#for pupil look for peak between 0 and 4 seconds relative to heat onset
data_sample = data[(data["epoch"]>=100)&(data["epoch"]<900)] #the interval is 11 second long, goes from -1 to 1000, so this is taking 0 to 8 seconds
data_sample_max = data_sample.groupby(["sub","ses","trial"])["val_scaled"].max().reset_index()
data_sample_max_avg = data_sample_max.groupby(["sub","ses"])["val_scaled"].mean().reset_index()
#Reliability
reliability= pg.intraclass_corr(data=data_sample_max_avg, targets="sub", raters="ses", ratings="val_scaled")
data_sample_max_avg.to_csv(f'{out_dir}peak_scr_ReliabilityRun.csv')
#Difference
data_ttest = data_sample_max_avg.pivot_table(values="val_scaled", columns="ses", index="sub")
ttest = pg.ttest(data_ttest["ses-01"], data_ttest["ses-02"], paired=True)

#%% Figure 2. Subjective and peripheral physiological responses, SCR
x = pd.Series(np.linspace(-1, 10, num=1100))
color_avg = "darkgreen"
color_ses1 = "#d95f02"
color_ses2 = "#7570b3"
    
ylim_lo = -0.02
ylim_hi = 0.1
ylim_dist = ylim_hi -ylim_lo

rect = patches.Rectangle((0,ylim_lo), 1, ylim_dist, linewidth=1, edgecolor='#9c96a4', facecolor="#9c96a4", alpha=0.2, label="Heat")
rect2 = patches.Rectangle((0,ylim_lo), 1, ylim_dist, linewidth=1, edgecolor='#9c96a4', facecolor='#9c96a4', alpha=0.2, label='_nolegend_')

mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8)  
with sns.plotting_context('paper', font_scale = 2): 
    #overall 
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, 
                                   constrained_layout=True,
                                   figsize=(11,4))
    fig.suptitle("Heat effect on SCR", y=1.2, size=30)
    ax1.add_patch(rect)
    ax1.plot(x, data_overall.val_scaled, color=color_avg, label="Both days")
    ax1.fill_between(x, 
                     (data_overall['val_scaled'] - data_overall['sem']), 
                     data_overall['val_scaled'] + data_overall['sem'], color=color_avg, alpha=0.25, label='_nolegend_')

    ax1.set_ylim(ylim_lo, ylim_hi)
    #ax1.set_yticks([-0.01, 0, 0.01, 0.02, 0.03, 0.04])
    ax1.set_xticks([0, 2, 4, 6, 8, 10])
    ax1.set_xlabel('Time in s', labelpad=10, size=15)
    ax1.set_ylabel('SCR in μS', size=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax1.spines[axis].set_linewidth(0.5)
    ax2 = fig.add_subplot(1, 2, 2)
    ses1 = data_session.query("ses=='ses-01'")
    ses2 = data_session.query("ses=='ses-02'")
    ax2.plot(x, ses1.val_scaled, color=color_ses1, label="Day 1")
    ax2.plot(x, ses2.val_scaled, color=color_ses2, label="Day 2")
    ax2.fill_between(x, 
                     (ses1['val_scaled'] - ses1['sem']), 
                     ses1['val_scaled'] + ses1['sem'], color=color_ses1, alpha=0.25, label='_nolegend_')
    ax2.fill_between(x, 
                     (ses2['val_scaled'] - ses2['sem']), 
                     ses2['val_scaled'] + ses2['sem'], color=color_ses2, alpha=0.25, label='_nolegend_')
    ax2.add_patch(rect2)
    ax2.set_ylim(ylim_lo, ylim_hi)
    #ax2.set_yticks([-0.01, 0, 0.01, 0.02, 0.03, 0.04])
    ax2.set_yticklabels(["", "", "", "", "", ""])
    ax2.set_xticks([0, 2, 4, 6, 8, 10])
    ax2.set_xlabel('Time in s', labelpad=10, size=15)
    #ax2.set_ylabel('Pupil dilation (a.u.)', size=15, labelpad=5)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax2.spines[axis].set_linewidth(0.5)
    plt.savefig(f'{out_dir}heateffect_scr_ReliabilityRun.png', bbox_inches='tight', format="png")
    plt.show()
