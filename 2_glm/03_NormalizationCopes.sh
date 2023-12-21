#!/bin/bash
# 02_NormalizationCopes.sh

#Use this script to normalize the statistical output images

# What shall be done
normalize=1

# Loop across sessions for data preparation
model=denoised_single_2step_v2
for subject in {1..40} ; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    #setting and directories
    data_dir=/data/pt_02306/main/data/derivatives/glm/sub-${sub}/ses-${ses}/${model}
    func_dir=/data/pt_02306/main/data/derivatives/preprocessing/sub-${sub}/ses-${ses}/func/therm_denoise_te-40_2step_seifert

    if [ $normalize = 1 ]; then
      echo "$model"
      data_dir=/data/pt_02306/main/data/derivatives/glm/sub-${sub}/ses-${ses}/${model}
      echo "subject: " $sub "session: " $ses
      cd $data_dir
      for i in $(ls -d sub*te-40_*refined_crop_smooth.feat/); do
        echo $i
        fname=$(basename "$i" | cut -d. -f1)
        echo $fname
        run_dir=$data_dir/${i}stats
        echo $run_dir
        template_dir=/data/u_dabbagh_software/sct_5.8/data/PAM50/template
        warp_dir=$func_dir/normalization
        out_dir=$run_dir/normalization
        mkdir -p $out_dir

        #register all the relevant things to template space
        echo "cope images exists for subject $sub session $ses"
        mkdir -p $out_dir
        cd $run_dir

        #normalize copes
        echo "normalizing cope image, spline"
        for cope in cope1 tstat1 zstat1; do
          sct_apply_transfo -i $run_dir/${cope}.nii.gz \
                            -d $template_dir/PAM50_t2.nii.gz \
                            -w $warp_dir/warp_${fname}_m2PAM50_t2s.nii.gz \
                            -o $out_dir/${cope}_normalized_spline.nii.gz \
                            -x spline
        done
       done
     fi

  done
done
