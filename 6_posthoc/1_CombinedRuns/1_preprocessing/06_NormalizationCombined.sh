#!/bin/bash
# 06_Normalization.sh

# What shall be done?
#normalization of T2w can be found in github/pain-reliability-spinalcord/1_preprocessing/06_Normalization.sh first part, no need to repeat here :)
normalize_epi=1

# Loop across sessions for data preparation
for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    anat_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/anat/preprocessing/normalization
    data_dir_epi=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing/CombinedRuns
    out_dir_epi=$data_dir_epi/normalization
    mkdir -p $out_dir_epi
    template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template #insert here your path to the SCT PAM50 template

    # Normalize  ReliabilityRun moco refined epi and create warp fields
    if [ $normalize_epi = 1 ]; then
      fname=moco_all_refined
      echo "normalizing epi $fname, subject:  $sub session:  $ses"

      #prepare
      cp $anat_dir/warp_anat2template.nii.gz $out_dir_epi/warp_anat2template.nii.gz
      cp $anat_dir/warp_template2anat.nii.gz $out_dir_epi/warp_template2anat.nii.gz
      cd $data_dir_epi
      #segment moco_all_refined_m!
      sct_deepseg_sc -i ${fname}_m.nii.gz -c t2s

      cd $out_dir_epi
      echo "registering epi"
      sct_register_multimodal -i $template_dir/PAM50_t2s.nii.gz \
                             -d $data_dir_epi/${fname}_m.nii.gz \
                             -iseg $template_dir/PAM50_cord.nii.gz \
                             -dseg $data_dir_epi/${fname}_m_seg.nii.gz \
                             -param step=1,type=seg,algo=centermass:step=2,type=seg,algo=bsplinesyn \
                             -initwarp warp_template2anat.nii.gz \
                             -initwarpinv warp_anat2template.nii.gz \
                             -x spline \
                             -ofolder $out_dir_epi
    fi

  done
done
