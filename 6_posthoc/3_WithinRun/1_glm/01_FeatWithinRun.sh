#!/bin/bash
# 01_FeatWithinRun.sh

#what shall be done
create_fsf=0
run_feat=0
normalize_feat=1

#Directories
original_fsf=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/design.fsf

for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    base_dir=$project_dir/sub-${sub}/ses-${ses}/func/
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
    out_dir_fsf=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/glm/WithinRun
    mkdir -p $out_dir_fsf
    #normalization Directories
    template_dir=/data/u_dabbagh_software/sct_5.5/data/PAM50/template #replace with your own sct folder

    cd  $data_dir
    for file in $(find $data_dir/ -maxdepth 1 -name  "*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
      fname=$(basename "$file" | cut -d. -f1)

      if [ $create_fsf = 1 ]; then
        echo "preparing fsf file"
        #prepare timing file
        for event_file in $(find $base_dir/ -maxdepth 1 -name "*te40ReliabilityRun*events.tsv"); do
          event_name=$(basename "$event_file" | cut -d. -f1)
          glmevent_name=$data_dir/${fname}_events

          #make odd-even timing files
          glmevent_name_odd=$data_dir/${fname}_events_odd
          glmevent_name_even=$data_dir/${fname}_events_even
          awk 'NR>1 {if ($5 % 2 == 0) print $1 "\t1\t1" > "'${glmevent_name_even}.txt'"; else print $1 "\t1\t1" > "'${glmevent_name_odd}.txt'"}' "$event_file"

          #then early-late
          glmevent_name_first=$data_dir/${fname}_events_early
          glmevent_name_second=$data_dir/${fname}_events_late
          awk 'NR>1 {if (NR<=11) print $1 "\t1\t1" > "'${glmevent_name_first}.txt'"; else print $1 "\t1\t1" > "'${glmevent_name_second}.txt'"}' "$event_file"
        done

        #create fsf
        for within_type in odd_even early_late; do
          if [ "$within_type" == "odd_even" ]; then
            event_type_array=("odd" "even")
          elif [ "$within_type" == "early_late" ]; then
            event_type_array=("early" "late")
          fi
          out_dir=$out_dir_fsf/$within_type
          original_fsf=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/design_withinRun.fsf

          #define out dir
          sed "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/glm/WithinRun/early_late+$out_dir+g" $original_fsf > $out_dir_fsf/${fname}_$within_type.fsf
          #define input time series
          sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined+$data_dir/${fname}+g" $out_dir_fsf/${fname}_${within_type}.fsf
          #define time input
          # Update the FSF file for custom1
          sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined_events_early.txt+${glmevent_name}_${event_type_array[0]}.txt+g" $out_dir_fsf/${fname}_${within_type}.fsf
          sed -i "s+Heat_early+Heat_${event_type_array[0]}+g" $out_dir_fsf/${fname}_${within_type}.fsf
          # Update the FSF file for custom2
          sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined_events_late.txt+${glmevent_name}_${event_type_array[1]}.txt+g" $out_dir_fsf/${fname}_${within_type}.fsf
          sed -i "s+Heat_late+Heat_${event_type_array[1]}+g" $out_dir_fsf/${fname}_${within_type}.fsf
          #pnm evlist
          sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/pnm/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined/pnm_evlist.txt+${data_dir}/pnm/${fname}/pnm_evlist.txt+g" $out_dir_fsf/${fname}_${within_type}.fsf
      #    #outlier file
          sed -i "s+/data/pt_02306/main/data/derivatives/preprocessing/sub-01/ses-01/func/therm_denoise_te-40_2step/outliers/feat_input/sub-01_ses-01_run-01_task-heat-patch-04_acq-te-40_bold_denoised_moco_refined_outlier.txt+${data_dir}/outliers/feat_input/${fname}_outlier.txt+g" $out_dir_fsf/${fname}_${within_type}.fsf
          #evlist
          ev_file=/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/pnm_evlist.txt
          sed "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/pnm/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined+${data_dir}/pnm/${fname}+g" $ev_file > $data_dir/pnm/${fname}/pnm_evlist.txt
          sed -i "s+/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/sub-01/ses-01/func/preprocessing/sub-01_ses-01_task-heat_acq-te40ReliabilityRun_run-01_bold_denoised_moco_refined_params+${data_dir}/${fname}_params+g" $data_dir/pnm/${fname}/pnm_evlist.txt
        done
      fi

      if [ $run_feat = 1 ]; then
        for within_type in odd_even early_late; do
          echo "running Feat"
          feat $out_dir_fsf/${fname}_${within_type}.fsf
        done
      fi

      if [ $normalize_feat = 1 ]; then
        for within_type in odd_even early_late; do
          out_dir=$out_dir_fsf/$within_type
          echo "normalizing feat stats"
          glm_dir=${out_dir}.feat/stats
          warp_dir=${data_dir}/normalization
          out_dir_normalization=${glm_dir}/normalization
          mkdir -p $out_dir_normalization

          for stat in {1..2}; do
            #normalize copes
            echo "normalizing cope image"
            sct_apply_transfo -i $glm_dir/cope${stat}.nii.gz \
                              -d $template_dir/PAM50_t2.nii.gz \
                              -w $warp_dir/warp_${fname}_m2PAM50_t2s.nii.gz \
                              -o $out_dir_normalization/cope${stat}_reg.nii.gz \
                              -x spline

            #normalize copes
            echo "normalizing zstat image"
            sct_apply_transfo -i $glm_dir/zstat${stat}.nii.gz \
                              -d $template_dir/PAM50_t2.nii.gz \
                              -w $warp_dir/warp_${fname}_m2PAM50_t2s.nii.gz \
                              -o $out_dir_normalization/zstat${stat}_reg.nii.gz \
                              -x spline
          done
        done
      fi
    done
  done
done
