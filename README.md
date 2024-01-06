# pain-reliability-spinalcord
This repository is associated with the following [manuscript](https://www.biorxiv.org/content/10.1101/2023.12.22.572825v1.article-metrics) and the corresponding dataset.

## Content
This repository contains the preprocessing and analysis code needed to assess the reliability of task-based spinal cord fMRI as presented in above-mentioned manuscript. The code is organized into the sections: 
<li>1_preprocessing: preprocessing of fMRI and physiological data</li>
<li>2_glm: running Feat GLM, extracting masks in template space, running the group level analysis, extracting relevant statistics</li>
<li>3_heateffect: assessing and plotting the effect of the heat stimulus for fMRI data and physiological measures and ratings</li>
<li>4_spatialspecificity: plotting spatial specificity across all levels of the spinal cord in the GM horns, assessing the perceptage of active voxels in each quadrant per level, and calculating dice coefficients for the left DH C6 on both group and individual level</li>
<li>5_reliability: importing stats and calculating & plotting ICCs for each domain of interest</li>
<li>6_posthoc: Will be added soon</li>
<li>helper_functions: functions / templates needed for running the rest of the code</li>

## Required software
<li>[MATLAB](https://de.mathworks.com/products/matlab.html) , version R2022b or higher</li>
<li>[Spinal Cord Toolbox (SCT)](https://spinalcordtoolbox.com/index.html), version 5.5</li>
<li>[FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL) version 5.0 or higher</li>
<li>[Python](https://www.python.org/) version 3.10.9</li>
<li>For python packages: see requirements_python.txt</li>
<li>try to install required python packages via pip install -r requirements_python.txt</li>
<li>Otherwise  each python script lists the version of the packages used at the top!</li>

## Github repos
<li>https://github.com/NYU-DiffusionMRI/mppca_denoise</li>
<li>https://github.com/pog87/PtitPrince</li>

## Preprocessing & Analysis software
For preprocessing and calculation of results the following software was used:
<li>Bash: GNU bash, version 5.1.4(1)-release (x86_64-pc-linux-gnu)</li>
<li>Spinal cord toolbox: sct_5.5</li>
<li>Matlab version used: 9.13.0.2049777 (R2022b)</li>
<li>FSL version 6.0.3</li>
<li>PSPM toolbox: PsPM_v6.0.0</li>
<li>EEGlab: eglab2019_0</li>
<li>For ANTs N4BiasFieldCorrection: ANTs version 2.3.1</li>
