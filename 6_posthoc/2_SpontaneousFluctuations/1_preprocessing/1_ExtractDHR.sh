#!/bin/bash
# 1_ExtractDHR.sh
# create mask that

# What shall be done
prep_mask=1
extract_timeseries=1

#common directories
atlas_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/atlas #insert here your path to the SCT PAM50 atlas
project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
mask_dir=$project_dir/derivatives/masks
dh_template=PAM50_atlas_35

fslmaths $atlas_dir/${dh_template}.nii.gz -bin $mask_dir/${dh_template}_bin_00.nii.gz -odt int

# Loop across sessions for data preparation
for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses
    #Directories
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    normalization_dir=$data_dir/normalization
    out_dir=$data_dir/DHR
    mkdir -p $out_dir
    # 1. prepare
    if [ $prep_mask = 1 ]; then
      #for prepping the mask: get dh right mask into anatomical space
      #right dorsal horn: atlas_35
      cd $data_dir
      for destination_file in $(find $data_dir/ -maxdepth 1 -name "sub*te40ReliabilityRun*bold_denoised_moco_refined_m.nii.gz"); do
        destination=$(basename "$destination_file" | cut -d. -f1)
      done
      echo $destination

      cd $normalization_dir
      for warp_file in $(find $normalization_dir/ -maxdepth 1 -name "warp_PAM50_t2s2sub-*te40ReliabilityRun*bold_denoised_moco_refined_m.nii.gz"); do
        warpname=$(basename "$warp_file" | cut -d. -f1)
      done
      echo $warpname

      echo "binarize DH atlas mask"
      echo "get DH mask into anat space"
      sct_apply_transfo -i $mask_dir/${dh_template}_bin_00.nii.gz \
                        -d $destination_file \
                        -w $warp_file \
                        -x nn \
                        -o $out_dir/dh_right_anat.nii.gz
    fi

    # 2. get time-series
    if [ $extract_timeseries = 1 ]; then
      echo "getting time series now"
      cd $data_dir
      for file in $(find $data_dir/ -maxdepth 1 -name "sub*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)

        #define
        img=$data_dir/${fname}.nii.gz
        mask=$out_dir/dh_right_anat.nii.gz #
        if [[ $subject = 20 && $session = 1 ]]; then
          echo "correct sub-$sub, ses-$ses manually!"
          mask=$out_dir/dh_right_anat_corr.nii.gz
        fi
        tsname=$out_dir/${fname}_dhr.txt

        fslmeants -i $img -o $tsname -m $mask --showall
      done
    fi

  done
done
