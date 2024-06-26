#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
matplotlib version: 3.6.3
"""

#%% Import Modules
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import warnings
import matplotlib as mpl
warnings.filterwarnings("ignore") 

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/ReliabilityRun/reliability/'
physio_dir = f'{project_dir}derivatives/results/ReliabilityRun/physio/'

#%% Import data
scr = pd.read_csv(f'{physio_dir}peak_scr_ReliabilityRun.csv')
scr = scr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)
pdr = pd.read_csv(f'{physio_dir}peak_pupil_ReliabilityRun.csv')
pdr = pdr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)
hpr = pd.read_csv(f'{physio_dir}peak_hpr_ReliabilityRun.csv')
hpr = hpr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)

pdr["modality"] = "pupil"
scr["modality"] = "scr"
hpr["modality"] = "hpr"
physio = pdr.append([scr, hpr]).loc[:,"sub":"modality"]

#import ratings
ratings = pd.read_pickle(f'{physio_dir}rating_ReliabilityRun.pickle')

#import copes
stats = pd.read_pickle(f'{out_dir}cope_ReliabilityRun.pickle')
copes = stats[stats["stat"]=="cope1"]
dhl = copes[copes["roi"]=="dh_left_c6"]
dl_dil = copes[copes["roi"]=="c6_dl_dil"]
vhr = copes[copes["roi"]=="vh_right_c6"]
vr_dil = copes[copes["roi"]=="c6_vr_dil"]
#%% Supplementary Figure 1. Individual values underlying ICC calculation: DHL C6 across days
dhl_w = pd.pivot_table(dhl, values="top10", index="sub", columns="ses")
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2.2): 
    f, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(data=dhl_w, x="ses-01", y="ses-02", color="dimgray", ax=ax)
    ax.set_ylim(0,4700)
    ax.set_xlim(0,4700)
    diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".6")
    ax.set_xticks([0, 1000, 2000, 3000, 4000])
    ax.set_xticklabels([0, 1000, 2000, 3000, 4000])
    ax.set_yticks([0, 1000, 2000, 3000, 4000])
    ax.set_yticklabels([0, 1000, 2000, 3000, 4000])
    plt.xlabel("Day 1", labelpad = 15)
    plt.ylabel("Day 2", labelpad=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}dhl_dotplot.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
    
#%% Supplementary Figure 1. Individual values underlying ICC calculation: Dorsal left dilated quadrant C6 across days
dl_dil_w = pd.pivot_table(dl_dil, values="top10", index="sub", columns="ses")
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2.2): 
    f, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(data=dl_dil_w, x="ses-01", y="ses-02", color="dimgray", ax=ax)
    ax.set_ylim(0,12000)
    ax.set_xlim(0,12000)
    diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".6")
    ax.set_xticks([0, 2500, 5000, 10000])
    ax.set_xticklabels([0, 2500, 5000, 10000])
    ax.set_yticks([0, 2500, 5000, 10000])
    ax.set_yticklabels([0, 2500, 5000, 10000])
    plt.xlabel("Day 1", labelpad = 15)
    plt.ylabel("Day 2", labelpad=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}dl_dil_dotplot.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
    
#%% Supplementary Figure 1. Individual values underlying ICC calculation: Peak SCR across days
scr_w = pd.pivot_table(scr, values="maxval", index="sub", columns="ses")
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white") 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2.2): 
    f, ax = plt.subplots(figsize=(6, 6))
    ax = sns.scatterplot(data=scr_w, x="ses-01", y="ses-02", color="dimgray")
    ax.set_ylim(-0.1,1.1)
    ax.set_xlim(-0.1,1.1)
    diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".6")
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels([0, 0.25, 0.5, 0.75, 1])
    plt.xlabel("Day 1", labelpad = 15)
    plt.ylabel("Day 2", labelpad=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}scr_dotplot.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
    
#%% Supplementary Figure 1. Individual values underlying ICC calculation: Peak PDR across days
pup_w = pd.pivot_table(pdr, values="value", index="sub", columns="ses")
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2.2): 
    f, ax = plt.subplots(figsize=(6, 6))
    ax = sns.scatterplot(data=pup_w, x="ses-01", y="ses-02", color="dimgray")
    ax.set_ylim(0,1500)
    ax.set_xlim(0, 1500)
    diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".6")
    ax.set_xticks([0, 500, 1000, 1500])
    ax.set_xticklabels([0, 500, 1000, 1500])
    ax.set_yticks([0, 500, 1000, 1500])
    ax.set_yticklabels([0, 500, 1000, 1500])
    plt.xlabel("Day 1", labelpad = 15)
    plt.ylabel("Day 2", labelpad=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}pdr_dotplot.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
    
#%% Supplementary Figure 1. Individual values underlying ICC calculation: HPR across days
hpr_w = pd.pivot_table(hpr, values="maxval", index="sub", columns="ses")
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8) 
sns.set_style('ticks') 
sns.set_style('ticks') 
with sns.plotting_context('paper', font_scale=2.2): 
    f, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(data=hpr_w, x="ses-01", y="ses-02", color="dimgray", ax=ax)
    ax.set_ylim(-250,0)
    ax.set_xlim(-250, 0)
    diag_line, = ax.plot(ax.get_xlim(), ax.get_ylim(), ls="--", c=".6")
    ax.set_xticks([-200, -100, 0])
    ax.set_xticklabels([-200, -100, 0])
    ax.set_yticks([-200, -100, 0])
    ax.set_yticklabels([-200, -100, 0])
    plt.xlabel("Day 1", labelpad = 15)
    plt.ylabel("Day 2", labelpad=15)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}hpr_dotplot.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
