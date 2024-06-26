#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
matplotlib version: 3.6.3
pingouin version: 0.5.3
ptitprince version: 0.2.6
scipy version: 1.11.4
"""
#%% Import Modules
import pandas as pd
import glob 
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib as mpl
import pingouin as pg
from pathlib import Path
import warnings

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/ReliabilityRun/quality/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% 
data= []
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        #Define subject directories and ROIs
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/preprocessing/'
        file = glob.glob(f'{data_dir}sub*ReliabilityRun*bold_denoised_moco_refined_t.txt')[0]
        tmp = pd.read_csv(file, header=None, delim_whitespace=True).transpose()
        tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
        tmp['sub'] = sub
        tmp['ses'] = ses
        data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
# store as variables to avoid loading every time
pd.to_pickle(data, f'{out_dir}tsnr_ReliabilityRun.pickle')                

#%% Load variables 
data = pd.read_pickle(f'{out_dir}tsnr_ReliabilityRun.pickle')
ids = data["sub"].unique()
sub_n = len(ids)

#%% data aggregation
data = data.groupby(["sub", "ses", "z"], as_index=False).mean()
data = data.groupby(["ses", "z"], as_index=False).agg({"val":["mean", "std"]}).reset_index() 
data.columns = ["".join(x) for x in data.columns.ravel()] 

#%% Test for differences: 
data_ttest = data.pivot_table(values="valmean", columns="ses", index="z")
data_ttest.mean()
data_ttest.std()
ttest = pg.ttest(data_ttest["ses-01"], data_ttest["ses-02"], paired=True)
print(ttest['p-val'])

#%% Fig. 6. Physiological state and data quality across days, TSNR
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white",font_scale=2.8) 
ses1_color="#d95f02"
ses2_color="#7570b3" 
with sns.plotting_context('paper', font_scale = 2.4): 
    sns.set_style('ticks') 
    warnings.filterwarnings("ignore") 
    fig, ax = plt.subplots(1, 1,   tight_layout=True,
                                   figsize=(10,5))
    ses1 = data[(data["ses"]=="ses-01")].reset_index()
    ses1["min"] = ses1["valmean"] - ses1["valstd"]
    ses1["max"] = ses1["valmean"] + ses1["valstd"]
    ses2 = data[(data["ses"]=="ses-02")].reset_index()
    ses2["min"] = ses2["valmean"] - ses2["valstd"]
    ses2["max"] = ses2["valmean"] + ses2["valstd"]

    ax.set_ylabel('tSNR within cord mask', labelpad=10)
    ax.set_ylim([10,26])
    ax.set_yticks([10,15,20,25,30, 35], fontsize=10)
    ax.set_xlim([0.5,17.5])
    plt.plot([16.3, 16.5, 16.5, 16.3], [15, 15, 30, 30], lw=1.5, c="darkgrey")
    plt.text((17), 22, "ns", ha='center', va='bottom', color="black", fontsize=18)
    
    ax.set_xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], fontsize=10)
    ax.plot("z", "valmean", data=ses1, color=ses1_color, label="Day 1",linestyle='-', marker=None, lw=2)
    ax.plot("z", "valmean", data=ses2, color=ses2_color, label="Day 2", linestyle='-', marker=None, lw=2)
    ax.fill_between("z","min", "max", data=ses1, alpha=0.2, color=ses1_color)
    ax.fill_between("z","min", "max", data=ses2, alpha=0.2, color=ses2_color)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
              ncol=1, labels=["Day 1", "Day 2"], fontsize=15)
    ax.get_legend().remove()
    plt.xlabel('Slice', labelpad=10, size=20)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.5)
    plt.savefig(f'{out_dir}TSNR_ReliabilityRun.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
