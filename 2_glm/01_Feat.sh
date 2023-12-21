#!/bin/bash
# 01_Feat.sh

#what shall be done
create_fsf=1
run_feat=1

#choose a model!
model=denoised_single
model_out=denoised_single_2step_v2
#Directories
original_fsf=/data/pt_02306/main/data/derivatives/glm/design/denoised_single/design.fsf

for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses
    echo "run: $run"

    #Directories
    data_dir=/data/pt_02306/main/data/derivatives/preprocessing/sub-${sub}/ses-${ses}/func/therm_denoise_te-40_2step
    design_dir=/data/pt_02306/main/data/derivatives/glm/design/$model
    out_dir=/data/pt_02306/main/data/derivatives/glm/sub-${sub}/ses-${ses}/$model_out
    mkdir -p $design_dir
    mkdir -p $out_dir

    if [ $create_fsf = 1 ]; then
      cd  $data_dir
      for file in $(find $data_dir/ -maxdepth 1 -name  "sub*te-40_bold_denoised_moco_refined.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        #prepare info
        #number of volumes
        numvol=160
        tr=1.8
        #block for timing file
        if [[ $fname = *"run-01"* ]]; then
          block=block_1
        elif [[ $fname = *"run-02"* ]]; then
          block=block_2
        elif [[ $fname = *"run-03"* ]]; then
          block=block_3
        elif [[ $fname = *"run-04"* ]]; then
          block=block_4
        elif [[ $fname = *"run-05"* ]]; then
          block=block_5
        fi
        echo $block

        #create fsf
        original_fsf=/data/pt_02306/main/data/derivatives/glm/design/denoised_single/design.fsf
        sed "s+sub-01/ses-01/denoised_te-40+sub-$sub/ses-$ses/${model_out}/${fname}+g" $original_fsf > $out_dir/${fname}.fsf
        sed -i "s+sub-01/ses-01/func/therm_denoise_te-40/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined+sub-$sub/ses-$ses/func/therm_denoise_te-40_2step/${fname}+g" $out_dir/${fname}.fsf
        sed -i "s+sub-01/ses-01/events/block_1.txt+sub-$sub/ses-$ses/events/$block.txt+g" $out_dir/${fname}.fsf
        sed -i -e "s+1.8+$tr+g" $out_dir/${fname}.fsf
        sed -i -e "s+160+$numvol+g" $out_dir/${fname}.fsf
        sed -i "s+sub-01/ses-01/func/therm_denoise_te-40/pnm/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined/pnm_evlist_design.txt+sub-$sub/ses-$ses/func/therm_denoise_te-40_2step/pnm/${fname}/pnm_evlist.txt+g" $out_dir/${fname}.fsf
        #outlier file
        sed -i "s+sub-01/ses-01/func/therm_denoise_te-40/outliers/feat_input/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined_outlier.txt+sub-$sub/ses-$ses/func/therm_denoise_te-40_2step/outliers/feat_input/${fname}_outlier.txt+g" $out_dir/${fname}.fsf
        #evlist
        ev_file=/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/func/therm_denoise_te-40/pnm/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined/pnm_evlist_design.txt
        sed "s+sub-01/ses-01/func/therm_denoise_te-40/pnm/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco+sub-$sub/ses-$ses/func/therm_denoise_te-40_2step/pnm/${fname}+g" $ev_file > $data_dir/pnm/${fname}/pnm_evlist.txt
        sed -i "s+sub-01/ses-01/func/therm_denoise_te-40/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined_params_+sub-$sub/ses-$ses/func/therm_denoise_te-40_2step/${fname}_params_+g" $data_dir/pnm/${fname}/pnm_evlist.txt
      done
    fi

    if [ $run_feat = 1 ]
      then
        feat $out_dir/${fname}.fsf
    fi

  done
done
