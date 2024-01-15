#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
"""
#%% Modules
import pandas as pd
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

#%% Functions
def retain_quantile(data, percentile=0.9):
    percentile_val = data[3].quantile(percentile)
    return data[data[3] >= percentile_val]

#%% For reliability
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/WithinRun/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois=['dh_left_c6', 'c6_dl_dil', 'vh_right_c6', 'c6_vr_dil']
data= []
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        for within_type in ["early", "late", "odd", "even"]:
            #Define subject directories and ROIs
            data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/glm/WithinRun/{within_type}.feat/stats/normalization/extracts/'
            for roi in rois:
                for stat in ['cope1', 'zstat1']:
                    tmp=pd.read_csv(f'{data_dir}{stat}_{roi}_m.txt' , header=None, names=["avg"], delim_whitespace=True)
                    tmp1=pd.read_csv(f'{data_dir}{stat}_{roi}_min_max.txt' , header=None, delim_whitespace=True)
                    tmp['max'] = tmp1.iloc[0,1]
                    tmp2 = pd.read_csv(f'{data_dir}{stat}_{roi}_all.txt' , header=None, delim_whitespace=True).transpose()
                    tmp2 = retain_quantile(tmp2).reset_index(drop=True)
                    tmp['top10'] = tmp2[3].mean()
                    tmp['sub'] = sub
                    tmp['ses'] = ses
                    tmp['roi'] = roi
                    tmp['stat'] = stat
                    tmp["subset"] = within_type
                    data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}cope_WithinRun.pickle')

#%% All individual values
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/WithinRun/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois=['dh_left_c6']
data= []
for subject in range(1, 5):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        for within_type in ["early", "late", "odd", "even"]:
            #Define subject directories and ROIs
            data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/glm/WithinRun/{within_type}.feat/stats/normalization/extracts/'
            for roi in rois:
                for stat in ['cope1', 'zstat1']:
                    tmp=pd.read_csv(f'{data_dir}{stat}_{roi}_all.txt', header=None, delim_whitespace=True).transpose()
                    tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
                    tmp['sub'] = sub
                    tmp['ses'] = ses
                    tmp['roi'] = roi
                    tmp['stat'] = stat
                    tmp["subset"] = within_type
                    data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}all_stats_WithinRun.pickle')

#%% Prepare physio data for WithinRun Reliability
#Directory
physio_dir = f'{project_dir}derivatives/results/ReliabilityRun/physio/'
out_dir = f'{project_dir}derivatives/results/WithinRun/reliability/'

#Load data
scr = pd.read_pickle(f'{physio_dir}scr_ReliabilityRun.pickle')
pdr = pd.read_pickle(f'{physio_dir}pupil_ReliabilityRun.pickle')
hpr = pd.read_pickle(f'{physio_dir}hpr_ReliabilityRun.pickle')

#modify data
modalities = [scr, pdr, hpr]  # List of your dataframes
modality_names = ['scr', 'pdr', 'hpr']  # Corresponding names for the modalities
combined_dfs = {}

for modality, modality_name in zip(modalities, modality_names):
    overall_max = modality.value.max()
    modality['val_scaled'] = modality.value/overall_max;
    if modality_name=="hpr":
        data_sample = modality[(modality["epoch"]>=100)&(modality["epoch"]<900)] #the interval is 11 second long, goes from -1 to 1000, so this is taking 0 to 8 seconds
        data_sample_max = data_sample.groupby(["sub","ses","trial"])["val_scaled"].min().reset_index()
    elif modality_name=="pdr":
        data_sample = modality[(modality["epoch"]>=100)&(modality["epoch"]<500)] #the interval is 11 second long, goes from -1 to 1000, so this is taking 0 to 8 seconds
        data_sample_max = data_sample.groupby(["sub","ses","trial"])["val_scaled"].max().reset_index()
    elif modality_name=="scr":
        data_sample = modality[(modality["epoch"]>=100)&(modality["epoch"]<900)] #the interval is 11 second long, goes from -1 to 1000, so this is taking 0 to 8 seconds
        data_sample_max = data_sample.groupby(["sub","ses","trial"])["val_scaled"].max().reset_index()
    data_sample_max["trial"] = data_sample_max["trial"]+1
    data_sample_max['odd'] = (data_sample_max['trial'] % 2).astype(int)
    data_sample_max['even'] = (data_sample_max['trial'] % 2 == 0).astype(int)
    data_sample_max['early'] = data_sample_max['trial'].between(1, 10).astype(int)
    data_sample_max['late'] = data_sample_max['trial'].between(11, 20).astype(int)

    avg_max_odd = data_sample_max[data_sample_max['odd'] == 1].groupby(['sub', 'ses'])['val_scaled'].mean().reset_index()
    avg_max_even = data_sample_max[data_sample_max['even'] == 1].groupby(['sub', 'ses'])['val_scaled'].mean().reset_index()
    avg_max_early = data_sample_max[data_sample_max['early'] == 1].groupby(['sub', 'ses'])['val_scaled'].mean().reset_index()
    avg_max_late = data_sample_max[data_sample_max['late'] == 1].groupby(['sub', 'ses'])['val_scaled'].mean().reset_index()

    avg_max_odd['subset'] = 'odd'
    avg_max_even['subset'] = 'even'
    avg_max_early['subset'] = 'early'
    avg_max_late['subset'] = 'late'

    # Concatenate all the dataframes
    combined_df = pd.concat([avg_max_odd, avg_max_even, avg_max_early, avg_max_late])
    combined_df.to_csv(f'{out_dir}{modality_name}_WithinRun.csv')
