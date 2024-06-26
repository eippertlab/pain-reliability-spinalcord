#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
"""

#%% Import Modules
import pandas as pd
import warnings
from pathlib import Path
import glob
warnings.filterwarnings("ignore")

#%% Functions
def retain_quantile(data, percentile=0.9):
    percentile_val = data[3].quantile(percentile)
    return data[data[3] >= percentile_val]

#%% For reliability: Summaries
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/DHR/reliability/'
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
        run_dir = glob.glob(f'{project_dir}/derivatives/{sub}/{ses}/func/glm/DHR/*acq-te40ReliabilityRun*.feat')[0]
        data_dir = f'{run_dir}/stats/normalization/extracts/'
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
pd.to_pickle(data, f'{out_dir}cope_DHR.pickle')

#%% All individual values
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/DHR/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)
rois=['dh_left_c6']
data= []
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        #Define subject directories and ROIs
        run_dir = glob.glob(f'{project_dir}/derivatives/{sub}/{ses}/func/glm/DHR/*acq-te40ReliabilityRun*.feat')[0]
        data_dir = f'{run_dir}/stats/normalization/extracts/'
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
pd.to_pickle(data, f'{out_dir}all_stats_DHR.pickle')
