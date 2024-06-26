#!/bin/bash
# 05_T2w.sh

#This script requires the usage of ANTs N4BiasFieldCorrection.
#We used ANTs version 2.3.1

# What shall be done?
cropAuto=1
biascorrect=1
denoise=1
segment=1
label=1
qc_check=1

#settings
cropA_minX=0
cropA_sizeX=-1
cropA_minY=0
cropA_sizeY=-1
cropA_minZ=0

#loop over subjects
for subject in {1..4}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/sub-${sub}/ses-${ses}/anat
    out_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/anat/preprocessing
    mkdir -p $out_dir
    qc_dir=$out_dir/qc
    mkdir -p $qc_dir
    cp -f $data_dir/*T2w.nii.gz $out_dir/

    #1. automatic cropping (based on pmj detection)
    if [ $cropAuto -eq 1 ]; then
      echo "cropping sub" $sub "session" $ses
      cd $out_dir
      for file in $(find . -name "*T2w.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
        sct_detect_pmj -i ${fname}.nii.gz \
                       -c t2 \
                       -o ${fname}_pmj.nii.gz \
                       -ofolder $out_dir

        if [[ $subject = 4 && $session = 2 ]]; then
          echo "sub-04 ses 02! --> manual pmj"
          pmj_coordZ=247

        elif [[ $subject = 16 && $session = 2 ]]; then
          echo "sub-16 ses 02! --> manual pmj"
          pmj_coordZ=259

        elif [[ $subject = 16 && $session = 1 ]]; then
          echo "sub-16 ses 01! --> manual pmj"
          pmj_coordZ=256

        elif [[ $subject = 18 && $session = 1 ]]; then
          echo "sub-16 ses 01! --> manual pmj"
          pmj_coordZ=255

        elif [[ $subject = 18 && $session = 2 ]]; then
          echo "sub-16 ses 01! --> manual pmj"
          pmj_coordZ=256

        elif [[ $subject = 20 && $session = 1 ]]; then
          echo "sub-20 ses 01! --> manual pmj"
          pmj_coordZ=236

        elif [[ $subject = 22 && $session = 1 ]]; then
          echo "sub-22 ses 01! --> manual pmj"
          pmj_coordZ=249

        elif [[ $subject = 22 && $session = 2 ]]; then
          echo "sub-22 ses 02! --> manual pmj"
          pmj_coordZ=249

        elif [[ $subject = 35 && $session = 1 ]]; then
          echo "sub-35 ses 01! --> manual pmj"
          pmj_coordZ=264

        else
          echo "using automated pmj detection"
          pmj_coordZ=$(fslstats ${fname}_pmj.nii.gz -x | awk -F ' ' '{print $3}')
        fi
        #echo the coordinates to check if they are normal and then cut
        echo "pmj coordinate:" $pmj_coordZ
        fslroi ${fname}.nii.gz ${fname}_crop.nii.gz $cropA_minX $cropA_sizeX $cropA_minY $cropA_sizeY $cropA_minZ $pmj_coordZ # the image orientation is AIL, this why we have y, then z, then x
      done
    fi

    #2. bias-correction
    if [ $biascorrect -eq 1 ]; then
      echo "bias correction sub" $sub "session" $ses
      cd $out_dir
      for file in $(find $out_dir/ -maxdepth 1 -name "*T2w.nii.gz"); do
        echo $file
        fname=$(basename "$file" | cut -d. -f1)
        /afs/cbs.mpg.de/software/ants/2.3.1/ubuntu-bionic-amd64/antsbin/bin/N4BiasFieldCorrection \
          -i ${fname}_crop.nii.gz \
          -o ${fname}_crop_biascorr.nii.gz \
          -c [200x200x200x200,0.000001]
          sleep 10
          echo "finished bias correction"
      done
    fi

    #3. denoising (via matlab)
    if [ $denoise -eq 1 ]; then
  echo "denoising sub" $sub "session" $ses
  github_folder=/data/pt_02306/main/code/github/pain-reliability-spinalcord
  helper_functions=$github_folder/helper_functions
  package_dir=/data/u_dabbagh_software/MRIDenoisingPackage_r01_pcode/ #change this to your own path to the package!
  cd $out_dir
  echo $out_dir
  for file in $(find $out_dir/ -maxdepth 1 -name "*T2w.nii.gz"); do
    fname=$(basename "$file" | cut -d. -f1)
    gunzip $out_dir/${fname}_crop_biascorr.nii.gz
    sleep 3  # unzip file because toolbox can't deal with .gz files
    filename=${fname}_crop_biascorr.nii
    out_name=${fname}_crop_biascorr_denoise.nii
    # Run MATLAB function with verbose output
    matlab -nosplash -nodesktop -r "addpath(genpath('${helper_functions}')); try; Denoising_T1('${package_dir}', 1, 2, 1, 1, 3, '_denoise', 0, '${filename}', '${out_dir}'); catch ME; disp(getReport(ME)); end; quit;"

    # Wait for output file to be created
    while [ ! -f "${out_dir}/${out_name}" ]; do
      sleep 1
    done

    gzip -f $out_dir/${filename}  # zip input file
    gzip -f $out_dir/$out_name    # zip resulting file
    sleep 5  # wait before executing next call to Matlab; prevents Matlab from randomly crashing on startup
  done
fi


    #4. segmentation
    if [ $segment -eq 1 ]; then
      echo "segmenting sub" $sub "session" $ses
      cd $out_dir
      if [ -d "$qc_dir/raw" ] && [ "$(ls -A "$qc_dir/raw")" ]; then
          echo "Removing all contents of $qc_dir/raw"
          rm -rf "$qc_dir/raw"/*
      fi

      if [ -d "$qc_dir/smooth" ] && [ "$(ls -A "$qc_dir/smooth")" ]; then
          echo "Removing all contents of $qc_dir/smooth"
          rm -rf "$qc_dir/smooth"/*
      fi

      for file in $(find $out_dir/ -maxdepth 1 -name "*T2w.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
          #1) initial segmentation
          sct_deepseg_sc -i $out_dir/${fname}_crop_biascorr_denoise.nii.gz \
                         -c t2 \
                         -o $out_dir/${fname}_seg_raw.nii.gz \
                         -qc $qc_dir -qc-dataset raw

          #2) smooth along spinal cord
          sct_smooth_spinalcord -i $out_dir/${fname}_crop_biascorr_denoise.nii.gz \
                                -s $out_dir/${fname}_seg_raw.nii.gz \
                                -smooth 0,0,6 \
                                -v 1 \
                                -o $out_dir/${fname}_crop_biascorr_denoise_smooth.nii.gz

          rm -Rf warp_* \
                 straightening.cache
          #3. segment smoothed T2
          sct_deepseg_sc -i $out_dir/${fname}_crop_biascorr_denoise_smooth.nii.gz \
                         -c t2 \
                         -o $out_dir/${fname}_seg.nii.gz \
                         -qc $qc_dir -qc-dataset seg
      done
    fi

    if [ $label -eq 1 ]; then
      echo "labeling discs for sub" $sub "session" $ses
      cd $out_dir
      if [ -d "$qc_dir/label" ] && [ "$(ls -A "$qc_dir/label")" ]; then
        echo "Removing all contents of $qc_dir/label"
        rm -rf "$qc_dir/label"/*
      fi
      for file in $(find $out_dir/ -maxdepth 1 -name "*T2w.nii.gz"); do
        fname=$(basename "$file" | cut -d. -f1)
          #automatic labeling of discs and vertebrae
        if [[ $subject = 8 && $session = 2 ]] || [[ $subject = 9 && $session = 1 ]] || [[ $subject = 23 ]] || [[ $subject = 37 && $session = 1 ]] || [[ $subject = 38 ]]; then
          #here disc detection did not work, do manually: "Initialize vertebral
          #labeling by providing a nifti file that has a single disc label.
          #An example of such file is a single voxel with value '3',
          #which would be located at the posterior tip of C2-C3 disc.
          #Such label file can be created using: sct_label_utils -i IMAGE_REF -create-viewer 3
          sct_label_utils -i ${fname}_crop_biascorr_denoise.nii.gz \
                          -create-viewer 3

          sct_label_vertebrae -i ${fname}_crop_biascorr_denoise.nii.gz \
                                -s ${fname}_seg.nii.gz \
                                -c t2 \
                                -initlabel labels.nii.gz \
                                -qc $qc_dir -qc-dataset label
        else
          sct_label_vertebrae -i ${fname}_crop_biascorr_denoise.nii.gz \
                              -s ${fname}_seg.nii.gz \
                              -c t2 \
                              -qc $qc_dir \
                              -qc-dataset label
        fi

        mv ${fname}_seg_labeled_discs.nii.gz ${fname}_labeled_discs.nii.gz
        #keep only the discs you need
        sct_label_utils -i ${fname}_labeled_discs.nii.gz \
                        -keep 2,3,4,5,6,7,8,9 \
                        -o ${fname}_labeled_discs.nii.gz

      done
    fi

    if [ $qc_check = 1 ]; then
      #quality control
      xdg-open $qc_dir/index.html
    fi
  done
done
