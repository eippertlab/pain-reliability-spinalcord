#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 11 18:05:03 2022

@author: dabbagh
"""
# =============================================================================
# Modules
# =============================================================================
#%%
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import pingouin as pg
from matplotlib.patches import Rectangle
import matplotlib as mpl
#%%
# =============================================================================
# Functions
# =============================================================================
def get_icc3(df):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    for modality in ["scr", "pupil", "hpr"]:
        tmp = df
        output_tmp = pg.intraclass_corr(data=tmp[tmp["modality"]==modality], targets="ID", raters="ses", ratings="maxval")
        value = output_tmp['ICC'][2]
        ci_low = output_tmp['CI95%'][2][0]
        ci_high = output_tmp['CI95%'][2][1]
        out = out.append({"roi":modality, "ICC3": value, "ci_low": ci_low,
                          "ci_high": ci_high, "group":"physiology"}, ignore_index=True)
    return out

def get_icc3_rating(df):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    tmp = df
    output_tmp = pg.intraclass_corr(data=tmp, targets="ID", raters="Session", ratings="Rating")
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

def get_icc3_evenodd(df, grouping):
    out = pd.DataFrame(columns=["roi", "ICC3", "ci_low", "ci_high", "group"])
    for measure in ["max"]:
        tmp = df
        output_tmp = pg.intraclass_corr(data=tmp, targets="ID", raters=grouping, ratings=measure)
        value = output_tmp['ICC'][2]
        ci_low = output_tmp['CI95%'][2][0]
        ci_high = output_tmp['CI95%'][2][1]
        out = out.append({"roi":"splithalf", "ICC3": value, "ci_low": ci_low, "ci_high": ci_high, "group":"BOLD"}, ignore_index=True)
    return out
#%%
# =============================================================================
# Directories
# =============================================================================
#import scr
phys_dir = '/data/pt_02306/main/data/derivatives/phys/results/'
epochmeans_40_scr = pd.read_csv(phys_dir + 'avg_peak_scr_te40.csv')
epochmeans_40_pup = pd.read_csv(phys_dir + 'avg_peak_pup_te40.csv')
epochmeans_40_hpr = pd.read_csv(phys_dir + 'avg_peak_hpr_te40.csv')
epochmeans_40_hpr = epochmeans_40_hpr.loc[:,"sub":"hep"]
epochmeans_40_hpr = epochmeans_40_hpr.rename(columns={"sub":"ID"})
epochmeans_40_hpr = epochmeans_40_hpr.rename(columns={"hep":"maxval"})
epochmeans_40_pup = epochmeans_40_pup.loc[:,"ID":"value"]
epochmeans_40_pup = epochmeans_40_pup.rename(columns={"value":"maxval"})
epochmeans_40_scr = epochmeans_40_scr.loc[:,"ID":"value"]
epochmeans_40_scr = epochmeans_40_scr.rename(columns={"value":"maxval"})
epochmeans_40_pup["modality"] = "pupil"
epochmeans_40_scr["modality"] = "scr"
epochmeans_40_hpr["modality"] = "hpr"
epochmeans = epochmeans_40_pup.append([epochmeans_40_scr, epochmeans_40_hpr]).loc[:,"ID":"modality"]

#import ratings
rate_dir = "/data/pt_02306/main/data/derivatives/phys/"
ratings = pd.read_csv(rate_dir + "Ratings.CSV", sep=";")
ratings_40 = ratings[(ratings["TE"]=="40")&(ratings["ID"]!=31)]
ratings_40 = ratings_40.groupby(["ID","Session"], as_index=False).mean().drop(["Run", "Patch"], axis=1)

#import copes
cope_dir = '/data/pt_02306/main/data/derivatives/reliability/func/'
dhl = pd.read_csv(cope_dir + "dhl_top10.csv")
dl_dil = pd.read_csv(cope_dir + "dil_dl_top10.csv")

cope_dilc6_rv = pd.read_csv(cope_dir + "vr_dil_top10.csv")
cope_vhrc6 = pd.read_csv(cope_dir + "vh_top10.csv")
#%%
#Ttests

#Ratings
test_ratings = pg.pairwise_tests(data=ratings_40, dv="Rating", subject="ID", within="Session",
                 alpha=0.05, parametric=True)
print(test_ratings["p-unc"].values[0])

#SCR
test_scr = pg.pairwise_tests(data=epochmeans_40_scr, dv="maxval", subject="ID", within="ses",
                 alpha=0.05, parametric=True)
print(test_scr["p-unc"].values[0])

#test PDR
test_pdr = pg.pairwise_tests(data=epochmeans_40_pup, dv="maxval", subject="ID", within="ses",
                 alpha=0.05)
print(test_pdr["p-unc"].values[0])
#test HPR
test_hpr = pg.pairwise_tests(data=epochmeans_40_hpr, dv="maxval", subject="ID", within="ses",
                 alpha=0.05)
print(test_hpr["p-unc"].values[0])



#%%
icc_table_ratings = get_icc3_rating(ratings_40)
icc_table_ratings["errsize"] = (icc_table_ratings["ci_high"] - icc_table_ratings["ci_low"])/2

icc_table = get_icc3(epochmeans)
icc_table["errsize"] = (icc_table["ci_high"] - icc_table["ci_low"])/2
#icc_table = icc_table.sort_values("modality", ascending=False)

icc_table_cope = get_icc3_cope(dhl, "dh_l_c6")
icc_table_cope["errsize"] = (icc_table_cope["ci_high"] - icc_table_cope["ci_low"])/2

icc_table_dl_dil = get_icc3_cope(dl_dil, "dl_dil")
icc_table_dl_dil["errsize"] = (icc_table_dl_dil["ci_high"] - icc_table_dl_dil["ci_low"])/2

icc_table_vhrc6 = get_icc3_cope(cope_vhrc6, "vhr")
icc_table_vhrc6["errsize"] = (icc_table_vhrc6["ci_high"] - icc_table_vhrc6["ci_low"])/2

icc_table_vr_dil = get_icc3_cope(cope_dilc6_rv, "vr_dil")
icc_table_vr_dil["errsize"] = (icc_table_vr_dil["ci_high"] - icc_table_vr_dil["ci_low"])/2

icc_table = icc_table.append([icc_table_ratings, icc_table_cope, icc_table_dl_dil,
                              icc_table_vhrc6, icc_table_vr_dil], ignore_index=True)

#%%#icc_table = icc_table.append({'roi': " ", "ICC3": None, "ci_low": None, "ci_high": None, "group": " ", "errsize": None }, ignore_index=True)
icc_table["order"] = [1, 2, 3, 0, 4, 5, 6, 7]
out_dir_manu='/data/pt_02306/main/data/derivatives/manuscript/figures/reliab/'

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
    #axes[0].vlines(x=1.5, ymin=0, ymax=1, color="darkgray")
    #axes[0].vlines(x=2.5, ymin=0, ymax=1, color="darkgray")
    axes[0].vlines(x=3.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)
    axes[0].vlines(x=5.5, ymin=0, ymax=1.2, color="darkgray", zorder=25)
    #axes[0].vlines(x=7.5, ymin=0, ymax=1, color="darkgray")

    for axis in ['top', 'bottom', 'left', 'right']:
        axes[0].spines[axis].set_linewidth(0.5)
    lines_labels = [axes[0].get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    #leg = plt.legend(lines, labels, bbox_to_anchor=(1.4, 1.01),loc = 'upper right', title="Interpretation ICC")
    #for line in leg.get_lines():
     #   line.set_linewidth(4.0)
plt.savefig(out_dir_manu+'reliability_te40_measures_top10_updated.pdf', bbox_inches='tight', format="pdf")
plt.savefig(out_dir_manu+'reliability_te40_measures_top10_updated.png', bbox_inches='tight', format="png", dpi=300)
plt.savefig(out_dir_manu+'reliability_te40_measures_top10_updated.svg', bbox_inches='tight', format="svg")
plt.show()
