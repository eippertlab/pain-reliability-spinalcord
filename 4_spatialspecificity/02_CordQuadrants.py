#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
matplotlib version: 3.6.3
numpy version: 1.23.3
"""
#%% Import modules
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/ReliabilityRun/spatial_specificity/'
out_dir = data_dir
mask_dir = f'{project_dir}derivatives/masks/'

#%% Import and prepare data
data = pd.read_pickle(f'{data_dir}cord_p_uncorr.pickle')
rois_quadrants = ['dr', 'vr', 'dl', 'vl']
levels = ['c5', 'c6', 'c7', 'c8']
data = data[data["roi"].isin(rois_quadrants)]
data["pval"] = 1 - data["val"]
data_thresh = data[data["pval"]<0.001]
data_thresh = data[data["pval"]<0.1]

#%%
percentages_quarterly = []
for level in levels:
    subset = data_thresh[data_thresh["level"] == level]
    n_all = len(subset)
    # Calculate counts
    counts = {roi: len(subset[subset['roi'].str.contains(roi)]) for roi in rois_quadrants}
    # Calculate percentages
    percentages = {roi: (count / n_all) * 100 if n_all else None for roi, count in counts.items()}
    # Add to the final list
    percentages_quarterly.extend(
        {'level': str(level), 
         'index': roi.upper(), 
         'perceptage': percentages[roi], 
         'nside': counts[roi], 
         'nall': n_all} 
        for roi in counts
    )

# Convert to DataFrame at the end
percentages_df = pd.DataFrame(percentages_quarterly)
