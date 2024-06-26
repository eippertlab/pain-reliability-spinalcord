#!/bin/bash
# 01_DenoiseMoco.sh

# What shall be done
prepData=1
thermnoise=1
moco=1
moco_refined=1
csf_mask=1

# Loop across sessions for data preparation
for subject in {1..4}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    github_folder=/data/pt_02306/main/code/github/pain-reliability-spinalcord
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/sub-${sub}/ses-${ses}/func
    out_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    mkdir -p $out_dir

    # 1. prepare
    if [ $prepData = 1 ]; then
      cd $data_dir
      #define number of volumes, these were different for different sessions
      for file in $(find $data_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold.nii.gz"); do
        echo "cutting file to 160 volumes"
        fname=$(basename "$file" | cut -d. -f1)
        echo $file
        numvol=160
        fslroi $file $out_dir/${fname}.nii.gz 0 $numvol
      done
    fi

    # 2. thermal denoising
    if [ $thermnoise = 1 ]; then
      cd $out_dir
      for file in $(find $out_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold.nii.gz"); do
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

    #3. run moco
    if [ $moco = 1 ]; then
      cd $out_dir
      echo $out_dir
      numvol=160
      for file in $(find $out_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised.nii.gz"); do
        echo "running moco"
        fname=$(basename "$file" | cut -d. -f1)
        fslmaths $file -Tmean ${fname}_m.nii.gz

        # B) Create mask to be used for moco, based on this new overall mean
        echo "segmentation"
        sct_deepseg_sc -i ${fname}_m.nii.gz -c t2s

        echo "Done with segmentation, continuing"
        sct_create_mask -i ${fname}_m.nii.gz -p centerline,${fname}_m_seg.nii.gz #size: 41 pixels

        # Prepend mean image to time-series
        fslmerge -t ${fname}_tmpInput.nii.gz ${fname}_m.nii.gz $file

        # Do actual motion correction
        sct_fmri_moco -i ${fname}_tmpInput.nii.gz \
                      -m mask_${fname}_m.nii.gz \
                      -g 1 \
                      -param iterAvg=0,sampling=None \
                      -x spline

        # Clean up moco files (also remove mean from time-series, would need to be done for parameter files as well)
        mv ${fname}_tmpInput_moco.nii.gz ${fname}_moco.nii.gz
        rm -f *tmpInput*

        fslroi ${fname}_moco.nii.gz ${fname}_moco.nii.gz 1 $numvol #always see what this would add up to, when 140 then its
        mv moco_params.tsv ${fname}_moco_params.tsv
        mv moco_params_x.nii.gz ${fname}_moco_params_x.nii.gz
        mv moco_params_y.nii.gz ${fname}_moco_params_y.nii.gz

        fslroi ${fname}_moco_params_x.nii.gz ${fname}_moco_params_x.nii.gz 1 $numvol
        fslroi ${fname}_moco_params_y.nii.gz ${fname}_moco_params_y.nii.gz 1 $numvol

        # Calculate TSNR for moco
        fslmaths ${fname}_moco.nii.gz -Tmean ${fname}_moco_m.nii.gz
        fslmaths ${fname}_moco.nii.gz -Tstd ${fname}_moco_sd.nii.gz
        fslmaths ${fname}_moco_m.nii.gz -div ${fname}_moco_sd.nii.gz ${fname}_moco_t.nii.gz -odt float
      done
    fi

    #4. run refined moco
    if [ $moco_refined = 1 ]; then
      echo "running refined moco"
      cd $out_dir
      echo $out_dir
      numvol=160
      for file in $(find $out_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)

        echo "segmentation"
        sct_deepseg_sc -i ${fname}_moco_m.nii.gz -c t2s

        echo "Done with moco segmentation, continuing"
        sct_create_mask -i ${fname}_moco_m.nii.gz -p centerline,${fname}_moco_m_seg.nii.gz #size: 41 pixels

        # Prepend mean image to time-series
        fslmerge -t ${fname}_tmpInput.nii.gz ${fname}_moco_m.nii.gz $file

        # Do actual motion correction
        sct_fmri_moco -i ${fname}_tmpInput.nii.gz \
                      -m mask_${fname}_m.nii.gz \
                      -g 1 \
                      -param iterAvg=0,sampling=None \
                      -x spline

        # Clean up moco files (also remove mean from time-series, would need to be done for parameter files as well)
        mv ${fname}_tmpInput_moco.nii.gz ${fname}_moco_refined.nii.gz
        rm -f *tmpInput*

        fslroi ${fname}_moco_refined.nii.gz ${fname}_moco_refined.nii.gz 1 $numvol #always see what this would add up to, when 140 then its
        mv moco_params.tsv ${fname}_moco_refined_params.tsv
        mv moco_params_x.nii.gz ${fname}_moco_refined_params_x.nii.gz
        mv moco_params_y.nii.gz ${fname}_moco_refined_params_y.nii.gz

        fslroi ${fname}_moco_refined_params_x.nii.gz ${fname}_moco_refined_params_x.nii.gz 1 $numvol
        fslroi ${fname}_moco_refined_params_y.nii.gz ${fname}_moco_refined_params_y.nii.gz 1 $numvol

        # Calculate TSNR for moco_refined
        fslmaths ${fname}_moco_refined.nii.gz -Tmean ${fname}_moco_refined_m.nii.gz
        fslmaths ${fname}_moco_refined.nii.gz -Tstd ${fname}_moco_refined_sd.nii.gz
        fslmaths ${fname}_moco_refined_m.nii.gz -div ${fname}_moco_refined_sd.nii.gz ${fname}_moco_refined_t.nii.gz -odt float
      done
    fi

    #5. create csf masks for pnm
    if [ $csf_mask = 1 ]; then
      cd $out_dir
      for file in $(find $out_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        echo "building csf mask"
        sct_deepseg_sc -i ${fname}_moco_refined_m.nii.gz -c t2s
        #now build dilated mask for csf
        sct_maths -i ${fname}_moco_refined_m_seg.nii.gz -dilate 4 -o ${fname}_moco_refined_dilated_mask.nii.gz
      done
    fi

  done
done
