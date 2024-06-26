#!/bin/bash
# SpinalLearning_2020_MotionOutliers is the helper function you will need here.

#1. find motion outliers in mocoed blocks
echo "detecting motion outliers for refined moco, CombinedRuns"

# Loop across sessions for data preparation
for subject in {1..41}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing/CombinedRuns
    out_dir=$data_dir/outliers
    mkdir -p $out_dir
    github_folder=/data/pt_02306/main/code/github/pain-reliability-spinalcord
    helper_functions=$github_folder/helper_functions

    cd $data_dir
    for file in $(find $data_dir/ -maxdepth 1  -name "sub*bold_denoised_moco_all_refined.nii.gz"); do
      fname=$(basename "$file" | cut -d. -f1)
      mask=$data_dir/mask_all_runs_m.nii.gz
      fsl_motion_outliers -i $file \
                          -m $mask \
                          -o $out_dir/${fname}_dvars2020 \
                          -s $out_dir/${fname}_dvars2020.txt \
                          --dvars --nomoco

      fsl_motion_outliers -i $file \
                          -m $mask \
                          -o $out_dir/${fname}_refrms2020 \
                          -s $out_dir/${fname}_refrms2020.txt \
                          --refrms --nomoco

      $helper_functions/fsl_motion_outliers_edited \
                          -i $file \
                          -m $mask \
                          -o $out_dir/${fname}_refrms2020edited \
                          -s $out_dir/${fname}_refrms2020edited.txt \
                          --refrms --nomoco
      done
    done

 done
done
