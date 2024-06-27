#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
numpy version: 1.23.3
pingouin version: 0.5.3
"""

#%% Import Modules
import pandas as pd
import numpy as np
import pingouin as pg
from pathlib import Path

#%% Functions
def get_correlation(comparison, roi, measure_type, column1, column2, df):
    subset = df.groupby("sub").mean(numeric_only=True).reset_index()
    corr_value, p_value = pg.corr(subset[column1], subset[column2]).iloc[0]["r"], pg.corr(subset[column1], subset[column2]).iloc[0]["p-val"]
    p_value_pos = pg.corr(subset[column1], subset[column2], alternative="greater").iloc[0]["p-val"]
    p_value_neg = pg.corr(subset[column1], subset[column2], alternative="less").iloc[0]["p-val"]
    print(f'{comparison}, r = {corr_value}, p={p_value}')
    results.append({
        'Comparison': comparison,
        'session': "avg",
        'type': "averaged across sessions",
        'ROI': roi,
        'Measure Type': measure_type,
        'r': np.round(corr_value, 3),
        'p-value': np.round(p_value, 3),
        'p-value_pos' : np.round(p_value_pos,3),
        'p-value_neg' : np.round(p_value_neg,3)
        })
    for ses in ["ses-01", "ses-02"]:
        subset = df[df["ses"]==ses]
        corr_value, p_value = pg.corr(subset[column1], subset[column2]).iloc[0]["r"], pg.corr(subset[column1], subset[column2]).iloc[0]["p-val"]
        p_value_pos = pg.corr(subset[column1], subset[column2], alternative="greater").iloc[0]["p-val"]
        p_value_neg = pg.corr(subset[column1], subset[column2], alternative="less").iloc[0]["p-val"]
        print(f'{comparison}, {ses}, r = {corr_value}, p={p_value}')
        results.append({
            'Comparison': comparison,
            'session': ses,
            'type': "averaged across sessions",
            'ROI': roi,
            'Measure Type': measure_type,
            'r': np.round(corr_value, 3),
            'p-value': np.round(p_value, 3),
            'p-value_pos' : np.round(p_value_pos,3),
            'p-value_neg' : np.round(p_value_neg,3)
            })
        
def get_correlation_rating_diff(comparison, roi, measure_type, series1, series2):
    corr_value, p_value =  pg.corr(series1, series2).iloc[0]["r"], pg.corr(series1, series2).iloc[0]["p-val"]
    print(f'{comparison}, r = {corr_value}, p={p_value}')
    p_value_pos = pg.corr(series1, series2, alternative="greater").iloc[0]["p-val"]
    p_value_neg = pg.corr(series1, series2, alternative="less").iloc[0]["p-val"]
    results.append({
        'Comparison': comparison,
        'type': "difference between sessions",
        'ROI': roi,
        'Measure Type': measure_type,
        'r': np.round(corr_value, 3),
        'p-value': np.round(p_value, 3),
        'p-value_pos': np.round(p_value_pos, 3),
        'p-value_neg': np.round(p_value_neg, 3)
    })

def get_correlation_quality(comparison, roi, measure_type, series1, series2, extra=None):
    corr_value, p_value =  pg.corr(series1, series2).iloc[0]["r"], pg.corr(series1, series2).iloc[0]["p-val"]
    print(f'{comparison}, r = {corr_value}, p={p_value}')
    p_value_pos = pg.corr(series1, series2, alternative="greater").iloc[0]["p-val"]
    p_value_neg =  pg.corr(series1, series2, alternative="less").iloc[0]["p-val"]
    results_quality.append({
        'Comparison': comparison,
        'ROI': roi,
        'Measure Type': measure_type,
        'r': np.round(corr_value, 3),
        'p-value': np.round(p_value, 3),
        'p_value_pos': np.round(p_value_pos, 3),
        'p_value_neg': np.round(p_value_neg, 3)
    })

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord'
bold_dir = f'{project_dir}/derivatives/results/reliability/'
physio_dir = f'{project_dir}/derivatives/results/ReliabilityRun/physio/'
out_dir = f'{project_dir}/derivatives/results/Posthoc/Correlations/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Setting
#What BOLD measure do you want to calculate correlations for?
#cope1 or zstat1
stat = "cope1"

#%% Import data
#physio data
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
stats = pd.read_pickle(f'{bold_dir}cope_ReliabilityRun.pickle')
copes = stats[stats["stat"]==stat]
dhl = copes[copes["roi"]=="dh_left_c6"]
dl_dil = copes[copes["roi"]=="c6_dl_dil"]
vhr = copes[copes["roi"]=="vh_right_c6"]
vr_dil = copes[copes["roi"]=="c6_vr_dil"]

#import quality indicators
#1. Motion parameters (refrms)
refrms = pd.read_pickle(f'{out_dir}moco.pickle') 
#2. Dice coefficient between normalized EPI mask and PAM40
dc = pd.read_pickle(f'{out_dir}dc.pickle')
#3. curvature metrics
angle_to_b0 = pd.read_csv(f'{out_dir}dicom_zplane.csv')

#%% Correlations between physiological indicators of pain, ratings and BOLD results
results = []  
#1: beta and pain ratings
merged_df = pd.merge(dhl, ratings, on=['sub', 'ses'], how='inner')
get_correlation("DHL and Ratings", "DHL", stat, 'top10', 'Rating', merged_df)

#Rating differences
rating_wide = pd.pivot_table(merged_df, values="Rating", index="sub", columns="ses")
rating_diff = abs(rating_wide["ses-02"] - rating_wide["ses-01"])
dhl_wide = pd.pivot_table(merged_df, values="top10", index="sub", columns="ses")
dhl_diff = abs(dhl_wide["ses-02"] - dhl_wide["ses-01"])
get_correlation_rating_diff("Abs Difference DHL between sessions and abs difference rating", "DHL", stat, dhl_diff, rating_diff)

#2: beta and pupil
merged_df_pup = pd.merge(dhl, pdr, on=['sub', 'ses'], how='inner')
get_correlation("DHL and PDR", "DHL", stat, 'top10', 'maxval', merged_df_pup)

#3: beta and SCR
merged_df_scr = pd.merge(dhl, scr, on=['sub', 'ses'], how='inner')
get_correlation("DHL and SCR", "DHL", stat, 'top10', 'maxval', merged_df_scr)

#4: beta and HPR
merged_df_hpr = pd.merge(dhl, hpr, on=['sub', 'ses'], how='inner')
get_correlation("DHL and HPR", "DHL", stat, 'top10', 'maxval', merged_df_hpr)

results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv(f'{out_dir}correlation_results_physio_{stat}.csv', index=False)

#%% Correlations between quality indicators and BOLD results
results_quality = []

dhl_wide = pd.pivot_table(dhl, values="top10", index="sub", columns="ses")
dhl_diff = abs(dhl_wide["ses-02"] - dhl_wide["ses-01"])

#1. Motion parameters (refrms)
refrms_wide = pd.pivot_table(refrms, values="motionmean", index="sub", columns="ses")
refrms_diff = abs(refrms_wide["ses-02"] - refrms_wide["ses-01"])
get_correlation_quality("Abs DHL difference and abs refrms mean difference", "DHL", stat, dhl_diff, refrms_diff)

# 2. Dice coefficient between normalized EPI mask and PAM40
dc_wide = pd.pivot_table(dc, values="dc", index="sub", columns="ses")
dc_diff = abs(dc_wide["ses-02"] - dc_wide["ses-01"])
get_correlation_quality("Abs DHL difference and abs DC difference", "DHL", stat, dhl_diff, dc_diff)

angle_to_b0_wide = pd.pivot_table(angle_to_b0, values="angle", index="sub", columns="ses")
angle_to_b0_diff = abs(angle_to_b0_wide["ses-02"] - angle_to_b0_wide["ses-01"])
get_correlation_quality("Abs DHL beta difference and abs b0  difference", "DHL", stat, dhl_diff, angle_to_b0_diff)

results_quality_df = pd.DataFrame(results_quality)

# Save the results to a CSV file
results_quality_df.to_csv(f'{out_dir}correlation_results_quality.csv', index=False)


