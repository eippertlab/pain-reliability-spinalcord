#!/bin/sh
# 06_b_pnm_thermnoise.sh

# What shall be done
prepInput=1
runpnm=1

# Loop across sessions for data preparation
for subject in {1..40}; do
  for session in {1..2}; do
    printf -v sub "%02d" $subject
    printf -v ses "%02d" $session
    echo "subject: " $sub "session: " $ses

    #Directories
    project_dir=/data/pt_02306/main/data/pain-reliability-spinalcord
    data_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/func/preprocessing
		physio_dir=$project_dir/derivatives/sub-${sub}/ses-${ses}/physio
    out_dir=$data_dir/pnm
    mkdir -p $out_dir
		cd $input_dir

    for physio_file in $(find $physio_dir/ -maxdepth 1  -name "*te40ReliabilityRun**physio.tsv"); do
      physio_name=$(basename "$physio_file" | cut -d. -f1)
      pnm_name=$physio_dir/${physio_name}_pnminput
      echo $pnm_name
      #1. Prep physio files
      if [ $prepInput = 1 ]; then
        sed '1d;s/\t/ /g' "$physio_file" > "${pnm_name}.txt"
      fi

      #2. run pnm
      if [ $runpnm = 1 ]; then
    		cd $data_dir
    		for file in $(find $data_dir/ -maxdepth 1 -name "*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz"); do
    			fname=$(basename "$file" | cut -d. -f1)
    		done
        trs=(1.800)

    		run_dir=$out_dir/$fname
    		mkdir -p $run_dir
    		pnm_file=$run_dir/pnm
    		epi_file=$data_dir/${fname}.nii.gz
    		cd $run_dir
    		echo "Running Pnm Extraction"
    		echo "file: ${fname}.nii.gz, tr: ${trs}, physiofile = ${pnm_name}.txt"
    		#define files
    		#/usr/share/fsl/5.0/bin/
    		fslFixText \
    			 ${pnm_name}.txt \
    			 ${pnm_file}_input.txt

    			#stage 1
    		 #/usr/share/fsl/5.0/bin/
    		 pnm_stage1 \
    				-i ${pnm_file}_input.txt \
    				-o ${pnm_file} \
    				-s 1000 --tr=$trs --smoothcard=0.1 --smoothresp=0.1 --resp=2 --cardiac=3 --trigger=4 --pulseox_trigger

    		 #popp
    		 #/usr/share/fsl/5.0/bin/
    			popp \
    			 -i ${pnm_file}_input.txt \
    			 -o ${pnm_file} \
    					 -s 1000 --tr=${trs} --smoothcard=0.1 --smoothresp=0.1 --resp=2 --cardiac=3 --trigger=4 --pulseox_trigger

    				obase=${pnm_file}

    				#/usr/share/fsl/5.0/bin/
    			pnm_evs \
    					-i $epi_file \
    					-c ${pnm_file}_card.txt \
    					-r ${pnm_file}_resp.txt \
    					-o ${pnm_file}_ --tr=${trs} --oc=4 --or=4 --multc=2 --multr=2 --sliceorder=down --slicedir=z --csfmask=$data_dir/${fname}_dilated_mask.nii.gz --sliceorder=down --slicedir=z

    			ls -1 `imglob -extensions ${obase}ev*` > ${pnm_file}_evlist.txt
        fi
    done
  done
done
