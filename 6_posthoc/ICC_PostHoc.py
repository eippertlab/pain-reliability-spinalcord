#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandas version: 1.5.0
numpy version: 1.23.3
seaborn version: 0.11.0
matplotlib version: 3.6.3
pingouin version: 0.5.3
"""
#%% Import Modules
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import pingouin as pg
from matplotlib.patches import Rectangle
import matplotlib as mpl
from pathlib import Path

#%% Setting
#What do you want to calculate reliability for?
#cope or zstat
stat = "cope"

#%% Functions
def get_icc3_physio(df, modality):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings="maxval")
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    new_row = pd.DataFrame({"roi": [modality],
                    "ICC3": [value],
                    "ci_low": [ci_low],
                    "ci_high": [ci_high],
                    "group": ["Physiology"]})
    out = pd.concat([out, new_row], ignore_index=True)
    return out

def get_icc3_rating(df):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings="value")
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    new_row = pd.DataFrame({"roi": ["Ratings"],
                    "ICC3": [value],
                    "ci_low": [ci_low],
                    "ci_high": [ci_high],
                    "group": ["Physiology"]})
    out = pd.concat([out, new_row], ignore_index=True)
    return out

def get_icc3_cope(df, roi):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings="top10")
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    new_row = pd.DataFrame({"roi": [roi],
                    "ICC3": [value],
                    "ci_low": [ci_low],
                    "ci_high": [ci_high],
                    "group": ["BOLD"]})
    out = pd.concat([out, new_row], ignore_index=True)
    return out

def get_icc3_withinrun(df, modality):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df.copy()
    if modality in ["scr", "pdr", "hpr"]:
        meas = "val_scaled"
        rater = "subset_type"
        group = "phys"
    if modality in ["dhl"]:
        meas = "top10"
        rater = "subset_type"
        group = "BOLD"
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters=rater, ratings=meas)
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    new_row = pd.DataFrame({"roi": ["WithinRun"],
                    "ICC3": [value],
                    "ci_low": [ci_low],
                    "ci_high": [ci_high],
                    "group": [group]})
    out = pd.concat([out, new_row], ignore_index=True)
    return out

#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
cope_dir_combined = f'{project_dir}derivatives/results/CombinedRuns/reliability/'
cope_dir_dhr = f'{project_dir}derivatives/results/DHR/reliability/'
dir_withinrun = f'{project_dir}derivatives/results/WithinRun/reliability/'
physio_dir_combined = f'{project_dir}derivatives/results/CombinedRuns/physio/'
out_dir = f'{project_dir}derivatives/results/Posthoc/reliability/'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Load data
scr = pd.read_csv(f'{physio_dir_combined}peak_scr_CombinedRuns.csv')
scr = scr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)
pdr = pd.read_csv(f'{physio_dir_combined}peak_pupil_CombinedRuns.csv')
pdr = pdr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)
hpr = pd.read_csv(f'{physio_dir_combined}peak_hpr_CombinedRuns.csv')
hpr = hpr.rename(columns={"val_scaled":"maxval"}).drop("Unnamed: 0", axis=1)
pdr["modality"] = "pupil"
scr["modality"] = "scr"
hpr["modality"] = "hpr"

#import ratings CombinedRuns
ratings = pd.read_pickle(f'{physio_dir_combined}rating_CombinedRuns.pickle')

#import copes Combined Runs
stats = pd.read_pickle(f'{cope_dir_combined}cope_CombinedRuns.pickle')
copes = stats[stats["stat"]==stat]
dhl = copes[copes["roi"]=="dh_left_c6"]
dl_dil = copes[copes["roi"]=="c6_dl_dil"]
vhr = copes[copes["roi"]=="vh_right_c6"]
vr_dil = copes[copes["roi"]=="c6_vr_dil"]
dhl_CombinedRuns = dhl.copy()

#import copes with DHR regressor for spontaneous fluctuations
dhr = pd.read_pickle(f'{cope_dir_dhr}cope_DHR.pickle')

#import within run physio data
scr_WithinRun = pd.read_csv(f'{dir_withinrun}scr_WithinRun.csv')
pdr_WithinRun = pd.read_csv(f'{dir_withinrun}pdr_WithinRun.csv')
hpr_WithinRun = pd.read_csv(f'{dir_withinrun}hpr_WithinRun.csv')

#import copes within run
withinrun = pd.read_pickle(f'{dir_withinrun}cope_WithinRun.pickle')
odd_even = withinrun[withinrun["subset"].isin(["odd", "even"])]
early_late = withinrun[withinrun["subset"].isin(["early", "late"])]

#%% within run BOLD data
odd_even_ses1 = odd_even[odd_even["ses"]=="ses-01"]
icc_splithalf_evenodd_ses1 = get_icc3_withinrun(odd_even_ses1, "dhl")
icc_splithalf_evenodd_ses1["errsize"] = icc_splithalf_evenodd_ses1["ci_high"] - icc_splithalf_evenodd_ses1["ci_low"]

evenodd_ses2 = odd_even[odd_even["ses"]=="ses-02"]
icc_evenodd_ses2 = get_icc3_withinrun(evenodd_ses2, "dhl")
icc_evenodd_ses2["errsize"] = icc_evenodd_ses2["ci_high"] - icc_evenodd_ses2["ci_low"]

icc_evenodd = pd.concat([icc_splithalf_evenodd_ses1, icc_evenodd_ses2])
icc_evenodd = icc_evenodd.groupby(["roi", "group"], as_index=False).mean(numeric_only=True)
icc_evenodd["roi"] = "odd-even"
icc_evenodd["group"] = "BOLD"

#within run early late
early_late_ses1 = early_late[early_late["ses"]=="ses-01"]
icc_early_late_ses1 = get_icc3_withinrun(early_late_ses1, "dhl")
icc_early_late_ses1["errsize"] = icc_early_late_ses1["ci_high"] - icc_early_late_ses1["ci_low"]

early_late_ses2 = early_late[early_late["ses"]=="ses-02"]
icc_early_late_ses2 = get_icc3_withinrun(early_late_ses2, "dhl")
icc_early_late_ses2["errsize"] = icc_early_late_ses2["ci_high"] - icc_early_late_ses2["ci_low"]

icc_early_late = pd.concat([icc_early_late_ses1, icc_early_late_ses2])
icc_early_late = icc_early_late.groupby(["roi", "group"], as_index=False).mean(numeric_only=True)
icc_early_late["roi"] = "early-late"
icc_early_late["group"] = "BOLD"

#%% SCR WithinRun
scr_evenodd = scr_WithinRun[scr_WithinRun["subset"].isin(["odd", "even"])]
scr_evenodd_ses1 = scr_evenodd[scr_evenodd["ses"]=="ses-01"]
icc_scr_evenodd_ses1 = get_icc3_withinrun(scr_evenodd_ses1, "scr")
icc_scr_evenodd_ses1["errsize"] = icc_scr_evenodd_ses1["ci_high"] - icc_scr_evenodd_ses1["ci_low"]

scr_evenodd_ses2 = scr_evenodd[scr_evenodd["ses"]=="ses-02"]
icc_scr_evenodd_ses2 = get_icc3_withinrun(scr_evenodd_ses2, "scr")
icc_scr_evenodd_ses2["errsize"] = icc_scr_evenodd_ses2["ci_high"] - icc_scr_evenodd_ses2["ci_low"]

icc_scr_evenodd = pd.concat([icc_scr_evenodd_ses1, icc_scr_evenodd_ses2])
icc_scr_evenodd = icc_scr_evenodd.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_scr_evenodd["roi"][0] = "odd-even"
icc_scr_evenodd["group"] = "Phys"

scr_earlylate = scr_WithinRun[scr_WithinRun["subset"].isin(["early", "late"])]
scr_earlylate_ses1 = scr_earlylate[scr_earlylate["ses"]=="ses-01"]
icc_scr_earlylate_ses1 = get_icc3_withinrun(scr_earlylate_ses1, "scr")
icc_scr_earlylate_ses1["errsize"] = icc_scr_earlylate_ses1["ci_high"] - icc_scr_earlylate_ses1["ci_low"]

scr_earlylate_ses2 = scr_earlylate[scr_earlylate["ses"]=="ses-02"]
icc_scr_earlylate_ses2 = get_icc3_withinrun(scr_earlylate_ses2, "scr")
icc_scr_earlylate_ses2["errsize"] = icc_scr_earlylate_ses2["ci_high"] - icc_scr_earlylate_ses2["ci_low"]

icc_scr_earlylate = pd.concat([icc_scr_earlylate_ses1, icc_scr_earlylate_ses2])
icc_scr_earlylate = icc_scr_earlylate.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_scr_earlylate["roi"][0] = "early-late"
icc_scr_earlylate["group"] = "Phys"

#%% PDR WithinRun
pdr_evenodd = pdr_WithinRun[pdr_WithinRun["subset"].isin(["odd", "even"])]
pdr_evenodd_ses1 = pdr_evenodd[pdr_evenodd["ses"]=="ses-01"]
icc_pdr_evenodd_ses1 = get_icc3_withinrun(pdr_evenodd_ses1, "pdr")
icc_pdr_evenodd_ses1["errsize"] = icc_pdr_evenodd_ses1["ci_high"] - icc_pdr_evenodd_ses1["ci_low"]

pdr_evenodd_ses2 = pdr_evenodd[pdr_evenodd["ses"]=="ses-02"]
icc_pdr_evenodd_ses2 = get_icc3_withinrun(pdr_evenodd_ses2, "pdr")
icc_pdr_evenodd_ses2["errsize"] = icc_pdr_evenodd_ses2["ci_high"] - icc_pdr_evenodd_ses2["ci_low"]

icc_pdr_evenodd = pd.concat([icc_pdr_evenodd_ses1, icc_pdr_evenodd_ses2])
icc_pdr_evenodd = icc_pdr_evenodd.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_pdr_evenodd["roi"][0] = "odd-even"
icc_pdr_evenodd["group"] = "Phys"

pdr_earlylate = pdr_WithinRun[pdr_WithinRun["subset"].isin(["early", "late"])]
pdr_earlylate_ses1 = pdr_earlylate[pdr_earlylate["ses"]=="ses-01"]
icc_pdr_earlylate_ses1 = get_icc3_withinrun(pdr_earlylate_ses1, "pdr")
icc_pdr_earlylate_ses1["errsize"] = icc_pdr_earlylate_ses1["ci_high"] - icc_scr_earlylate_ses1["ci_low"]

pdr_earlylate_ses2 = pdr_earlylate[pdr_earlylate["ses"]=="ses-02"]
icc_pdr_earlylate_ses2 = get_icc3_withinrun(pdr_earlylate_ses2, "pdr")
icc_pdr_earlylate_ses2["errsize"] = icc_pdr_earlylate_ses2["ci_high"] - icc_pdr_earlylate_ses2["ci_low"]

icc_pdr_earlylate = pd.concat([icc_pdr_earlylate_ses1, icc_pdr_earlylate_ses2])
icc_pdr_earlylate = icc_pdr_earlylate.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_pdr_earlylate["roi"][0] = "early-late"
icc_pdr_earlylate["group"] = "Phys"

#%% HPR WithinRun
hpr_evenodd = hpr_WithinRun[hpr_WithinRun["subset"].isin(["odd", "even"])]
hpr_evenodd_ses1 = hpr_evenodd[hpr_evenodd["ses"]=="ses-01"]
icc_hpr_evenodd_ses1 = get_icc3_withinrun(hpr_evenodd_ses1, "hpr")
icc_hpr_evenodd_ses1["errsize"] = icc_hpr_evenodd_ses1["ci_high"] - icc_hpr_evenodd_ses1["ci_low"]

hpr_evenodd_ses2 = hpr_evenodd[hpr_evenodd["ses"]=="ses-02"]
icc_hpr_evenodd_ses2 = get_icc3_withinrun(hpr_evenodd_ses2, "hpr")
icc_hpr_evenodd_ses2["errsize"] = icc_hpr_evenodd_ses2["ci_high"] - icc_hpr_evenodd_ses2["ci_low"]

icc_hpr_evenodd = pd.concat([icc_hpr_evenodd_ses1, icc_hpr_evenodd_ses2])
icc_hpr_evenodd = icc_hpr_evenodd.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_hpr_evenodd["roi"][0] = "odd-even"
icc_hpr_evenodd["group"] = "Phys"

hpr_earlylate = hpr_WithinRun[hpr_WithinRun["subset"].isin(["early", "late"])]
hpr_earlylate_ses1 = hpr_earlylate[hpr_earlylate["ses"]=="ses-01"]
icc_hpr_earlylate_ses1 = get_icc3_withinrun(hpr_earlylate_ses1, "hpr")
icc_hpr_earlylate_ses1["errsize"] = icc_hpr_earlylate_ses1["ci_high"] - icc_hpr_earlylate_ses1["ci_low"]

hpr_earlylate_ses2 = hpr_earlylate[hpr_earlylate["ses"]=="ses-02"]
icc_hpr_earlylate_ses2 = get_icc3_withinrun(hpr_earlylate_ses2, "hpr")
icc_hpr_earlylate_ses2["errsize"] = icc_hpr_earlylate_ses2["ci_high"] - icc_hpr_earlylate_ses2["ci_low"]

icc_hpr_earlylate = pd.concat([icc_hpr_earlylate_ses1, icc_hpr_earlylate_ses2])
icc_hpr_earlylate = icc_hpr_earlylate.groupby(["roi"], as_index=False).mean(numeric_only=True)
icc_hpr_earlylate["roi"][0] = "early-late"
icc_hpr_earlylate["group"] = "Phys"

#%% ICC tables
icc_table_ratings = get_icc3_rating(ratings)
icc_table_ratings["errsize"] = (icc_table_ratings["ci_high"] - icc_table_ratings["ci_low"])/2

icc_table_scr = get_icc3_physio(scr, "scr")
icc_table_scr["errsize"] = (icc_table_scr["ci_high"] - icc_table_scr["ci_low"])/2

icc_table_pupil = get_icc3_physio(pdr, "pupil")
icc_table_pupil["errsize"] = (icc_table_pupil["ci_high"] - icc_table_pupil["ci_low"])/2

icc_table_hpr = get_icc3_physio(hpr, "hpr")
icc_table_hpr["errsize"] = (icc_table_hpr["ci_high"] - icc_table_hpr["ci_low"])/2

icc_table_dhr = get_icc3_cope(dhr, "dhr")
icc_table_dhr["errsize"] = (icc_table_dhr["ci_high"] - icc_table_dhr["ci_low"])/2

icc_table_dhl_CombinedRuns = get_icc3_cope(dhl_CombinedRuns, "CombinedRuns")
icc_table_dhl_CombinedRuns["errsize"] = (icc_table_dhl_CombinedRuns["ci_high"] - icc_table_dhl_CombinedRuns["ci_low"])/2

icc_table = pd.concat([icc_table_ratings, icc_table_scr, icc_table_pupil, icc_table_hpr, icc_evenodd, icc_early_late, icc_table_dhl_CombinedRuns, icc_table_dhr], ignore_index=True)
#icc_table = icc_table.append({'roi': " ", "ICC3": None, "ci_low": None, "ci_high": None, "group": " ", "errsize": None }, ignore_index=True)
icc_table["order"] = [0, 1, 2, 3, 6, 7, 4, 5]

#%% updated Reliability Figure for posthoc analysis:
#Supplementary Figure 3. Test-retest reliability across both days for subjective ratings, peripheral physiological data and BOLD response amplitudes
badcolor="#cc4c02"
faircolor="#fe9929"
goodcolor="#fed98e"
bestcolor="#ffffd4"
al=0.5
#plot
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white")
with sns.plotting_context('paper', font_scale = 1.5):
    g = sns.catplot(x="roi", y="ICC3", data=icc_table, kind="point",
                join=False, sharex=False, sharey=True, height=2.5, aspect=3,
                color="black", scale=0.5, order=["Ratings", "scr", "pupil", "hpr",
                                                 "mocoall", "dhr", "odd-even",  "early-late", ], zorder=20, alpha=1)
    axes=g.axes.flatten()

    axes[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
    axes[0].set_yticklabels(["0", "0.25", "0.5", "0.75", "1"])
    axes[0].set_ylim(0, 1)
    axes[0].set_xlim(-0.5,7.75)
    axes[0].errorbar(icc_table['order'], icc_table['ICC3'],
                     yerr=icc_table['errsize'],
                     ls='none', capsize=None, color="black",
                elinewidth=0.8, zorder=15)
    axes[0].set_xlabel(None)
    axes[0].set_title(None)
    axes[0].add_patch(Rectangle((-0.5, 0.75),8.25,0.25, fill = True ,linewidth = 2, alpha=al, facecolor=bestcolor, edgecolor=None, label="excellent", zorder=10))
    axes[0].add_patch(Rectangle((-0.5, 0.60),8.25,0.15, fill = True,linewidth = 2, alpha=al, facecolor=goodcolor, edgecolor = None, label="good", zorder=10))
    axes[0].add_patch(Rectangle((-0.5, 0.4),8.25,0.2, fill = True,linewidth = 2, alpha=al, facecolor=faircolor, edgecolor=None, label="fair", zorder=10))
    axes[0].add_patch(Rectangle((-0.5, 0),8.25,0.4, fill = True,linewidth = 2, alpha=al, facecolor=badcolor, edgecolor = None, label="poor", zorder=10))
    axes[0].set_xticklabels(["Ratings\nCombined", "SCR\nCombined", "Pupil\nCombined", "HPR\nCombined",
                            "ROI\nCombined", "ROI\nDHR",
                            "ROI\nOdd-even", "ROI\nEarly-late"], size=10)
    axes[0].set_ylabel(' ', labelpad=10, size=30)
    axes[0].vlines(x=3.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)
    axes[0].vlines(x=5.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)

    for axis in ['top', 'bottom', 'left', 'right']:
        axes[0].spines[axis].set_linewidth(0.5)
    lines_labels = [axes[0].get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    plt.title("Post-hoc reliability", y=1.05)
    leg = plt.legend(lines, labels, bbox_to_anchor=(1.4, 1.01),loc = 'upper right', title="Interpretation ICC")
    for line in leg.get_lines():
        line.set_linewidth(4.0)
plt.savefig(f'{out_dir}reliability_posthhoc_top10.png', bbox_inches='tight', format="png", dpi=300)
plt.show()
