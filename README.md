# pain-reliability-spinalcord
This repository is associated with the following [manuscript](https://www.biorxiv.org/content/10.1101/2023.12.22.572825v1) and the corresponding dataset. If you have any questions regarding this code, please feel free to reach out to dabbagh@cbs.mpg.de

## Content
This repository contains the preprocessing and analysis code needed to assess the reliability of task-based spinal cord fMRI as presented in above-mentioned manuscript. The code is organized into the sections: 
* 1_preprocessing: Preprocessing of fMRI and physiological data
* 2_glm: running Feat GLM, extracting masks in template space, running the group level analysis, extracting relevant statistics
* 3_heateffect: Assessing and plotting the effect of the heat stimulus for fMRI data and physiological measures and ratings
* 4_spatialspecificity: Plotting spatial specificity across all levels of the spinal cord in the GM horns, assessing the percentage of active voxels in each quadrant per level, and calculating dice coefficients for the left DH C6 on both group and individual level
* 5_reliability: Importing stats and calculating & plotting ICCs for each domain of interest
* 6_posthoc: Will be added soon
* helper_functions: Functions / templates needed for running the rest of the code

Bash scripts end on .sh, matlab scripts on .m and python scripts on .py! The number of the scripts tell you the order in which they should be run.

## Required software
* [MATLAB](https://de.mathworks.com/products/matlab.html) , version R2022b or higher
* [Spinal Cord Toolbox (SCT)](https://spinalcordtoolbox.com/index.html), version 5.5
* [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL) version 5.0 or higher
* [Python](https://www.python.org/) version 3.10.9
* For python packages: see requirements_python.txt
* Try to install required python packages via pip install -r requirements_python.txt
* Otherwise  each python script lists the version of the packages used at the top!

## Github repos
* https://github.com/NYU-DiffusionMRI/mppca_denoise
* https://github.com/pog87/PtitPrince

## Preprocessing & Analysis software
For preprocessing and calculation of results the following software was used:
* Bash: GNU bash, version 5.1.4(1)-release (x86_64-pc-linux-gnu)
* Spinal cord toolbox: sct_5.5
* Matlab version used: 9.13.0.2049777 (R2022b)
* FSL version 6.0.3
* PSPM toolbox: PsPM_v6.0.0
* EEGlab: eglab2019_0
* For ANTs N4BiasFieldCorrection: ANTs version 2.3.1
