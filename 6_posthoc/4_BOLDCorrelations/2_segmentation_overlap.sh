#!/bin/bash
# 1_segmentation_overlap.sh

# Loop across sessions for data preparation
process_subject() {
  sub=$1
  echo "Processing subject: " $sub
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing/normalization
    cd $data_dir

    #get segmentations of normalized mean EPI
    for file in $(find $data_dir/ -maxdepth 1 -name "*te40ReliabilityRun*refined_m_reg.nii.gz"); do
      fname=$(basename "$file" | cut -d. -f1)
      sct_deepseg_sc -i ${fname}.nii.gz -c t2s
      fslroi ${fname}_seg.nii.gz ${fname}_seg_cut.nii.gz 0 141 0 141 763 114 0 -1

      echo "getting single voxel data for "$fname
      fslmeants -i ${fname}_seg_cut.nii.gz -m ${fname}_seg_cut.nii.gz -o ${fname}_seg_t.txt --showall
    done
  done
}

# Loop across subjects for data preparation in parallel
for subject in {1..40}; do #1; do #{1..5}; do
  printf -v sub "%02d" $subject
  echo "Starting parallel processing for subject: sub-"$sub
  #process_subject $sub &  # Start in the background
done

# Wait for all background processes to finish
wait
echo "All parallel processes completed."

mask_dir=/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/masks/
fslroi $mask_dir/PAM50_cord.nii.gz $mask_dir/PAM50_cord_cut_cut.nii.gz 0 141 0 141 763 114 0 -1
fslmeants -i $mask_dir/PAM50_cord_cut.nii.gz -m $mask_dir/PAM50_cord_cut.nii.gz -o $mask_dir/PAM50_cord_cut_t.txt --showall
