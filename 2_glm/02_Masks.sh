#!/bin/bash
# 02_Masks.sh

#our EPIs cover C5, C6, C7 and C8

#what to do
build_horn_masks=0
build_dilated_quadrant_masks=1
build_cord_mask=1
build_quadrant_masks=1
delete_warping_files=1

#Directories
atlas_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/atlas #insert here your path to the SCT PAM50 atlas
template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template #insert here your path to the SCT PAM50 template
project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
mask_dir=$project_dir/derivatives/masks
mkdir -p $mask_dir

#1. create masks for each segmental level for DH left and right as well as VH left and right
if [ $build_horn_masks = 1 ]; then
  echo "building horn masks"
  cp $template_dir/PAM50_cord.nii.gz $mask_dir/PAM50_cord.nii.gz
  cp $template_dir/PAM50_t2s.nii.gz $mask_dir/PAM50_t2s.nii.gz

  declare -A atlas_files=(["vh_left"]=30 ["vh_right"]=31 ["dh_left"]=34 ["dh_right"]=35)

  for region in "${!atlas_files[@]}"; do
    cp $atlas_dir/PAM50_atlas_${atlas_files[$region]}.nii.gz $mask_dir/${region}.nii.gz
    fslmaths $mask_dir/${region}.nii.gz -bin $mask_dir/${region}.nii.gz

    # Define spinal cord levels and their corresponding slices
    declare -A levels=(["c5"]="844 33" ["c6"]="812 31" ["c7"]="778 33" ["c8"]="739 38")
    for level in "${!levels[@]}"; do
      slices=${levels[$level]}
      fslroi $mask_dir/${region}.nii.gz $mask_dir/${region}_${level} 0 -1 0 -1 $slices
      sct_register_multimodal -i $mask_dir/${region}_${level}.nii.gz \
                              -d $mask_dir/PAM50_cord.nii.gz \
                              -identity 1 \
                              -o $mask_dir/${region}_${level}.nii.gz
    done
  done
fi

#2. for each dilated quadrant (dorsal left right & ventral left right), make mask for each segment
if [ $build_dilated_quadrant_masks = 1 ]; then
  echo "making quadrant masks"
  cd $mask_dir
  sct_maths -i PAM50_cord.nii.gz -dilate 6 -o PAM50_cord_dilated.nii.gz

  # Define ROIs
  declare -A rois=(["roi_r"]="0 71 0 -1 0 -1" ["roi_r_s"]="0 70 0 -1 0 -1" ["roi_l"]="70 71 0 -1 0 -1" ["roi_d"]="0 -1 0 71 0 -1" ["roi_d_s"]="0 -1 0 70 0 -1" ["roi_v"]="0 -1 70 71 0 -1")

  # Create ROIs
  for roi in "${!rois[@]}"; do
    fslroi PAM50_cord_dilated.nii.gz $roi ${rois[$roi]}
  done

  # Create empty halves for merging
  fslmaths roi_r_s -mul 0 roi_null_r
  fslmaths roi_d_s -mul 0 roi_null_d

  # Merge ROIs
  fslmerge -y roi_d roi_d roi_null_d
  fslmerge -y roi_v roi_null_d roi_v
  fslmerge -x roi_r roi_r roi_null_r
  fslmerge -x roi_l roi_null_r roi_l

  # Create combined ROIs
  for side in r l; do
    for vert in v d; do
      fslmaths roi_${side} -mul roi_${vert} roi_${vert}${side}
    done
  done

  # Register ROIs to PAM50_cord
  for roi in dr vr dl vl; do
    sct_register_multimodal -i roi_${roi}.nii.gz -d PAM50_cord.nii.gz -identity 1 -o roi_${roi}.nii.gz
  done

  # Cut to spinal levels and multiply to make quadrant masks
  declare -A levels=(["c5"]="844 33" ["c6"]="812 31" ["c7"]="778 33" ["c8"]="739 38")
  for level in "${!levels[@]}"; do
    echo "making ${level} masks"
    fslroi PAM50_cord_dilated.nii.gz cord_${level}_dil 0 -1 0 -1 ${levels[$level]}
    sct_register_multimodal -i cord_${level}_dil.nii.gz -d PAM50_cord.nii.gz -identity 1 -o cord_${level}_dil.nii.gz

    for roi in dr vr dl vl; do
      fslmaths cord_${level}_dil.nii.gz -mul roi_${roi}.nii.gz ${level}_${roi}_dil.nii.gz
    done
  done
fi

#3. for entire cord section, create mask for each segment
if [ $build_cord_mask = 1 ]; then
  echo "cutting cord mask according to determined segmental coordinates"

  # Define spinal levels and their corresponding slices
  declare -A levels=(["c5"]="844 33" ["c6"]="812 31" ["c7"]="778 33" ["c8"]="739 38")

  for level in "${!levels[@]}"; do
    # Extract each spinal level
    fslroi $mask_dir/PAM50_cord.nii.gz $mask_dir/cord_${level} 0 -1 0 -1 ${levels[$level]}

    # Register to PAM50_cord
    sct_register_multimodal -i $mask_dir/cord_${level}.nii.gz \
                            -d $mask_dir/PAM50_cord.nii.gz \
                            -identity 1 \
                            -o $mask_dir/cord_${level}.nii.gz
  done
fi

#4. for not dilated but normal cord, create segmental mask for each quadrant (dorsal left right & ventral left right)
if [ $build_quadrant_masks = 1 ]; then
  echo "making quadrant masks"
  cd $mask_dir

  # Define ROIs
  declare -A rois=(["roi_r"]="0 71 0 -1 0 -1" ["roi_r_s"]="0 70 0 -1 0 -1" ["roi_l"]="70 71 0 -1 0 -1" ["roi_d"]="0 -1 0 71 0 -1" ["roi_d_s"]="0 -1 0 70 0 -1" ["roi_v"]="0 -1 70 71 0 -1")

  # Create ROIs
  for roi in "${!rois[@]}"; do
    fslroi PAM50_cord.nii.gz $roi ${rois[$roi]}
  done

  # Create empty halves for merging
  fslmaths roi_r_s -mul 0 roi_null_r
  fslmaths roi_d_s -mul 0 roi_null_d

  # Merge ROIs
  fslmerge -y roi_d roi_d roi_null_d
  fslmerge -y roi_v roi_null_d roi_v
  fslmerge -x roi_r roi_r roi_null_r
  fslmerge -x roi_l roi_null_r roi_l

  # Create combined ROIs
  for side in r l; do
    for vert in v d; do
      fslmaths roi_${side} -mul roi_${vert} roi_${vert}${side}
    done
  done

  # Register ROIs to PAM50_cord and get segmental level for each mask
  for roi in dr vr dl vl; do
    sct_register_multimodal -i roi_${roi}.nii.gz -d PAM50_cord.nii.gz -identity 1 -o roi_${roi}.nii.gz
    declare -A levels=(["c5"]="844 33" ["c6"]="812 31" ["c7"]="778 33" ["c8"]="739 38")
    for level in "${!levels[@]}"; do
      echo $level
      fslmaths cord_${level}.nii.gz -mul roi_${roi}.nii.gz ${level}_${roi}.nii.gz
    done
  done
fi

if [ $delete_warping_files = 1 ]; then
  #i dont need all the warping files, so I delete them to clear up some space. comment this out if you want to keep them :)
  rm -rf $mask_dir/warp*.nii.gz
fi
