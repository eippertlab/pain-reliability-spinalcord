#!/bin/bash
# 5_TSNRExtractQuality.sh

# Loop across sessions for data preparation
for subject in {1..4}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    github_folder=/data/pt_02306/main/code/github/pain-reliability-spinalcord
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    out_dir=$data_dir

    #get single voxel data for TSNR plotting via fslmeants
    for file in $(find $data_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
      fname=$(basename "$file" | cut -d. -f1)
      echo "getting single voxel data for "$fname
      fslmeants -i $data_dir/${fname}_t.nii.gz -o $out_dir/${fname}_t.txt -m $data_dir/${fname}_m_seg.nii.gz --showall
    done
  done
done
