#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
ptitprince version: 0.2.6
seaborn version: 0.11.0
matplotlib version: 3.6.3
"""
#%% Import Modules
import pandas as pd
import ptitprince as pt
import seaborn as sns
import matplotlib.pyplot as plt
import glob
#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/physio/'
#%% Import data
data = [] 
excluded_subjects = {3, 31}

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
        data_dir = f'{project_dir}{sub}/{ses}/func/'
        file_pattern = f'{data_dir}{sub}*ReliabilityRun*events.tsv'
        files = glob.glob(file_pattern)
        for file in files:
            df = pd.DataFrame()
            run = next((r for r in ["run-01", "run-02", "run-03", "run-04", "run-05"] if r in file), None) 
            tmp = pd.read_csv(file, sep="\t")
            df["value"] = [tmp["rating"][0]]
            df["sub"] = sub
            df["ses"] = ses
            #df["run"] = run     
            data.append(df)

# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
# store as variables to avoid loading every time
pd.to_pickle(data, f'{out_dir}rating_ReliabilityRun.pickle')
#%% import data
ratings = pd.read_pickle(f'{out_dir}rating_ReliabilityRun.pickle')
ids = ratings["sub"].unique()
for sub in ids:
    avg = (ratings[(ratings["sub"]==sub)&(ratings["ses"]=="ses-01")]["value"].values[0] + 
                  ratings[(ratings["sub"]==sub)&(ratings["ses"]=="ses-02")]["value"].values[0])/2
    ratings = ratings.append({"sub":sub, "ses":"Average","value":avg}, ignore_index=True)
#%%
ratings["Session_num_shift"] = ratings["ses"].replace('ses-02',2.15)
ratings["Session_num_shift"] = ratings["Session_num_shift"].replace('ses-01', 1.15)
ratings["Session_num_shift"] = ratings["Session_num_shift"].replace('Average', 0.15)
#%%
ratings["Session_num"] = ratings["ses"].replace('ses-02', str(2))
ratings["Session_num"] = ratings["Session_num"].replace('ses-01', str(1))
ratings["Session_num"] = ratings["Session_num"].replace('Average', str(0))
ratings["Session_num"] = ratings['Session_num'].astype(float)
#%%
import numpy as np
np.random.seed(10)
jitter = 0.1
ratings = ratings.assign(x_new = lambda df: df.Session_num_shift + (np.random.random(df.Session_num_shift.size))*jitter-0.02,
                         y_new = lambda df: df.value + (np.random.random(df.value.size))-0.5)
#%% Figure 2. Subjective and peripheral physiological responses; Rating
my_pal2 = {0:"darkgreen", 1: "#d95f02", 2: "#7570b3"}
my_pal = {"Average":"darkgreen", "ses-01": "#d95f02", "ses-02": "#7570b3"}
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=1.8)
sns.set_style('ticks')  
colors = ["darkgreen","#d95f02","#7570b3"]
#create normal distribution curve
with sns.plotting_context('paper', font_scale = 2): 
    f, ax = plt.subplots(figsize=(7, 8))
    ax=pt.half_violinplot( x = "Session_num", y = "value", data = ratings, 
                          bw = .15, cut = 2,
                          scale = "area", width = .4, inner = None, orient = "v", 
                          alpha=0.25, palette=my_pal2)
    sns.boxplot( x = "Session_num", y = "value", data = ratings, color = "black", width = .1, zorder = 10,\
                showcaps = False, boxprops = {'facecolor':'none', "zorder":10},\
                showfliers=True, whiskerprops = {'linewidth':2, "zorder":10},\
                    saturation = 1, orient = "v",ax=ax)
    p = 0
    for violin in ax.collections:
       violin.set_edgecolor(None)
    for box in ax.patches:
    #print(box.__class__.__name__)
        if box.__class__.__name__ == 'PathPatch':
            if p == 0:
                box.set_edgecolor('darkgreen')
                box.set_facecolor('white')
                for k in range(3*p,3*(p+1)):
                    ax.lines[k].set_color('darkgreen')
                p += 1
            elif p == 1:
                box.set_edgecolor('#d95f02')
                box.set_facecolor('white')
                for k in range(4*p,4*(p+1)):
                    ax.lines[k].set_color('#d95f02')
                p +=1
            elif p == 2:
                box.set_edgecolor('#7570b3')
                box.set_facecolor('white')
                for k in range(4*p,4*(p+1)):
                    ax.lines[k].set_color('#7570b3')
                p +=1
    ax.scatter(x = ratings["x_new"], y = ratings["y_new"], 
               color="grey", alpha=0.6, s=15)
    plt.ylim(30,100)
    plt.yticks([30, 40, 50, 60, 70, 80, 90, 100])
    ax.axhline(y=50, color='red', linestyle='--', label="Pain threshold")
    #plt.legend(
    markers = [plt.Line2D([0],[0],color=color, linewidth=2, alpha=0.5) for color in my_pal.values()]
    plt.legend(markers, my_pal.keys(), numpoints=1, prop={'size': 10}, bbox_to_anchor=(1,1))
    
    plt.xlabel(None)
    for axis in ['bottom', 'left']:
        ax.spines[axis].set_linewidth(0.5)
    ax.spines[['right', 'top']].set_visible(False)
    plt.savefig(f'{out_dir}heateffect_rating_ReliabilityRun.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
