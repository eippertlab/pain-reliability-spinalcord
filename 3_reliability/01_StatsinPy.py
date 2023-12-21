#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 13:08:47 2022

@author: dabbagh
"""
# =============================================================================
# Modules
# =============================================================================
import pandas as pd
import glob
import pingouin as pg
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib.axes as axt
import warnings
import numpy as np
import warnings
warnings.filterwarnings("ignore")
#%%
# =============================================================================
# =============================================================================
# Functions
# =============================================================================
def get_icc3(df):
    out = pd.DataFrame(columns=["measure", "ICC3", "ci_low", "ci_high"])
    for measure in ["avg", "max", "top10"]:
        tmp = df
        output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings=measure)
        value = output_tmp['ICC'][2]
        ci_low = output_tmp['CI95%'][2][0]
        ci_high = output_tmp['CI95%'][2][1]
        out = out.append({"measure":measure, "ICC3": value, "ci_low": ci_low, "ci_high": ci_high}, ignore_index=True)
    return out

def retain_quantile(data, percentile=0.9):
    percentile_val = data[3].quantile(percentile)
    return data[data[3] >= percentile_val]
#%%
############ DH left, c6 ######################################################
out_dir = '/data/pt_02306/main/data/derivatives/reliability/func/'
models=["denoised_single_2step_v2"]
rois=["dhlc6_00", "dhlc5_00"]
data= pd.DataFrame(columns=['sub', 'ses', 'max', 'avg', 'top10'], dtype='float')
for subject in range(1, 41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    #Loop over sessions
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        for model in models:
            #print('session: ',ses)
            #Define directory and ROIs
            base_dir = '/data/pt_02306/main/data'
            data_dir = base_dir + '/derivatives/glm/' + sub + '/' + ses + '/' + model + '/'
            runs = glob.glob(data_dir + "*te-40_*refined.feat")
            for run in runs:
                file_dir = run + '/stats/normalization/extracts/'
                for roi in rois:
                    tmp=pd.read_csv(file_dir + roi + '_m.txt' , header=None, names=["avg"], delim_whitespace=True)
                    tmp1=pd.read_csv(file_dir + roi + '_min_max.txt' , header=None, delim_whitespace=True)
                    tmp["max"] = tmp1.iloc[0,1]
                    tmp2 = pd.read_csv(file_dir + roi + '_all.txt' , header=None, delim_whitespace=True).transpose()
                    tmp2 = retain_quantile(tmp2).reset_index(drop=True)
                    tmp["top10"] = tmp2[3].mean()
                    tmp['sub'] = sub
                    tmp['ses'] = ses
                    tmp["roi"] = roi
                    data = data.append(tmp, ignore_index=True)
#%%
data6=data.groupby(["sub", "ses"], as_index=False).mean()
#%%
icc_table_dhl = get_icc3(data6)
icc_table_dhl["errsize"] = icc_table_dhl["ci_high"] - icc_table_dhl["ci_low"]
#%%
