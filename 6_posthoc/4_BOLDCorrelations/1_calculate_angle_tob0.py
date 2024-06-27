#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandas version: 1.5.0
numpy version: 1.23.3
"""

#%% Import Modules
import pandas as pd
import numpy as np
import glob
import json
from pathlib import Path

#%% Functions
def calculate_deviation_angle(row):
    # Extract row and column direction cosines
    x_direction  = np.array(row["orientation"][:3])
    y_direction  = np.array(row["orientation"][3:])
    
    # Calculate the normal vector to the image plane
    z_direction  = np.cross(x_direction, y_direction)
       
    # B0 field direction (assuming perfectly aligned with the z-axis)
    b0_direction = np.array([0, 0, 1])
    
    # Calculate the cosine of the angle between the normal vector and the B0 direction
    cos_angle = np.dot(z_direction, b0_direction)
    
    # Ensure the cosine value is within the valid range [-1, 1] to avoid numerical issues
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    # Calculate the angle in degrees
    angle = np.arccos(cos_angle) * (180.0 / np.pi)
    if angle > 90:
        angle = 180 - angle
    
    return angle

#%% Directories
project_dir = '/data/pt_02306/main/data/pain-reliability-spinalcord'
out_dir = f'{project_dir}/derivatives/results/Posthoc/Correlations'
Path(out_dir).mkdir(parents=True, exist_ok=True)

#%% Load data
data_all= []
for subject in range(1, 41): 
    sub = 'sub-' + str(subject).zfill(2)
    print('subject: ',sub)
    for session in range (1,3):
        ses = 'ses-' + str(session).zfill(2)
        data_dir = f'{project_dir}/{sub}/{ses}/func/'
        files = glob.glob(data_dir + "*te40ReliabilityRun*bold.json")
        file_path = files[0]
        with open(file_path, 'r') as file:
            data = json.load(file)
        te = data.get("EchoTime")
        if te != 0.04:
            print(f'Warning: EchoTime is not 0.04 for {sub}, {ses}')
        orientation = data.get("ImageOrientationPatientDICOM")
        orientation_np = np.array(orientation)
        tmp = pd.DataFrame({'sub': [sub],  
                            'ses': [ses], 
                            'te': [te],
                            'orientation': [orientation_np]})
        data_all.append(tmp)      
angle_to_b0 = pd.concat(data_all, ignore_index=True) 

#%% Save 
angle_to_b0["angle"] = angle_to_b0.apply(calculate_deviation_angle, axis=1)
savename = f'{out_dir}dicom_zplane.csv'
angle_to_b0.to_csv(savename, index=False)
