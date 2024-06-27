#!/bin/bash
# 01_DenoiseMocoCombined.sh

# What shall be done
prepData=1
thermnoise=1
moco=1
moco_refined=1
csf_mask=1

# Loop across sessions for data preparation
for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    github_folder=/data/pt_02306/main/code/github/pain-reliability-spinalcord
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/sub-${sub}/ses-${ses}/func
    out_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing/CombinedRuns
    mkdir -p $out_dir

    # 1. prepare
    if [ $prepData = 1 ]; then
      cd $data_dir
      #define number of volumes, these were different for different sessions
      for file in $(find $data_dir/ -maxdepth 1 -name "sub*bold.nii.gz"); do
        echo "cutting file to 160 volumes" #in the beginning some scans were accidentally longer :)
        fname=$(basename "$file" | cut -d. -f1)
        echo $file
        numvol=160
        fslroi $file $out_dir/${fname}.nii.gz 0 $numvol
      done
    fi

    # 2. thermal denoising
    if [ $thermnoise = 1 ]; then
      cd $out_dir
      for file in $(find $out_dir/ -maxdepth 1 -name "*bold.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        echo "running thermal denoising"
        echo $file
        datain=$file
        folderout=$out_dir/
        #run function function thermalNoiseRemoval(filein, name, ofolder)
        matlab_script_dir=$github_folder/helper_functions/ #your github code folder here with
        matlab -nosplash -nodesktop -r "addpath(genpath('${matlab_script_dir}')); \
                                        try; thermalNoiseRemoval('$datain', '$fname', '$folderout'); catch ME; disp(ME); end; quit;"; # run matlab function from command line
      done
    fi

    #3. run moco across all runs combined
    if [ $moco = 1 ]; then
      cd $out_dir
      all_runs=()
      all_files=()
      numvol=()
      for file in $(find $out_dir/ -maxdepth 1 -name "*bold_denoised.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        all_blocks+=( "$fname" )
        all_files+=( "$fname.nii.gz" )
      done
      IFS=$'\n' all_files=($(sort <<<"${all_files[*]}"))
      unset IFS

      IFS=$'\n' all_runs=($(sort <<<"${all_runs[*]}"))
      unset IFS

      i=160
      for file in ${all_files[@]}; do
        numvol+=($i)
      done

      numblock=${#all_files[@]}
      numvol_all=$(IFS=+; echo "$((${numvol[*]}))")
      echo "number of volumes of all blocks:"${numvol[@]}
      echo "number of runs: "$numblock
      echo "all of vols overall:" $numvol_all
      echo "Starting moco_all now"

      # A) Create overall mean (which will be the target of motion correction)
      echo "merging"
      echo "runs to merge: "${all_files[@]}
      fslmerge -t $out_dir/tmp.nii.gz ${all_files[@]}
      cd $out_dir
      fslmaths tmp.nii.gz -Tmean all_runs_m.nii.gz

      # B) Create mask to be used for moco, based on this new overall mean
      echo "segmentation"
      sct_deepseg_sc -i all_runs_m.nii.gz -c t2s

      echo "creating mask"
      sct_create_mask -i all_runs_m.nii.gz -p centerline,all_runs_m_seg.nii.gz

      cd $out_dir
      echo "merging combined runs with moco mean"
       Create time-series composed of overall mean and all three sessions
      fslmerge -t $out_dir/tmpInput.nii.gz $out_dir/all_runs_m.nii.gz ${all_files[@]}

      # Do actual motion correction
      sct_fmri_moco -i tmpInput.nii.gz \
                    -m mask_all_runs_m.nii.gz \
                    -g 1 \
                    -param iterAvg=0,sampling=None \
                    -x spline

      # Clean up moco files (also remove mean from time-series, would need to be done for parameter files as well)
      fslroi tmpInput_moco.nii.gz tmpInput_moco.nii.gz 1 $numvol_all #always see what this would add up to, when 140 then its

      mv tmpInput_moco.nii.gz moco_all.nii.gz
      mv moco_params.tsv moco_all_params.tsv
      mv moco_params_x.nii.gz moco_all_params_x.nii.gz
      mv moco_params_y.nii.gz moco_all_params_y.nii.gz
      rm -f tmp*

      fslroi moco_all_params_x.nii.gz moco_all_params_x.nii.gz 1 $numvol_all
      fslroi moco_all_params_y.nii.gz moco_all_params_y.nii.gz 1 $numvol_all

      #Split up time-series back into original sessions (this would also need to be done for parameter files)
      echo ${numvol[@]}
      sum=(0)
      for ((i=0;i<$numblock;i++)); do
        echo ${all_runs[$i]}
        echo $sum ${numvol[$i]}
        fslroi moco_all.nii.gz ${all_runs[$i]}_moco_all.nii.gz $sum ${numvol[$i]}
        fslroi moco_all_params_x.nii.gz ${all_runs[$i]}_moco_all_params_x.nii.gz $sum ${numvol[$i]}
        fslroi moco_all_params_y.nii.gz ${all_runs[$i]}_moco_all_params_y.nii.gz $sum ${numvol[$i]}
        sum=$((sum + numvol[$i]))
      done

      # Calculate TSNR for moco_all
      fslmaths moco_all.nii.gz -Tmean moco_all_m.nii.gz
      fslmaths moco_all.nii.gz -Tstd moco_all_sd.nii.gz
      fslmaths moco_all_m.nii.gz -div moco_all_sd.nii.gz moco_all_t.nii.gz -odt float
    fi

    # 4. Run moco refined
    if [ $moco_refined = 1 ]; then
      all_runs=()
      all_files=()
      numvol=()
      for file in $(find $out_dir/ -maxdepth 1 -name "*bold_denoised.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        all_runs+=( "$fname" )
        all_files+=( "$fname.nii.gz" )
      done
      IFS=$'\n' all_files=($(sort <<<"${all_files[*]}"))
      unset IFS

      IFS=$'\n' all_runs=($(sort <<<"${all_runs[*]}"))
      unset IFS

      i=160
      for file in ${all_files[@]}; do
        numvol+=($i)
      done
      numblock=${#all_files[@]}
      numvol_all=$(IFS=+; echo "$((${numvol[*]}))")
      echo "number of volumes of all blocks:"${numvol[@]}
      echo "number of blocks: "$numblock
      echo "all of vols overall:" $numvol_all
      echo "Starting moco_all_refined now"
      cd $out_dir
      # Create time-series composed of overall mean and all three sessions
      fslmerge -t $out_dir/tmpInput.nii.gz $out_dir/moco_all_m.nii.gz ${all_files[@]}

      # Do actual motion correction
      sct_fmri_moco -i tmpInput.nii.gz \
                    -m mask_all_runs_m.nii.gz \
                    -g 1 \
                    -param iterAvg=0,sampling=None \
                    -x spline

      # Clean up moco files (also remove mean from time-series, would need to be done for parameter files as well)
      fslroi tmpInput_moco.nii.gz tmpInput_moco.nii.gz 1 $numvol_all #always see what this would add up to, when 140 then its

      mv tmpInput_moco.nii.gz moco_all_refined.nii.gz
      mv moco_params.tsv moco_all_params_refined.tsv
      mv moco_params_x.nii.gz moco_all_params_x_refined.nii.gz
      mv moco_params_y.nii.gz moco_all_params_y_refined.nii.gz
      rm -f tmp*

      fslroi moco_all_params_x_refined.nii.gz moco_all_params_x_refined.nii.gz 1 $numvol_all
      fslroi moco_all_params_y_refined.nii.gz moco_all_params_y_refined.nii.gz 1 $numvol_all

      #Split up time-series back into original sessions (this would also need to be done for parameter files)
      echo ${numvol[@]}
      sum=(0)
      for ((i=0;i<$numblock;i++)); do
        echo ${all_runs[$i]}
        echo $sum ${numvol[$i]}
        fslroi moco_all_refined.nii.gz ${all_runs[$i]}_moco_all_refined.nii.gz $sum ${numvol[$i]}
        fslroi moco_all_params_x_refined.nii.gz ${all_runs[$i]}_moco_all_refined_params_x.nii.gz $sum ${numvol[$i]}
        fslroi moco_all_params_y_refined.nii.gz ${all_runs[$i]}_moco_all_refined_params_y.nii.gz $sum ${numvol[$i]}
        sum=$((sum + numvol[$i]))
      done

      # Calculate TSNR for moco_all
      fslmaths moco_all_refined.nii.gz -Tmean moco_all_refined_m.nii.gz
      fslmaths moco_all_refined.nii.gz -Tstd moco_all_refined_sd.nii.gz
      fslmaths moco_all_refined_m.nii.gz -div moco_all_refined_sd.nii.gz moco_all_refined_t.nii.gz -odt float
    fi

    #5. create csf masks for pnm
    if [ $csf_mask = 1 ]; then
      cd $out_dir
      for file in $(find $out_dir/ -maxdepth 1 -name "*bold_denoised_moco_all_refined.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        #make run mean
        echo "making run mean"
        fslmaths ${fname}.nii.gz -Tmean ${fname}_m.nii.gz
        echo "segmenting run mean"
        sct_deepseg_sc -i ${fname}_m.nii.gz -c t2s
        #now build dilated mask for csf
        echo "building csf mask"
        sct_maths -i ${fname}_m_seg.nii.gz -dilate 4 -o ${fname}_dilated_mask.nii.gz
      done
    fi

  done
done
