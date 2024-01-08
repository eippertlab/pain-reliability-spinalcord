#!/bin/bash
# 03_GroupLevel.sh

#what shall be done
prep_sessionwise=0
run_dhl_sessionwise=0
run_cord_sessionwise=0
run_cord_dil_sessionwise=0

prep_avg=0
run_dhl_avg=1
run_cord_avg=1
run_cord_dil_avg=1

#Directories
template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template
project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
mask_dir=$project_dir/derivatives/masks

if [ $prep_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "ses-${ses}"
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		mkdir -p $groupdir

		# Loop across sessions for data preparation
		full_cope=()
		for subject in {1..8}; do #{1..40}; do
			printf -v sub "%02d" $subject
      #subject directory
			data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/ReliabilityRun.feat/stats/normalization
			full_cope+="$data_dir/cope1_reg.nii.gz "
		done
		echo ${full_cope[@]}
		echo "merging"
		fslmerge -t $groupdir/ses-${ses}_cope_merged.nii.gz ${full_cope[@]}

		echo "cutting"
		#now cut in z direction so that all have same border for highest and lowest point of the cord!
		# lo: 763 hi: 877
		fslroi $groupdir/ses-${ses}_cope_merged.nii.gz $groupdir/ses-${ses}_cope_merged.nii.gz 0 141 0 141 763 114 0 -1
	done
fi

if [ $run_dhl_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "group level ttest ses-${ses}"
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		mkdir -p $groupdir/dh_left_c6

		#cut merged cope and mask so to limits over all participants
		cp $mask_dir/dh_left_c6.nii.gz $groupdir/dh_left_c6/dh_left_c6.nii.gz
		fslroi $groupdir/dh_left_c6/dh_left_c6.nii.gz $groupdir/dh_left_c6/dh_left_c6.nii.gz 0 141 0 141 763 114 0 -1

		#run randomise
		randomise -i $groupdir/ses-${ses}_cope_merged.nii.gz -m $groupdir/dh_left_c6/dh_left_c6.nii.gz -o $groupdir/dh_left_c6/dh_left_c6_ses-${ses}_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
	done
fi

if [ $run_cord_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "group level ttest ses-${ses}"
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		mkdir -p $groupdir/cord

		#cut merged cope and mask so to limits over all participants
		cp $mask_dir/PAM50_cord.nii.gz $groupdir/cord/cord.nii.gz
		fslroi $groupdir/cord/cord.nii.gz $groupdir/cord/cord.nii.gz 0 141 0 141 763 114 0 -1

		#run randomise
		randomise -i $groupdir/ses-${ses}_cope_merged.nii.gz -m $groupdir/cord/cord.nii.gz -o $groupdir/cord/cord_${ses}_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
	done
fi

if [ $run_cord_dil_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "group level ttest ses-${ses}"
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		mkdir -p $groupdir/cord_dilated

		#cut merged cope and mask so to limits over all participants
		cp $mask_dir/PAM50_cord_dilated.nii.gz $groupdir/cord_dilated/cord_dilated.nii.gz
		fslroi $groupdir/cord_dilated/cord_dilated.nii.gz $groupdir/cord_dilated/cord_dilated.nii.gz 0 141 0 141 763 114 0 -1

		#run randomise
		randomise -i $groupdir/ses-${ses}_cope_merged.nii.gz -m $groupdir/cord_dilated/cord_dilated.nii.gz -o $groupdir/cord_dilated/cord_dilated_${ses}_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
	done
fi

if [ $prep_avg = 1 ]; then
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		cope_dir=$groupdir/copes
		mkdir -p $cope_dir
		full_cope=()
		# Loop across subjects and sessions sessions for data preparation
		for subject in {1..4}; do
			echo "subject: $sub"
			printf -v sub "%02d" $subject
			sub_cope=()
			for session in {1..2}; do
				printf -v ses "%02d" $session
	      #Directories
				data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/ReliabilityRun.feat/stats/normalization
				sub_cope+="$data_dir/cope1_reg.nii.gz "
				if [[ $session = 2 ]]; then
					echo "$sub_cope"
					fslmerge -t $cope_dir/merge_sub-${sub}.nii.gz ${sub_cope[@]}
					fslmaths $cope_dir/merge_sub-${sub}.nii.gz -Tmean $cope_dir/cope_m_sub-${sub}.nii.gz
					full_cope+="$cope_dir/cope_m_sub-${sub}.nii.gz "
				fi
			done
		done
		echo ${full_cope[@]}
		echo "now merging! "
		fslmerge -t $cope_dir/cope_merged.nii.gz ${full_cope[@]}

		echo "done merging, now cutting!"
		#now cut in z direction so that all have same border for highest and lowest point of the cord!
		# lo: 763 hi: 877 --> subtract 877-736 thats how hi it should go
		fslroi $cope_dir/cope_merged.nii.gz $cope_dir/cope_merged.nii.gz 0 141 0 141 763 114 0 -1
fi

if [ $run_dhl_avg = 1 ]; then
	groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
	mkdir -p $groupdir/dh_left_c6
	echo "running the avg 2nd level analysis for dh left c6"
	randomise -i $groupdir/copes/cope_merged.nii.gz -m $groupdir/dh_left_c6/dh_left_c6.nii.gz -o $design_dir/$groupdir/dh_left_c6/dh_left_c6_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi

 if [ $run_cord_avg = 1 ]; then
	printf -v ses "%02d" $session
	echo "group level ttest ses-${ses}"
	groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
	mkdir -p $groupdir/cord
	#run randomise
	randomise -i $groupdir/copes/cope_merged.nii.gz -m $groupdir/cord/cord.nii.gz -o $groupdir/cord/cord_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi

 if [ $run_cord_dil_avg = 1 ]; then
		printf -v ses "%02d" $session
		groupdir=$project_dir/derivatives/results/glm/ReliabilityRun
		mkdir -p $groupdir/cord_dilated
		#run randomise
		randomise -i $groupdir/copes/cope_merged.nii.gz -m $groupdir/cord_dilated/cord_dilated.nii.gz -o $groupdir/cord_dilated/cord_dilated_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi
