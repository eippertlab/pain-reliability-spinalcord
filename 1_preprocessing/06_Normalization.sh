#!/bin/bash
# 06_Normalization.sh

# What shall be done?
normalize_t2=1
normalize_epi=1

# Loop across sessions for data preparation
for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/anat/preprocessing
    qc_dir=$data_dir/qc
    out_dir=$data_dir/normalization
    mkdir -p $out_dir
    data_dir_epi=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    out_dir_epi=$data_dir_epi/normalization/ReliabilityRun
    mkdir -p $out_dir_epi
    template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template #insert here your path to the SCT PAM50 template

    #1. normalize T2
    if [ $normalize_t2 = 1 ]; then
      cd $data_dir
      echo "normalizing T2w for subject: $sub session: $ses"
      for file in $(find . -name "*_T2w.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        sct_register_to_template -i ${fname}_crop_biascorr_denoise.nii.gz \
                                 -s ${fname}_seg.nii.gz \
                                 -ldisc ${fname}_labeled_discs.nii.gz \
                                 -param step=1,type=seg,algo=centermassrot \
                                 -c t2 \
                                 -ofolder $out_dir \
                                 -qc $qc_dir/normalization_t2
      done
     fi

     #2. Normalize  ReliabilityRun moco refined epi and create warp fields
     if [ $normalize_epi = 1 ]; then
       echo "normalizing epi ReliabilityRun, subject:  $sub session:  $ses"
       for file in $(find $data_dir_epi/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
         fname=$(basename "$file" | cut -d. -f1)
         #prepare
         cp $out_dir/warp_anat2template.nii.gz $out_dir_epi/warp_anat2template.nii.gz
         cp $out_dir/warp_template2anat.nii.gz $out_dir_epi/warp_template2anat.nii.gz
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
        done
      fi

  done
done
