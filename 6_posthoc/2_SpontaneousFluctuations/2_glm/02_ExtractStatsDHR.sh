#!/bin/bash
# 02_ExtractStatsDHR.sh

#on subject level we need:
#peak zstat & cope, #avg zstat & cope, all values in respective ROI zstat & cope
#rois:only c6, dh left, ventral horn right and respective dilated version

#we dont need group level extraction as this code will only check for changes in reliability, not spatial specificity.
#of course, code from the main analysis can be adapted to also get these results!

#what shall be done
extract_single_level=1

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
	    run_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/DHR
			cd $run_dir
			for i in $(ls -d *te40ReliabilityRun*.feat/); do
				data_dir=$run_dir/${i}stats/normalization
	  		out_dir=$data_dir/extracts
				mkdir -p $out_dir
				for stat in cope1 zstat1; do
					sct_register_multimodal -i $data_dir/${stat}_reg.nii.gz \
																	-d $mask_dir/PAM50_cord.nii.gz \
																	-identity 1 \
																	-o $data_dir/${stat}_reg.nii.gz

					for mask in dh_left_c6 vh_right_c6 c6_dl_dil c6_vr_dil; do
						fslmaths $data_dir/${stat}_reg.nii.gz -mas $mask_dir/${mask}.nii.gz $out_dir/${stat}_${mask}.nii.gz
						fslstats $out_dir/${stat}_${mask}.nii.gz  -R > $out_dir/${stat}_${mask}_min_max.txt
						fslmeants -i $data_dir/${stat}_reg.nii.gz -m $mask_dir/${mask}.nii.gz -o $out_dir/${stat}_${mask}_m.txt
						fslmeants -i $data_dir/${stat}_reg.nii.gz -m $mask_dir/${mask}.nii.gz -o $out_dir/${stat}_${mask}_all.txt --showall
					done
				done
			done
		done
  done
fi
