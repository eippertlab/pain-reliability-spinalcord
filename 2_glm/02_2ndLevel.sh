#!/bin/bash
# 02_2ndLevel.sh

# Before running this script, you need to have set up a higher-level design, e.g.
# using Glm_gui (command: Glm).

#what shall be done
prep=1
run=1

model_main=denoised_single_2step_v2
model_data=denoised_single_2step_v2

template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template

if [ $prep = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "ses-${ses}"
		design_dir=/data/pt_02306/main/data/derivatives/glm/results/${model_main}/separate_sessions
		mkdir -p $design_dir
		full_cope=()

		# Loop across sessions for data preparation
		for subject in {1..40}; do
			printf -v sub "%02d" $subject
	      #Directories
				data_dir=/data/pt_02306/main/data/derivatives/glm/sub-${sub}/ses-${ses}/${model_data}
				if [ -d "$data_dir" ]; then
					cd $data_dir
					  for i in $(ls -d *.feat/); do
							run_dir=$data_dir/${i}stats/normalization
							if [[ $run_dir = *"te-40_"* ]]; then
								full_cope+="$run_dir/cope1_normalized_spline.nii.gz "
							else
								continue
							fi
						done
				fi
		done
		echo ${full_cope[@]}
		echo "now merging! "
		fslmerge -t $design_dir/ses-${ses}_cope_merged_spline.nii.gz ${full_cope[@]}

		echo "done merging, now cutting!"
		#now cut in z direction so that all have same border for highest and lowest point of the cord!
		# lo: 763 hi: 877
		fslroi $design_dir/ses-${ses}_cope_merged_spline.nii.gz $design_dir/ses-${ses}_cope_merged_spline.nii.gz 0 141 0 141 763 114 0 -1
	done
fi

if [ $run = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "ses-${ses}"
		design_dir=/data/pt_02306/main/data/derivatives/glm/results/${model_main}/separate_sessions
		mkdir -p $design_dir/dh_l_c6
		mask_dir=/data/pt_02306/main/data/derivatives/glm/results/pnm_param/main/masks
		echo "running the 2nd level analysis for " $ses
		randomise -i $design_dir/ses-${ses}_cope_merged_spline.nii.gz -m $mask_dir/dh_l_c6.nii.gz -o $design_dir/dh_l_c6/dh_l_c6_ses-${ses}_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
		done
fi
