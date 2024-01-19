#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
numpy version: 1.23.3
seaborn version: 0.11.0
matplotlib version: 3.6.3
pingouin version: 0.5.3
ptitprince version: 0.2.6
scipy version: 1.11.4
"""
#%% Import Modules
import pandas as pd
import numpy as np
import glob 
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib as mpl
import pingouin as pg
from pathlib import Path
import warnings

#%% Functions
def timedomain(rr):
    results = {}
    hr = 60000/rr
    results['Mean_RR(ms)'] = np.mean(rr)
    results['STD_RR/SDNN(ms)'] = np.std(rr)
    results['Mean_HR(Kubios\' style) (beats/min)'] = 60000/np.mean(rr)
    results['Mean_HR(beats/min)'] = np.mean(hr)
    results['STD_HR(beats/min)'] = np.std(hr)
    results['Min_HR(beats/min)'] = np.min(hr)
    results['Max_HR(beats/min)'] = np.max(hr)
    results['RMSSD(ms)'] = np.sqrt(np.mean(np.square(np.diff(rr))))
    results['NNxx'] = np.sum(np.abs(np.diff(rr)) > 50)*1
    results['pNNxx(%)'] = 100 * np.sum((np.abs(np.diff(rr)) > 50)*1) / len(rr)
    results_df = pd.DataFrame([results])
    return results_df

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/ReliabilityRun/quality/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Import data
data = []
#Loop over sessions
for subject in range(1, 41): 
    sub = 'sub-' + str(subject).zfill(2)
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        print('subject: ',sub)
        print('session: ',ses)
        data_dir = f'{project_dir}derivatives/{sub}/{ses}/physio/'
        file = glob.glob(f'{data_dir}*ReliabilityRun*physio.tsv')[0]
        physio = pd.read_csv(file, sep="\t")
        pks = physio[physio['Rpeak'] != 0]['Rpeak'].index
        rr = np.diff(pks) #in ms
        tmp = timedomain(rr)
        tmp['sub'] = sub
        tmp['ses'] = ses
        data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
# store as variables to avoid loading every time
pd.to_pickle(data, f'{out_dir}scr_ReliabilityRun_HRinfo.pickle')
#%% Load variables 
data = pd.read_pickle(f'{out_dir}scr_ReliabilityRun_HRinfo.pickle')
ids = data["sub"].unique()
sub_n = len(ids)

#%% Test for differences
# Heart rate
data_ttest = data.pivot_table(values="Mean_HR(beats/min)", columns="ses", index="sub")
data_ttest.mean()
data_ttest.std()
ttest = pg.ttest(data_ttest["ses-01"], data_ttest["ses-02"], paired=True)
print(ttest['p-val'])       
# Heart rate variability
data_ttest = data.pivot_table(values="RMSSD(ms)", columns="ses", index="sub")
data_ttest.mean()
data_ttest.std()
ttest = pg.ttest(data_ttest["ses-01"], data_ttest["ses-02"], paired=True)
print(ttest['p-val'])  

#%% prepare for plotting
data["x_bp"] = data["ses"].replace('ses-01',1)
data["x_bp"] = data["x_bp"].replace('ses-02', 2)
data["x_hv"] = data["ses"].replace('ses-01',0.75)
data["x_hv"] = data["x_hv"].replace('ses-02', 2.25)
data["x_l"] = data["ses"].replace('ses-01',1.25)
data["x_l"] = data["x_l"].replace('ses-02', 1.75)
space = 6
order_violin = [['ses-01'], [None]*(space + 2), ['ses-02']]
order_violin = [item for sublist in order_violin for item in sublist]
order_box = [[None], ['ses-01'], [None]*(space), ['ses-02'], [None]]
order_box = [item for sublist in order_box for item in sublist]
data['X'] = 2
data.X[data.ses=='ses-02'] = space + 1
#%% Fig. 5. Physiological state and data quality across days, HRV
my_pal = {"ses-01": "#d95f02", "ses-02": "#7570b3"}
warnings.filterwarnings("ignore") 
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2): 
    f, ax = plt.subplots(figsize=(5, 6))
    sns.violinplot(x = 'ses', y='RMSSD(ms)', hue = 'ses', data=data, split=True, 
                   inner=None, bw=0.4,
                    palette=my_pal, legend=False, width=2, order=order_violin, linewidth=0)
    plt.setp(ax.collections, alpha=.6)
    sns.boxplot(x='ses', y='RMSSD(ms)', data=data, width=0.7, 
                ax=ax, order=order_box, showcaps = False, boxprops = {'facecolor':'none'},
                showfliers=True, flierprops=dict(markerfacecolor='0.75', markersize=1, marker="o", linestyle='none'), 
                )
    p = 0
    for box in ax.patches:
        #print(box.__class__.__name__)
        if box.__class__.__name__ == 'PathPatch':
            if p % 2 == 0:
                box.set_edgecolor('#d95f02')
                box.set_facecolor('white')
                for k in range(3*p,3*(p+1)):
                    ax.lines[k].set_color('#d95f02')
                p += 1
            else:
                box.set_edgecolor('#7570b3')
                box.set_facecolor('white')
                for k in range(4*p,4*(p+1)):
                    ax.lines[k].set_color('#7570b3')
                p +=1
    
    plt.xlim(-2,(space + 4.5))
    sns.lineplot(data=data, x="X", y="RMSSD(ms)", units="sub", color=".7", estimator=None, lw=1)
    plt.xticks([1,8])
    plt.xlabel(None)
    plt.ylabel("Heart rate variability (ms)", labelpad=15)
    plt.xlabel(None)
    ax.set_xticklabels(["Day 1", "Day 2"])
    plt.plot([1, 1, 8, 8], [220,225, 225, 220], lw=1.5, c="darkgrey")
    plt.text((4.5), 225, "n.s.", ha='center', va='bottom', color="black", fontsize=18)
    ax.get_legend().remove()
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    lines_labels = [ax.get_legend_handles_labels() for ax in f.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    plt.savefig(f'{out_dir}HRV_ReliabilityRun_rmssd.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
#%% Fig. 5. Physiological state and data quality across days, HR
my_pal = {"ses-01": "#d95f02", "ses-02": "#7570b3"}
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2): 
    f, ax = plt.subplots(figsize=(5, 6))
    sns.violinplot(x = 'ses', y='Mean_HR(beats/min)', hue = 'ses', data=data, split=True, 
                   inner=None, bw=0.4,
                    palette=my_pal, legend=False, width=2, order=order_violin, linewidth=0)
    plt.setp(ax.collections, alpha=.6)
    sns.boxplot(x='ses', y='Mean_HR(beats/min)', data=data, width=0.7, 
                ax=ax, order=order_box, showcaps = False, boxprops = {'facecolor':'none'},
                showfliers=True, flierprops=dict(markerfacecolor='0.75', markersize=1, marker="o", linestyle='none'), 
                )
    p = 0
    for box in ax.patches:
        #print(box.__class__.__name__)
        if box.__class__.__name__ == 'PathPatch':
            if p % 2 == 0:
                box.set_edgecolor('#d95f02')
                box.set_facecolor('white')
                for k in range(3*p,3*(p+1)):
                    ax.lines[k].set_color('#d95f02')
                p += 1
            else:
                box.set_edgecolor('#7570b3')
                box.set_facecolor('white')
                for k in range(4*p,4*(p+1)):
                    ax.lines[k].set_color('#7570b3')
                p +=1
    
    plt.xlim(-2,(space + 4.5))
    sns.lineplot(data=data, x="X", y="Mean_HR(beats/min)", units="sub", color=".7", estimator=None, lw=1)
    plt.xticks([1,8])
    plt.xlabel(None)
    plt.ylabel("Heart rate (beats/min)", labelpad=15)
    plt.xlabel(None)
    ax.set_xticklabels(["Day 1", "Day 2"])
    plt.plot([1, 1, 8, 8], [95,96, 96, 95], lw=1.5, c="darkgrey")
    plt.text((4.5), 96.5, "*", ha='center', va='bottom', color="black", fontsize=18)
    ax.get_legend().remove()
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    lines_labels = [ax.get_legend_handles_labels() for ax in f.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    plt.savefig(f'{out_dir}HR_ReliabilityRun_bpm.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()

