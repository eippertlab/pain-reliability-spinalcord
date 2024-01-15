#!/bin/bash
# 01_Feat.sh

#what shall be done
create_fsf=1
run_feat=1
normalize_feat=1

#Directories
original_fsf=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/design.fsf

for subject in {5..8}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses
    echo "run: $run"

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    base_dir=$project_dir/sub-${sub}/ses-${ses}/func/
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    out_dir_fsf=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm
    mkdir -p $out_dir_fsf
    out_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/ReliabilityRun
    #normalization Directories
    template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template #replace with your own sct folder

    cd  $data_dir
    for file in $(find $data_dir/ -maxdepth 1 -name  "*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
      fname=$(basename "$file" | cut -d. -f1)

      if [ $create_fsf = 1 ]; then
        echo "preparing fsf file"
        #prepare timing file
        for event_file in $(find $base_dir/ -maxdepth 1  -name "*te40ReliabilityRun*events.tsv"); do
          event_name=$(basename "$event_file" | cut -d. -f1)
          glmevent_name=$data_dir/${fname}_events
          echo $glmevent_name
          awk 'NR>1 {print $1 "\t1\t1"}' "$event_file" > "${glmevent_name}.txt"
        done

        #create fsf
        original_fsf=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/design.fsf
        #define out dir
        sed "s+/data/pt_02306/main/data/derivatives/glm/sub-01/ses-01/denoised_te-40+$out_dir+g" $original_fsf > $out_dir_fsf/${fname}.fsf
        #define input time series
        sed -i "s+/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/func/therm_denoise_te-40/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined+$data_dir/${fname}+g" $out_dir_fsf/${fname}.fsf
        #define time input
        sed -i "s+/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/events/block_1.txt+${glmevent_name}.txt+g" $out_dir_fsf/${fname}.fsf
        sed -i "s+/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/func/therm_denoise_te-40/pnm/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined/pnm_evlist_design.txt+${data_dir}/pnm/${fname}/pnm_evlist.txt+g" $out_dir_fsf/${fname}.fsf
        #outlier file
        sed -i "s+/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/func/therm_denoise_te-40/outliers/feat_input/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined_outlier.txt+${data_dir}/outliers/feat_input/${fname}_outlier.txt+g" $out_dir_fsf/${fname}.fsf
        #evlist
        ev_file=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/pnm_evlist.txt
        sed "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/pnm/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined+${data_dir}/pnm/${fname}+g" $ev_file > $data_dir/pnm/${fname}/pnm_evlist.txt
        sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined_params+${data_dir}/${fname}_params+g" $data_dir/pnm/${fname}/pnm_evlist.txt
      fi

      if [ $run_feat = 1 ]; then
        echo "running Feat"
        feat $out_dir_fsf/${fname}.fsf
      fi

      if [ $normalize_feat = 1 ]; then
        echo "normalizing feat stats"
        glm_dir=${out_dir}.feat/stats
        warp_dir=${data_dir}/normalization
        out_dir_normalization=${glm_dir}/normalization
        mkdir -p $out_dir_normalization

        #normalize copes
        echo "normalizing cope image"
        sct_apply_transfo -i $glm_dir/cope1.nii.gz \
                          -d $template_dir/PAM50_t2.nii.gz \
                          -w $warp_dir/warp_${fname}_m2PAM50_t2s.nii.gz \
                          -o $out_dir_normalization/cope1_reg.nii.gz \
                          -x spline

        #normalize copes
        echo "normalizing cope image"
        sct_apply_transfo -i $glm_dir/zstat1.nii.gz \
                          -d $template_dir/PAM50_t2.nii.gz \
                          -w $warp_dir/warp_${fname}_m2PAM50_t2s.nii.gz \
                          -o $out_dir_normalization/zstat1_reg.nii.gz \
                          -x spline

      fi
    done
  done
done
