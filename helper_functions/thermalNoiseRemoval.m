function thermalNoiseRemoval(filein, name, ofolder)

% Make sure that the following has been done:
% - you have downloaded the most current nonlocal mppca repo from github
% (https://github.com/NYU-DiffusionMRI/mppca_denoise)
% - you have FSL installed and know where its Matlab functions are located
% - you have set up a sensible parallel pool in your Matlab preferences
%
% This function should only be used on the RAW imaging data (i.e. after
% Dicom-to-Nifti conversion, but before any further processing) of each
% SINGLE session/run/block (or whatever you call one data acquisition).
%
% As this was coded up quickly, please call this function from the
% directory where the raw data are located and only supply the filename of
% the 4D Nifti file.
%
% For now, the only output of interest is the file 'denoised.nii.gz', which
% you can then use instead of the raw data for all further processing steps
% that you would normally carry out. The other output is not important
% right now, as it only provides some sanity checks. 
%
% You can also check the tSNR improvement after thermal noise removal by
% looking at the provided tSNR maps of the raw and denoised data.


% Set up relevant environment & path
addpath('/data/u_dabbagh_software/mppca_denoise') %add your own directory here following the instructions above
addpath('/afs/cbs.mpg.de/software/fsl/6.0.3/ubuntu-bionic-amd64/etc/matlab'); %add your own matlab directory 
setenv('FSLOUTPUTTYPE', 'NIFTI_GZ')


% Set up file naming
dataInput   = filein;
dataOutput  = [ofolder name '_denoised.nii.gz'];
dataNoise   = [ofolder name '_noise.nii.gz'];
dataNoiseA  = [ofolder name '_noiseAfter.nii.gz'];
dataNumComp = [ofolder name '_numSignalComp.nii.gz'];
dataResid   = [ofolder name '_residuals.nii.gz'];


% Run denoising
data = read_avw(dataInput);

if size(data,4) > 342
    [denoised, sigma, npars, sigmaAfter] = MPnonlocal(data, 'kernel', 7, 'patchtype', 'box', 'exp', 3);
else
    [denoised, sigma, npars, sigmaAfter] = MPnonlocal(data, 'patchtype', 'nonlocal', 'exp', 3);
end

save_avw(denoised, dataOutput, 'd', [1 1 1 3]);
unix(['fslcpgeom ' dataInput ' ' dataOutput]);
unix(['fslmaths ' dataOutput ' ' dataOutput ' -odt int']);

save_avw(sigma, dataNoise, 'd', [1 1 1 3]);
unix(['fslcpgeom ' dataInput ' ' dataNoise]);
unix(['fslroi ' dataNoise ' ' dataNoise ' 0 1']);

save_avw(npars, dataNumComp, 'd', [1 1 1 3]);
unix(['fslcpgeom ' dataInput ' ' dataNumComp]);
unix(['fslroi ' dataNumComp ' ' dataNumComp ' 0 1']);

save_avw(sigmaAfter, dataNoiseA, 'd', [1 1 1 3]);
unix(['fslcpgeom ' dataInput ' ' dataNoiseA]);
unix(['fslroi ' dataNoiseA ' ' dataNoiseA ' 0 1']);


% Calculate relevant statistics
unix(['fslmaths ' dataInput ' -sub ' dataOutput ' ' dataResid]);
unix(['fslmaths ' dataResid ' -abs -Tmean $(remove_ext ' dataResid ')_meanAbs.nii.gz']);
calculateTSNR(dataInput);
calculateTSNR(dataOutput);


% Helper function for tSNR calculation
function calculateTSNR(inData)
unix(['fslmaths ' inData ' -Tmean $(remove_ext ' inData ')_m.nii.gz']);
unix(['fslmaths ' inData ' -Tstd $(remove_ext ' inData ')_sd.nii.gz']);
unix(['fslmaths $(remove_ext ' inData ')_m.nii.gz -div $(remove_ext ' inData ')_sd.nii.gz $(remove_ext ' inData ')_tsnr.nii.gz']);
end
end
