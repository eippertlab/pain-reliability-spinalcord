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
out_dir = f'{project_dir}derivatives/results/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois=['dh_left_c6', 'c6_dl_dil', 'vh_right_c6', 'c6_vr_dil']
data= []
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        #Define subject directories and ROIs
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/glm/ReliabilityRun.feat/stats/normalization/extracts/'
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
                data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}cope_ReliabilityRun.pickle')

#%% All individual values
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois=['dh_left_c6']
data= []
for subject in range(1, 5):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        #Define subject directories and ROIs
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/glm/ReliabilityRun.feat/stats/normalization/extracts/'
        for roi in rois:
            for stat in ['cope1', 'zstat1']:
                tmp=pd.read_csv(f'{data_dir}{stat}_{roi}_all.txt', header=None, delim_whitespace=True).transpose()
                tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
                tmp['sub'] = sub
                tmp['ses'] = ses
                tmp['roi'] = roi
                tmp['stat'] = stat
                data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}all_stats_ReliabilityRun.pickle')

#%% For spatial specificity, average over both sessions
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/glm/ReliabilityRun/cord/'
out_dir = f'{project_dir}derivatives/results/spatial_specificity/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois_horns = ['dh_left', 'dh_right', 'vh_left', 'vh_right']
rois_quadrants = ['dr', 'vr', 'dl', 'vl']
roi_choice = [rois_horns, rois_quadrants]
levels = ['c5', 'c6', 'c7', 'c8']
data= []
for roi_choice in roi_choice:
    for roi in range(4):
        for level in levels:
            tmp=pd.read_csv(f'{data_dir}{level}_{roi_choice[roi]}_vox_p_all.txt', header=None, delim_whitespace=True).transpose()
            tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
            tmp['level'] = level
            tmp['roi'] = roi_choice[roi]
            data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}cord_p_uncorr.pickle')

#%% For spatial specificity, single sessions for dice index
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/glm/ReliabilityRun/dh_left_c6/'
out_dir = f'{project_dir}derivatives/results/spatial_specificity/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
data= []
for ses in ["ses-01", "ses-02"]:
    tmp=pd.read_csv(f'{data_dir}dh_left_c6_{ses}_vox_p_all.txt', header=None, delim_whitespace=True).transpose()
    tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
    tmp['ses'] = ses
    data.append(tmp)
# Concatenate all dataframes at once
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}dhlc6_p_uncorr.pickle')
