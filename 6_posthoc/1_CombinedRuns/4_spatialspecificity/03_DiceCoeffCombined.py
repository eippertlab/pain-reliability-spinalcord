#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
numpy version: 1.23.3
"""
#%% Modules
import pandas as pd
import numpy as np

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/CombinedRuns/spatial_specificity/'

#%% Functions
def dice_coeff(df, thresh=None):
    if thresh != None:
        ses1 = df[(df["ses"]=="ses-01") & ((df["pval"] < thresh))].reset_index()
        ses2 =  df[(df["ses"]=="ses-02") & ((df["pval"] < thresh))].reset_index()
    else:
        ses1 = df[(df["ses"]=="ses-01")].reset_index()
        ses2 =  df[(df["ses"]=="ses-02")].reset_index()
    ses1_coor = np.array(ses1[["x", "y", "z"]].apply(lambda b: [b["x"], b["y"], b["z"]], axis=1))
    ses2_coor = np.array(ses2[["x", "y", "z"]].apply(lambda b: [b["x"], b["y"], b["z"]], axis=1))
    x = 0
    for n in ses1_coor:
        for i in ses2_coor:
            if n==i:
                x = x+1
    print(x)
    voverlap = x
    v1 = len(ses1)
    v2 = len(ses2)
    dc = (2*voverlap) / (v1 + v2) if (v1 + v2)!=0 else None
    return dc

#%% Second level Dice index left DH C6
data = pd.read_pickle(f'{data_dir}dhlc6_p_uncorr.pickle')
data['pval'] = 1 - data['val']
data_thresh_001 = data[data['pval']<0.001]
data_thresh_05 = data[data['pval']<0.05]
data[data['pval']<0.001].groupby(["ses"]).count()
data[data['pval']<0.05].groupby(["ses"]).count()
data[data['pval']<0.1].groupby(["ses"]).count()

#%% Calculate Dice Coefficient on group level
"""
DC = Dice coefficient:(2 * Voverlap) / (V1 + V2):
Voverlap is the number of overlapping voxels, V1 is the number of
voxels activated at time 1, and V2 is the number of voxels activated at
time 2.
"""
dc_001 = dice_coeff(data, 0.001)
print(dc_001)
dc_01 = dice_coeff(data, 0.01)
print(dc_01)
dc_05 = dice_coeff(data, 0.05)
print(dc_05)
dc_1 = dice_coeff(data, 0.1)
print(dc_1)

#%% Subject level overlap
data_dir = f'{project_dir}derivatives/results/CombinedRuns/reliability/'
data = pd.read_pickle(f'{data_dir}all_stats_CombinedRuns.pickle')
data = data[data["stat"]=='zstat1']
data_thresh = data[(data["val"] < -1.96 ) | (data["val"]> 1.96)]
#%%
dc_all = pd.DataFrame(columns=["sub", "dc"])
for sub in data_thresh["sub"].unique():
    subset = data_thresh[data_thresh["sub"]==sub]
    tmp = pd.DataFrame([dice_coeff(subset)], columns=["dc"])
    tmp["sub"] = sub
    dc_all = dc_all.append(tmp, ignore_index=True)

dc_all.describe()
test = dc_all[dc_all["dc"]!=0]
dc_all[dc_all["dc"]!=0].mean()
