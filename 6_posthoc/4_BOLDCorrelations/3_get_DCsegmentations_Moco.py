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
import numpy as np
import os
import numpy as np

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord"
out_dir = f'{project_dir}/derivatives/results/Posthoc/Correlations/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Import EPI segmentations
data= []
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        #Define subject directories and ROIs
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/preprocessing/normalization/'
        file = glob.glob(f'{data_dir}*te40ReliabilityRun*moco_refined_m_reg_seg_t.txt')[0]
        tmp = pd.read_csv(file, header=None, delim_whitespace=True).transpose()
        tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})
        tmp['sub'] = sub
        tmp['ses'] = ses
        data.append(tmp)
        
data = pd.concat(data, ignore_index=True)
pd.to_pickle(data, f'{out_dir}reg_segs.pickle')    

#%% Import PAM50 cord segmentations
mask_dir =  f'{project_dir}/derivatives/masks/'
file = "PAM50_cord_cut_t.txt"
pam50_cord = pd.read_csv(f'{mask_dir}{file}', header=None, delim_whitespace=True).transpose()
pam50_cord = pam50_cord.rename(columns={0:"x", 1:"y", 2:"z", 3:"val"})

#%% calculate Dice coefficients between both
dc_data = []
pam50_coor = np.array(pam50_cord[["x", "y", "z"]])

for sub in data["sub"].unique():
    print(sub)
    subset = data[data["sub"]==sub]
    ses1 = subset[subset["ses"]=="ses-01"].reset_index()
    ses2 = subset[subset["ses"]=="ses-02"].reset_index()
    ses = [ses1, ses2]
    #session 1:
    ses_string = ["ses-01", "ses-02"]
    for session in range(2):
        print(ses_string[session])
        ses_coor = np.array(ses[session][["x", "y", "z"]])
        overlap = np.sum(np.all(ses_coor[:, None, :] == pam50_coor[None, :, :], axis=2))
        voverlap = overlap
        v1 = len(ses[session])
        v2 = len(pam50_cord)
        dc = pd.DataFrame([(2*voverlap) / (v1 + v2)], columns=["dc"])
        dc["sub"] = sub
        dc["ses"] = ses_string[session]
        dc_data.append(dc)

dc_data = pd.concat(dc_data, ignore_index=True)
pd.to_pickle(dc_data, f'{out_dir}dc.pickle')    

#%% Import moco data
data = []
for subject in range(1, 41): 
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/preprocessing/outliers/'
        files = pd.DataFrame([os.path.basename(f) for f in glob.glob(data_dir+"*te40ReliabilityRun*refined_refrms2020edited.txt")])
        for file in files[0]:
            tmp = pd.read_csv(data_dir + file, header=None, names=["motion"])
            tmp["sub"] = sub
            tmp["ses"] = ses
            data.append(tmp)
data = pd.concat(data, ignore_index=True)
data_to_save = data.groupby(["sub","ses"], as_index=False).agg({"motion":["mean", "std"]}).reset_index(drop=True) 
data_to_save.columns = ["".join(x) for x in data_to_save.columns.ravel()] 
pd.to_pickle(data_to_save, f'{out_dir}moco.pickle')    
