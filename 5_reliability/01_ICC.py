#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandas version: 1.5.0
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

#%% Functions
def get_icc3_phys(df):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    for modality in ["scr", "pupil", "hpr"]:
        tmp = df
        output_tmp = pg.intraclass_corr(data=tmp[tmp["modality"]==modality], targets="sub", raters="ses", ratings="maxval")
        value = output_tmp['ICC'][2]
        ci_low = output_tmp['CI95%'][2][0]
        ci_high = output_tmp['CI95%'][2][1]
        out = out.append({"roi":modality, "ICC3": value, "ci_low": ci_low,
                          "ci_high": ci_high, "group":"physiology"}, ignore_index=True)
    return out

def get_icc3_rating(df):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings="value")
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    out = out.append({"roi":"Ratings", "ICC3": value, "ci_low": ci_low,
                      "ci_high": ci_high, "group":"physiology"}, ignore_index=True)
    return out

def get_icc3_cope(df, roi):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="sub", raters="ses", ratings="top10")
    value = output_tmp['ICC'][2]
    ci_low = output_tmp['CI95%'][2][0]
    ci_high = output_tmp['CI95%'][2][1]
    out = out.append({"roi":roi, "ICC3": value, "ci_low": ci_low,
                      "ci_high": ci_high, "group":"BOLD"}, ignore_index=True)
    return out
    
#%% Directories
project_dir = "/data/pt_02306/main/data/pain-reliability-spinalcord/"
out_dir = f'{project_dir}derivatives/results/ReliabilityRun/reliability/'
physio_dir = f'{project_dir}derivatives/results/ReliabilityRun/physio/'
#%% Setting
#What do you want to calculate reliability for?
#cope1 or zstat1
stat = "cope1"

#%% Import data
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
stats = pd.read_pickle(f'{out_dir}cope_ReliabilityRun.pickle')
copes = stats[stats["stat"]==stat]
dhl = copes[copes["roi"]=="dh_left_c6"]
dl_dil = copes[copes["roi"]=="c6_dl_dil"]
vhr = copes[copes["roi"]=="vh_right_c6"]
vr_dil = copes[copes["roi"]=="c6_vr_dil"]
#%%
#Ttests
#Ratings
test_ratings = pg.pairwise_tests(data=ratings, dv="value", subject="sub", within="ses",
                 alpha=0.05, parametric=True)
print(f'p-value ttest rating across days: {test_ratings["p-unc"].values[0]}')

#SCR
test_scr = pg.pairwise_tests(data=scr, dv="maxval", subject="sub", within="ses", alpha=0.05, parametric=True)
print(f'p-value ttest scr peaks across days: {test_scr["p-unc"].values[0]}')

#test PDR
test_pdr = pg.pairwise_tests(data=pdr, dv="maxval", subject="sub", within="ses",alpha=0.05, parametric=True)
print(f'p-value ttest pdr across days: {test_pdr["p-unc"].values[0]}')
#test HPR
test_hpr = pg.pairwise_tests(data=hpr, dv="maxval", subject="sub", within="ses",alpha=0.05, parametric=True)
print(f'p-value ttest hpr across days: {test_hpr["p-unc"].values[0]}')

#%%
icc_table_ratings = get_icc3_rating(ratings)
icc_table_ratings["errsize"] = (icc_table_ratings["ci_high"] - icc_table_ratings["ci_low"])/2

icc_table = get_icc3_phys(physio)
icc_table["errsize"] = (icc_table["ci_high"] - icc_table["ci_low"])/2
#icc_table = icc_table.sort_values("modality", ascending=False)

icc_table_cope = get_icc3_cope(dhl, "dh_l_c6")
icc_table_cope["errsize"] = (icc_table_cope["ci_high"] - icc_table_cope["ci_low"])/2

icc_table_dl_dil = get_icc3_cope(dl_dil, "dl_dil")
icc_table_dl_dil["errsize"] = (icc_table_dl_dil["ci_high"] - icc_table_dl_dil["ci_low"])/2

icc_table_vhrc6 = get_icc3_cope(vhr, "vhr")
icc_table_vhrc6["errsize"] = (icc_table_vhrc6["ci_high"] - icc_table_vhrc6["ci_low"])/2

icc_table_vr_dil = get_icc3_cope(vr_dil, "vr_dil")
icc_table_vr_dil["errsize"] = (icc_table_vr_dil["ci_high"] - icc_table_vr_dil["ci_low"])/2

icc_table = icc_table.append([icc_table_ratings, icc_table_cope, icc_table_dl_dil,
                              icc_table_vhrc6, icc_table_vr_dil], ignore_index=True)

#%%# Fig. 6: Test-retest reliability across both days for subjective ratings, peripheral physiological data and BOLD response amplitudes.
icc_table["order"] = [1, 2, 3, 0, 4, 5, 6, 7]
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
                join=False, sharex=False, sharey=True, height=2.5, aspect=3.5,
                color="black", scale=0.5, order=["Ratings", "scr", "pupil", "hpr",
                                                 "dh_l_c6",  "dl_dil", "vhr", "vr_dil"], zorder=20, alpha=1)
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
    axes[0].set_xticklabels(["Ratings", "SCR", "Pupil", "HPR",
                             "ROI", "Dilated ROI", "Control",
                             "Dilated control"], size=12)
    axes[0].set_ylabel(' ', labelpad=10, size=30)
    axes[0].vlines(x=3.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)
    axes[0].vlines(x=5.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)
    plt.title(f'ICC(3,1) for physio & {stat}', y=1.1)
    for axis in ['top', 'bottom', 'left', 'right']:
        axes[0].spines[axis].set_linewidth(0.5)
    lines_labels = [axes[0].get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    plt.savefig(out_dir+'icc_ReliabilityRun.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
