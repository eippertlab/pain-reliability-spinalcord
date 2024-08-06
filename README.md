[![GitHub Release](https://img.shields.io/github/v/release/eippertlab/pain-reliability-spinalcord)](https://github.com/eippertlab/pain-reliability-spinalcord/releases/tag/v1.0)
[![DOI](https://zenodo.org/badge/733083740.svg)](https://zenodo.org/doi/10.5281/zenodo.10518643)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# pain-reliability-spinalcord
This repository is associated with the following [manuscript](https://doi.org/10.1162/imag_a_00273) and the corresponding [dataset](https://openneuro.org/datasets/ds004926). If you have any questions regarding this code, please feel free to reach out to dabbagh@cbs.mpg.de.

## Content
This repository contains the preprocessing and analysis code needed to assess the reliability of task-based spinal cord fMRI as presented in above-mentioned manuscript. The code is organized into the sections: 
* 1_preprocessing: Preprocessing of fMRI and physiological data
* 2_glm: running Feat GLM, extracting masks in template space, running the group level analysis, extracting relevant statistics
* 3_heateffect: Assessing and plotting the effect of the heat stimulus for fMRI data and physiological measures and ratings
* 4_spatialspecificity: Plotting spatial specificity across all levels of the spinal cord in the GM horns, assessing the percentage of active voxels in each quadrant per level, and calculating dice coefficients for the left DH C6 on both group and individual level
* 5_reliability: Calculating & plotting ICCs for each domain of interest
  
Sections 1-5 make up the ReliabilityRun pipeline!

* 6_posthoc: Preprocessing and analysis code needed to assess changes in reliability from three further sets of analyses, which we had not specified in the preregistration: Increasing the number of runs, accounting for spontaneous activations and within-run reliability. The main pipelineneeds to be run first! The order in which the sub-analyses need to be run is indicated by numbers.
* 7_quality: Analysis of physiological state and data quality of the reliability run across days
* helper_functions: Functions / templates needed for running the rest of the code

Bash scripts end on .sh, matlab scripts on .m and python scripts on .py! The number of the scripts tell you the order in which they should be run.

## Required software
* [MATLAB](https://de.mathworks.com/products/matlab.html) , version R2022b or higher
* [Spinal Cord Toolbox (SCT)](https://spinalcordtoolbox.com/index.html), version 5.5; segmental mask coordinates from version 6.1
* [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL) version 5.0 or higher
* [Python](https://www.python.org/) version 3.10.9
* For python packages: see requirements_python.txt
* Try to install required python packages via pip install -r requirements_python.txt
* Otherwise  each python script lists the version of the packages used at the top!

## Github repos
* https://github.com/NYU-DiffusionMRI/mppca_denoise
* https://github.com/pog87/PtitPrince

## Matlab repos
* https://sites.google.com/site/pierrickcoupe/softwares/denoising/mri-denoising/mri-denoising-software

## Preprocessing & Analysis software
For preprocessing and calculation of results the following software was used:
* Bash: GNU bash, version 5.1.4(1)-release (x86_64-pc-linux-gnu)
* Spinal cord toolbox: sct_5.5
* Matlab version used: 9.13.0.2049777 (R2022b)
* FSL version 6.0.3
* PSPM toolbox: PsPM6.1
* EEGlab: eglab2019_0
* For ANTs N4BiasFieldCorrection: ANTs version 2.3.1
