#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
numpy version: 1.23.3
scipy version: 1.9.1
pandas version: 1.5.0
matplotlib version: 3.6.3
seaborn version: 0.11.0
pingouin version: 0.5.3
"""
#%% Import modules
import os
import glob
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as patches
import matplotlib as mpl
import seaborn as sns
from math import sqrt
from pathlib import Path
import pingouin as pg

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/physio/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
#%% Epoch and finalize data
hpr = []
#Loop over sessions
for session in range (1,3):
    ses = 'ses-' + str(session).zfill(2)
    for subject in range(1, 41): 
        sub = 'sub-' + str(subject).zfill(2)
        print('subject: ',sub)
        print('session: ',ses)
        data_dir = f'{project_dir}derivatives/{sub}/{ses}/physio/'
        result_dir = f'{data_dir}heart/'
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        physio_files = glob.glob(f'{data_dir}*ReliabilityRun*physio.tsv')
        physio_files = np.array(sorted(physio_files))
        run = next((r for r in ["run-01", "run-02", "run-03", "run-04", "run-05"] if r in physio_files[0]), None) 
        print(run)
        
        baseline = (-5, 0)  # interval for baseline correction
        interval = (-1, 10)  # interval for epoch
        sr = 1000
        
        #get data
        data = pd.read_csv(physio_files[0], sep="\t")
        ecg_events_new = data[data['Rpeak'] == 1].index.values
        average_pulse_new = 60/(np.diff(ecg_events_new).mean()/sr)
        first_real_event_new = np.where(data["Rpeak"] == 1)[0][0]
                
        # convert into heart period
        new_sr = 100
        num_samples = data.shape[0]
        hb = np.array([r/sr for r in ecg_events_new[:]]) 
        ibi = np.diff(hb)
        idx = (ibi > 0.5) & (ibi < 1.6)  # limits for realistic values
        hp = ibi * 1000  # in ms
        new_time = np.arange(1.0 / new_sr, (num_samples - 1) / sr, 1 / new_sr)
        X = hb[np.where(idx)[0] + 1]
        Y = hp[idx]
        interfunc = RegularGridInterpolator([X], Y, method='linear', bounds_error=False, fill_value=None)
        heart_period = interfunc(new_time)
       
        # convert events to seconds
        new_events = data[data['stim'] == 1].index.values / sr
        
        # another bandpass filter (Castagnetti et al 2016 Psychophysiology; Paulus et al., 2016)
        b, a = signal.butter(2, (0.01, 0.5), btype='bandpass', fs=new_sr)
        heart_period = signal.filtfilt(b, a, heart_period)
        
        
        # epoching and baseline correction
        for e, event in enumerate(new_events):
            baseline_value = np.mean(heart_period[int((event + baseline[0]) * new_sr):
                                                  int((event + baseline[1]) * new_sr)], axis=0)
           
            hp_epo = heart_period[int((event + interval[0]) * new_sr):
                                  int((event + interval[1]) * new_sr)] - baseline_value
            hp_epo = hp_epo - hp_epo[-interval[0]*new_sr]  
            hp_epo = pd.DataFrame(hp_epo, columns=["value"])
            hp_epo['sub'] = sub
            hp_epo['ses'] = ses
            hp_epo['run'] = run
            hp_epo['trial'] = e
            hp_epo['epoch'] = hp_epo.index
            hp_epo['x'] = np.arange(1100) 
            hpr.append(hp_epo)
data = pd.concat(hpr, ignore_index=True)
pd.to_pickle(data, f'{out_dir}hpr_ReliabilityRun.pickle')

#%% Load variables    
data = pd.read_pickle(f'{out_dir}hpr_ReliabilityRun.pickle')
ids = data["sub"].unique()
sub_n = len(ids)
epochs = data.x.unique()

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
data_sample_max_avg.to_csv(f'{out_dir}peak_hpr_ReliabilityRun.csv')
#Difference
data_ttest = data_sample_max_avg.pivot_table(values="val_scaled", columns="ses", index="sub")
ttest = pg.ttest(data_ttest["ses-01"], data_ttest["ses-02"], paired=True)

#%% Figure 2. Subjective and peripheral physiological responses, HPR
x = pd.Series(np.linspace(-1, 10, num=1100))
    
color_avg = "darkgreen"
color_ses1 = "#d95f02"
color_ses2 = "#7570b3"

mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8)  

ylim_lo = -0.2
ylim_hi = 0.2
ylim_dist = ylim_hi -ylim_lo

rect = patches.Rectangle((0,ylim_lo), 1, ylim_dist, linewidth=1, edgecolor='#9c96a4', facecolor="#9c96a4", alpha=0.2, label="Heat")
rect2 = patches.Rectangle((0,ylim_lo), 1, ylim_dist, linewidth=1, edgecolor='#9c96a4', facecolor='#9c96a4', alpha=0.2, label='_nolegend_')

with sns.plotting_context('paper', font_scale = 2): 
    #overall 
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, 
                                   constrained_layout=True,
                                   figsize=(11,4))
    fig.suptitle("Heat effect on HPR", y=1.2, size=30)
    ax1.add_patch(rect)
    ax1.plot(x, data_overall.val_scaled, color=color_avg, label="Both days")
    ax1.fill_between(x, 
                     (data_overall['val_scaled'] - data_overall['sem']), 
                     data_overall['val_scaled'] + data_overall['sem'], color=color_avg, alpha=0.25, label='_nolegend_')

    ax1.set_ylim(ylim_lo, ylim_hi)
    #ax1.set_yticks([0, 0.005, 0.01, 0.015, 0.02])
    ax1.set_xticks([0, 2, 4, 6,8, 10])
    ax1.set_xlabel('Time in s', labelpad=5, size=15)
    ax1.set_ylabel('Pupil dilation (a.u.)', size=15)
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
    ax2.set_ylim(ylim_lo, ylim_hi )
    #ax2.set_yticks([0, 0.01, 0.02])
    #ax2.set_yticklabels([" "," "," "])
    ax2.set_xticks([0, 2, 4, 6,8, 10])
    ax2.set_xlabel('Time in s', labelpad=5, size=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax2.spines[axis].set_linewidth(0.5)
    plt.savefig(f'{out_dir}heateffect_hpr_ReliabilityRun.png', bbox_inches='tight', format="png")
    plt.show()
