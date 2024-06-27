# -*- coding: utf-8 -*-
"""
Python version: 3.10.9
nibabel version: 4.0.2
numpy version: 1.23.3
pandas version: 1.5.0
"""

#%% Import Modules
import nibabel as nib
import numpy as np
import pandas as pd
import glob 

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord/'

#%% Write DHR regressor
for subject in range(1,41):
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        print('session: ',ses)
        data_dir = f'{project_dir}/derivatives/{sub}/{ses}/func/preprocessing/'
        out_dir = f'{data_dir}/DHR/'
        ref = glob.glob(f'{data_dir}/sub*te40ReliabilityRun*bold_denoised_moco_refined.nii.gz')[0]
        name = ref.split('/')[-1].split(".")[0]
        imgref = nib.load(ref)
        numvol = 160
        #load regressors
        txtfile = glob.glob(f'{out_dir}*refined_dhr.txt')[0]
        tmp = pd.read_csv(txtfile, header=None, delim_whitespace=True).transpose()
        tmp = tmp.rename(columns={0:"x", 1:"y", 2:"z"})
        timeseries = tmp.groupby(["z"]).mean().drop(["x","y"], axis=1).transpose()
      
        data = np.ones((128, 128, 16, numvol), dtype=np.float32) # dummy data in numpy matrix
        for sl in range(16):
            for tr in range(numvol):
                data[:,:,sl,tr] = data[:,:,sl,tr]* timeseries.iloc[tr,sl]
        img = nib.Nifti1Image(data, imgref.affine, imgref.header) 
        img.to_filename(f'{out_dir}{name}_dhr.nii.gz') # Save as NiBabel file

