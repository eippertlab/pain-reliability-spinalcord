#!/bin/bash
# 04_ExtractStats.sh

#on subject level we need:
#peak zstat & cope, #avg zstat & cope, all values in respective ROI zstat & cope
#rois:only c6, dh left, ventral horn right and respective dilated version

#on group level we need:
#uncorrected p values for each quadrant per segment,
#uncorrected p values within each horn per segment

#what shall be done
extract_single_level=1
extract_group_level=1
extract_group_level_dhlc6=1

#Directories
project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
mask_dir=$project_dir/derivatives/masks

if [ $extract_single_level -eq 1 ]; then
	for subject in {1..40}; do
	  for session in {1..2}; do
			echo $model
	    printf -v sub "%02d" $subject
	    printf -v ses "%02d" $session
	    echo "subject: " $sub "session: " $ses
	    #Directories
	    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/CombinedRuns
	    out_dir=$data_dir/extracts
			mkdir -p $out_dir
			for stat in cope zstat; do
				sct_register_multimodal -i $data_dir/${stat}_m_sub-${sub}_ses-${ses}.nii.gz \
																-d $mask_dir/PAM50_cord.nii.gz \
																-identity 1 \
																-o $data_dir/${stat}_m_sub-${sub}_ses-${ses}.nii.gz

				for mask in dh_left_c6 vh_right_c6 c6_dl_dil c6_vr_dil; do
				  fslmaths $data_dir/${stat}_m_sub-${sub}_ses-${ses}.nii.gz -mas $mask_dir/${mask}.nii.gz $out_dir/${stat}_${mask}.nii.gz
				  fslstats $out_dir/${stat}_${mask}.nii.gz  -R > $out_dir/${stat}_${mask}_min_max.txt
				  fslmeants -i $data_dir/${stat}_m_sub-${sub}_ses-${ses}.nii.gz -m $mask_dir/${mask}.nii.gz -o $out_dir/${stat}_${mask}_m.txt
					fslmeants -i $data_dir/${stat}_m_sub-${sub}_ses-${ses}.nii.gz -m $mask_dir/${mask}.nii.gz -o $out_dir/${stat}_${mask}_all.txt --showall
				done
			done
		done
  done
fi

if [ $extract_group_level = 1 ]; then
	rois=(dh_left dh_right vh_left vh_right)
	levs=(c5 c6 c7 c8)
  groupdir=$project_dir/derivatives/results/CombinedRuns/glm/cord
	sct_register_multimodal -i $groupdir/cord_avg_OneSampT_masked_vox_p_tstat1.nii.gz \
													-d $mask_dir/PAM50_cord.nii.gz \
													-identity 1 \
													-o $groupdir/cord_avg_OneSampT_masked_vox_p_tstat1.nii.gz
	extract GM horns
  for i in {0..3}; do
    for n in {0..3}; do
       fslmeants -i $groupdir/cord_avg_OneSampT_masked_vox_p_tstat1.nii.gz -m $mask_dir/${rois[$i]}_${levs[$n]}.nii.gz  -o $groupdir/${levs[$n]}_${rois[$i]}_vox_p_all.txt --showall
    done
  done

	#extract cord quadrants
	rois=(dr vr dl vl)
	for i in {0..3}; do
    for n in {0..3}; do
       fslmeants -i $groupdir/cord_avg_OneSampT_masked_vox_p_tstat1.nii.gz -m $mask_dir/${levs[$n]}_${rois[$i]}.nii.gz  -o $groupdir/${levs[$n]}_${rois[$i]}_vox_p_all.txt --showall
    done
  done
fi
if [ $extract_group_level_dhlc6 = 1 ]; then
	for session in {1..2}; do
    printf -v ses "%02d" $session
	  groupdir=$project_dir/derivatives/results/CombinedRuns/glm/dh_left_c6
		sct_register_multimodal -i $groupdir/dh_left_c6_ses-${ses}_OneSampT_masked_vox_p_tstat1.nii.gz \
														-d $mask_dir/PAM50_cord.nii.gz \
														-identity 1 \
														-o $groupdir/dh_left_c6_ses-${ses}_OneSampT_masked_vox_p_tstat1.nii.gz
		#extract DHL c6
    fslmeants -i $groupdir/dh_left_c6_ses-${ses}_OneSampT_masked_vox_p_tstat1.nii.gz -m $mask_dir/dh_left_c6.nii.gz  -o $groupdir/dh_left_c6_ses-${ses}_vox_p_all.txt --showall
	done
fi
