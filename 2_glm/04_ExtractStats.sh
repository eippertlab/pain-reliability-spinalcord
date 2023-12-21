#!/bin/bash
# 04_ExtractStats.sh

#what shall be done
extract_roi=1
mask_dir=/data/pt_02306/main/data/derivatives/masks
if [ $extract_roi -eq 1 ]; then
	for model in denoised_single_2step_v2; do
		for subject in {1..40}; do
		  for session in {1..2}; do
				echo $model
		    printf -v sub "%02d" $subject
		    printf -v ses "%02d" $session
		    echo "subject: " $sub "session: " $ses
		    #Directories
		    project_dir=/data/pt_02306/main/data
		    data_dir=$project_dir/derivatives/glm/sub-${sub}/ses-${ses}/$model
		    cd $data_dir
		    for i in $(ls -d *te-40*refined.feat/); do
					if [[ $i = *"te-40_"* ]]; then
		  		  run_dir=$data_dir/${i}stats/normalization
						echo $run_dir
						out_dir=$run_dir/extracts
						mkdir -p $out_dir
						sct_register_multimodal -i $run_dir/cope1_normalized_spline.nii.gz \
					  												-d $mask_dir/PAM50_cord.nii.gz \
																		-identity 1 \
																		-o $run_dir/cope1_normalized_spline_pam50.nii.gz

						fslroi $run_dir/cope1_normalized_spline_pam50.nii.gz $run_dir/cope1_normalized_spline_pam50.nii.gz 0 141 0 141 763 114 0 -1
					  fslmaths $run_dir/cope1_normalized_spline_pam50.nii.gz -mas $mask_dir/dh_left_c6.nii.gz $out_dir/dh_left_c6_cope1.nii.gz
		 			  fslstats $out_dir/dh_left_c6_cope1.nii.gz  -R > $out_dir/dh_left_c6_min_max.txt
		 			  fslmeants -i $run_dir/cope1_normalized_spline_pam50.nii.gz -m $mask_dir/dh_left_c6.nii.gz -o $out_dir/dh_left_c6_m.txt
						fslmeants -i $run_dir/cope1_normalized_spline_pam50.nii.gz -m $mask_dir/dh_left_c6.nii.gz -o $out_dir/dh_left_c6_all.txt --showall
					fi
					done
			  done
			done
		done
	fi
