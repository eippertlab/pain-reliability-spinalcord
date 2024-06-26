#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
pandas version: 1.5.0
seaborn version: 0.11.0
matplotlib version: 3.6.3
"""
#%% Modules
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'
data_dir = f'{project_dir}derivatives/results/spatial_specificity/'
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

#%% #%% Fig. 4. Spatial specificity of BOLD responses across cord quadrants.
mpl.rcParams['pdf.fonttype'] = 42
sns.set(style="white")  
with sns.plotting_context('paper', font_scale=1.5):
    # Define a custom color palette
    color_palette = ["#384910", "#9c9088", "#e7b190", "#e8ab16"]
    index_colors = {index: color for index, color in zip(subset['index'].unique(), color_palette)}
    plt.figure(figsize=(7, 4))
    # Get unique levels from the DataFrame
    levels = percentages_df['level'].unique()
    bottom = [0] * len(levels)  # Initialize the bottom for stacked bars
    # Loop through each index and plot
    for index in percentages_df['index'].unique():
        active_voxels = []
        for level in levels:
            data = percentages_df[(percentages_df['level'] == level) & (percentages_df['index'] == index)]
            active_voxels.append(data['nside'].values[0] if not data.empty else 0)
        bars = plt.bar(levels, active_voxels, bottom=bottom, label=index, color=index_colors[index], width=0.8, alpha=0.7)
        bottom = [bottom[i] + active_voxels[i] for i in range(len(bottom))]  # Increment the bottom for the next stack
    # Annotate total nall value on top of each bar grouping
    for i, level in enumerate(levels):
        level_data = subset[subset['level'] == level]
        total_voxels = level_data['nall'].values[0]  # Assuming 'nall' is constant per level in the subset
        plt.text(i, bottom[i], f'Total: {int(total_voxels)}', ha='center', va='bottom', size=11)
    # Customize axes spines
    axes = plt.gca()
    for axis in ['bottom', 'left']:
        axes.spines[axis].set_linewidth(0.5)
    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)
    # Set labels and titles
    plt.xlabel('Spinal Level')
    plt.yticks([0,250, 500, 750, 1000])
    # Adjust the legend to be outside the plot
    plt.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Show the plot
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the layout to make space for the legend
    plt.savefig(f'{out_dir}spatial_spec_quadrants.png', bbox_inches='tight', format="png", dpi=300)
    plt.show()