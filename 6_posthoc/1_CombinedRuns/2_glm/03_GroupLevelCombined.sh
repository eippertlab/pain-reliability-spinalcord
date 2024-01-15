#!/bin/bash
# 03_GroupLevelCombined.sh

#what shall be done
prep_sessionwise=1
run_dhl_sessionwise=1
run_cord_sessionwise=1
run_cord_dil_sessionwise=1

prep_avg=1
run_dhl_avg=1
run_cord_avg=1
run_cord_dil_avg=1

#Directories
template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template
project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
mask_dir=$project_dir/derivatives/masks
groupdir=$project_dir/derivatives/results/CombinedRuns/glm
mkdir -p $groupdir
cope_dir=$groupdir/copes
mkdir -p $cope_dir

if [ $prep_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "ses-${ses}"
		# Loop across sessions for data preparation
		ses_cope=()
		full_cope=()
		for subject in {1..40}; do 
			printf -v sub "%02d" $subject
			sub_cope=()
			sub_zstat=() #zstat is not needed for second level, but for later reliability analysis
      #subject directory
			data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/CombinedRuns
			cd $data_dir
			for i in $(ls -d *moco_all_refined.feat/); do
				run_dir=$data_dir/${i}stats/normalization
				sub_cope+="$run_dir/cope1_reg.nii.gz "
				sub_zstat+="$run_dir/zstat1_reg.nii.gz "
			done
			echo "merging: ${sub_cope[@]}"
			fslmerge -t $cope_dir/merge_sub-${sub}_ses-${ses}.nii.gz ${sub_cope[@]}
			fslmaths $cope_dir/merge_sub-${sub}_ses-${ses}.nii.gz -Tmean $cope_dir/cope_m_sub-${sub}_ses-${ses}.nii.gz
			ses_cope+="$cope_dir/cope_m_sub-${sub}_ses-${ses}.nii.gz "

			#for later reliability analyis, bring mean cope per session to glm folder
			cp $cope_dir/cope_m_sub-${sub}_ses-${ses}.nii.gz $data_dir/cope_m_sub-${sub}_ses-${ses}.nii.gz

			#for later reliability analysis, get mean zstat per session to glm folder as well
			echo "merging: ${sub_zstat[@]}"
			fslmerge -t $data_dir/merge_sub-${sub}_ses-${ses}_zstat.nii.gz ${sub_zstat[@]}
			fslmaths $data_dir/merge_sub-${sub}_ses-${ses}_zstat.nii.gz -Tmean $data_dir/zstat_m_sub-${sub}_ses-${ses}.nii.gz
		done
		full_cope=($(echo "${ses_cope[@]}" | sed 's/ /\n/g' | sort))
		echo ${full_cope[@]} ${#full_cope[@]}
		echo "now merging! "
		fslmerge -t $groupdir/ses-${ses}_cope_merged.nii.gz ${full_cope[@]}
		echo "done merging, now cutting!"
		#now cut in z direction so that all have same border for highest and lowest point of the cord!
		# lo: 763 hi: 877 --> subtract 877-736 thats how hi it should go
		fslroi $groupdir/ses-${ses}_cope_merged.nii.gz $groupdir/ses-${ses}_cope_merged.nii.gz 0 141 0 141 763 114 0 -1
	done
fi

if [ $run_dhl_sessionwise = 1 ]; then
	for session in {1..2}; do
		printf -v ses "%02d" $session
		echo "group level ttest ses-${ses}"
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
		mkdir -p $groupdir/cord_dilated

		#cut merged cope and mask so to limits over all participants
		cp $mask_dir/PAM50_cord_dilated.nii.gz $groupdir/cord_dilated/cord_dilated.nii.gz
		fslroi $groupdir/cord_dilated/cord_dilated.nii.gz $groupdir/cord_dilated/cord_dilated.nii.gz 0 141 0 141 763 114 0 -1

		#run randomise
		randomise -i $groupdir/ses-${ses}_cope_merged.nii.gz -m $groupdir/cord_dilated/cord_dilated.nii.gz -o $groupdir/cord_dilated/cord_dilated_${ses}_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
	done
fi

if [ $prep_avg = 1 ]; then
		full_cope=()
		# Loop across subjects and sessions sessions for data preparation
		for subject in {1..4}; do
			echo "subject: $sub"
			printf -v sub "%02d" $subject
			sub_cope=()
			for session in {1..2}; do
				sub_cope+="$cope_dir/cope_m_sub-${sub}_ses-${ses}.nii.gz "
			done
			echo "merging ${sub_cope[@]} ${#sub_cope[@]}"
			fslmerge -t $cope_dir/merge_sub-${sub}_avg.nii.gz ${sub_cope[@]}
			fslmaths $cope_dir/merge_sub-${sub}_avg.nii.gz -Tmean $cope_dir/cope_m_sub-${sub}_avg.nii.gz
			full_cope+="$cope_dir/cope_m_sub-${sub}_avg.nii.gz "
		done
		full_cope=($(echo "${full_cope[@]}" | sed 's/ /\n/g' | sort))
		echo ${full_cope[@]} ${#full_cope[@]}
		echo "now merging! "
		fslmerge -t $groupdir/avg_cope_merged.nii.gz ${full_cope[@]}

		echo "done merging, now cutting!"
		#now cut in z direction so that all have same border for highest and lowest point of the cord!
		# lo: 763 hi: 877 --> subtract 877-736 thats how hi it should go
		fslroi $groupdir/avg_cope_merged.nii.gz $groupdir/avg_cope_merged.nii.gz 0 141 0 141 763 114 0 -1
fi

if [ $run_dhl_avg = 1 ]; then
	mkdir -p $groupdir/dh_left_c6
	echo "running the avg 2nd level analysis for dh left c6"
	randomise -i $groupdir/avg_cope_merged.nii.gz -m $groupdir/dh_left_c6/dh_left_c6.nii.gz -o $groupdir/dh_left_c6/dh_left_c6_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi

 if [ $run_cord_avg = 1 ]; then
	echo "running the avg 2nd level analysis for cord"
	mkdir -p $groupdir/cord
	randomise -i $groupdir/avg_cope_merged.nii.gz -m $groupdir/cord/cord.nii.gz -o $groupdir/cord/cord_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi

 if [ $run_cord_dil_avg = 1 ]; then
	  echo "running the avg 2nd level analysis for dilated cord"
		mkdir -p $groupdir/cord_dilated
		#run randomise
		randomise -i $groupdir/avg_cope_merged.nii.gz -m $groupdir/cord_dilated/cord_dilated.nii.gz -o $groupdir/cord_dilated/cord_dilated_avg_OneSampT_masked -1 --uncorrp -T -x -c 2.3 -C 2.3
 fi
