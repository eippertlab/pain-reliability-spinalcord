#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
matplotlib version: 3.6.3
numpy version: 1.23.3
nibabel version: 4.0.2
"""
#%% Modules
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib as mpl
import nibabel as nib
import glob

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/CombinedRuns/spatial_specificity/'
out_dir = data_dir
mask_dir = f'{project_dir}derivatives/masks/'

#%% Import and prepare data
data = pd.read_pickle(f'{data_dir}cord_p_uncorr.pickle')
rois_horns = ['dh_left', 'dh_right', 'vh_left', 'vh_right']
data = data[data["roi"].isin(rois_horns)]
data['pval'] = 1-data["val"]
data_thresh = data[data['pval']<0.001]
data_thresh = data_thresh.drop(["z"], axis=1)
statcount = data_thresh[data_thresh['pval']<0.001].groupby(["roi", "level"], as_index=False).count()
x = data_thresh["x"]
y = data_thresh["y"]

#%% get cord mask
cord = glob.glob(f'{mask_dir}cord_c6.nii.gz')[0]
imgcord = nib.load(cord)
header = imgcord.header
print(header.get_data_shape())
print(header)
cord_data = imgcord.get_fdata()

slice_cord = cord_data[:, :, 837]
slice_cord_array = pd.DataFrame(columns=["x", "y"])
slice_cord_t = np.transpose(slice_cord)
for x in range(slice_cord.shape[0]):
    for y in range(slice_cord.shape[1]):
        if slice_cord[x, y]==1:
            slice_cord_array = slice_cord_array.append({"x": float(x), "y": float(y)}, ignore_index=True)
slice_cord_array["x"] = pd.to_numeric(slice_cord_array['x'], downcast='float')
slice_cord_array["y"] = pd.to_numeric(slice_cord_array['y'], downcast='float')

#%% get horn masks
#dhl
dhl_file = glob.glob(f'{mask_dir}dh_left_c6.nii.gz')[0]
imgdhl = nib.load(dhl_file)
header = imgdhl.header
print(header.get_data_shape())
print(header)
dhl_data = imgdhl.get_fdata()

dhl = dhl_data[:, :, 837]
dhl_df = pd.DataFrame(columns=["x", "y"])
#slice_cord_t = np.transpose(slice_cord)
for x in range(dhl.shape[0]):
    for y in range(dhl.shape[1]):
        if dhl[x, y]==1:
            dhl_df = dhl_df.append({"x": float(x), "y": float(y)}, ignore_index=True)
dhl_df["x"] = pd.to_numeric(dhl_df['x'], downcast='float')
dhl_df["y"] = pd.to_numeric(dhl_df['y'], downcast='float')

#dhr
dhr_file = glob.glob(f'{mask_dir}dh_right_c6.nii.gz')[0]
imgdhr = nib.load(dhr_file)
header = imgdhr.header
print(header.get_data_shape())
print(header)
dhr_data = imgdhr.get_fdata()

dhr = dhr_data[:, :, 837]
dhr_df = pd.DataFrame(columns=["x", "y"])
#slice_cord_t = np.transpose(slice_cord)
for x in range(dhr.shape[0]):
    for y in range(dhr.shape[1]):
        if dhr[x, y]==1:
            dhr_df = dhr_df.append({"x": float(x), "y": float(y)}, ignore_index=True)
dhr_df["x"] = pd.to_numeric(dhr_df['x'], downcast='float')
dhr_df["y"] = pd.to_numeric(dhr_df['y'], downcast='float')

#dhr
vhr_file = glob.glob(f'{mask_dir}vh_right_c6.nii.gz')[0]
imgvhr = nib.load(vhr_file)
vhr_data = imgvhr.get_fdata()

vhr = vhr_data[:, :, 837]
vhr_df = pd.DataFrame(columns=["x", "y"])
#slice_cord_t = np.transpose(slice_cord)
for x in range(vhr.shape[0]):
    for y in range(vhr.shape[1]):
        if vhr[x, y]==1:
            vhr_df = vhr_df.append({"x": float(x), "y": float(y)}, ignore_index=True)
vhr_df["x"] = pd.to_numeric(vhr_df['x'], downcast='float')
vhr_df["y"] = pd.to_numeric(vhr_df['y'], downcast='float')

#vhl
vhl_file = glob.glob(f'{mask_dir}vh_left_c6.nii.gz')[0]
imgvhl = nib.load(vhl_file)
vhl_data = imgvhl.get_fdata()

vhl = vhl_data[:, :, 837]
vhl_df = pd.DataFrame(columns=["x", "y"])
#slice_cord_t = np.transpose(slice_cord)
for x in range(vhl.shape[0]):
    for y in range(vhl.shape[1]):
        if vhl[x, y]==1:
            vhl_df = vhl_df.append({"x": float(x), "y": float(y)}, ignore_index=True)
vhl_df["x"] = pd.to_numeric(vhl_df['x'], downcast='float')
vhl_df["y"] = pd.to_numeric(vhl_df['y'], downcast='float')

#%%  prep axes
whole = data_thresh
c6 = data_thresh[data_thresh["level"]=="c6"]

x1 = c6["x"].values
x2 = whole["x"].values

y1 = c6["y"].values
y2 = whole["y"].values

#%% Spatial specificity of BOLD responses, CombinedRuns
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white")
color_c6 = "orangered"
with sns.plotting_context('paper', font_scale = 2):
    fig, axScatter = plt.subplots(figsize=(12, 7))
    sns.regplot(data = whole, marker='o', x = 'x', y = 'y',
                           fit_reg = False, x_jitter = 0.5, seed=np.random.seed(2),
                           y_jitter = 0.5, color="grey", ax=axScatter,
                           scatter_kws = {'alpha' : 0.3, 's': 8}, label="C5 - C8")
    sns.regplot(data = c6, marker='o', x = 'x', y = 'y',
                            fit_reg = False, x_jitter = 0.5, seed=np.random.seed(22),
                            y_jitter = 0.5, color=color_c6, ax=axScatter,
                            scatter_kws = {'alpha' : 0.3, 's': 8}, label="C6")

    axScatter.set_xlim([55, 85])
    axScatter.set_ylim([62, 83])
    sns.despine(left=True, bottom=True)

    divider = make_axes_locatable(axScatter)
    axHistx = divider.append_axes("bottom", 1.2, pad=0.2, sharex=axScatter)
    axHisty = divider.append_axes("left", 1.2, pad=0.2, sharey=axScatter)

    # make some labels invisible
    axHistx.xaxis.set_tick_params(labelbottom=False)
    axHisty.yaxis.set_tick_params(labelleft=False)

    # #add density plots, x
    sns.kdeplot(np.array(x2), bw=0.5, ax=axHistx, color="grey", linewidth=0.6)
    sns.kdeplot(np.array(x1), bw=0.5, ax=axHistx, color=color_c6, linewidth=0.6)

    sns.kdeplot(np.array(y2), bw=0.5, ax=axHisty, color="grey", vertical=True, linewidth=0.6)
    sns.kdeplot(np.array(y1), bw=0.5, ax=axHisty, color=color_c6, vertical=True, linewidth=0.6)

    #add contour
    sns.kdeplot(data=slice_cord_array, x="x", y="y", levels=1, bw=0.2, color="k", linewidths=1, ax=axScatter)
    sns.kdeplot(data=dhl_df, x="x", y="y", levels=1, bw=0.4, color="k", linewidths=1, ax=axScatter)
    sns.kdeplot(data=dhr_df, x="x", y="y", levels=1, bw=0.4, color="k", linewidths=1, ax=axScatter)
    sns.kdeplot(data=vhl_df, x="x", y="y", levels=1, bw=0.4, color="k", linewidths=1, ax=axScatter)
    sns.kdeplot(data=vhr_df, x="x", y="y", levels=1, bw=0.4, color="k", linewidths=1, ax=axScatter)
    axHisty.invert_xaxis()
    axHistx.invert_yaxis()

    #despine axes
    axHistx.set_axis_off()
    axHisty.set_axis_off()
    axScatter.legend(bbox_to_anchor=(1.3, 1), loc='upper left',
                     borderaxespad=0, markerscale=5)

    # set the labels
    axScatter.set_xticks([59, 81])
    axScatter.set_xticklabels([' ', '  '])
    axScatter.set(xlabel=None)
    axScatter.set_yticks([64, 79])
    axScatter.set_yticklabels([' ', ' '])
    axScatter.set(ylabel=None)

    mpl.axes.Axes.set_aspect(axScatter, aspect="equal")
    #save
    plt.savefig(f'{out_dir}spatial_spec_CombinedRuns.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()
