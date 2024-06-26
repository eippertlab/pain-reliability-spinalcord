% wrapper for epoching pupil data
% for predcod behav first replication dataset
% uses PSPM toolbox
% https://github.com/bachlab/PsPM
% version used here: PsPM_v6.0.0
% Ulrike Horn
% uhorn@cbs.mpg.de
% adapted by Alice Dabbagh (dabbagh@cbs.mpg.de)
% 27th November 2020
close all
clear
addpath '/data/pt_02306/main/code/github/pain-reliability-spinalcord/1_preprocessing/'
addpath '/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/'

%% Directories and files %%
for subject=1:40
    sub =  ['sub-',num2str(subject,'%02.f')];
    for session=1:2
        ses =  ['ses-',num2str(session,'%02.f')];
        data_dir = ['/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/', sub, '/', ses, '/physio/']
        cfg = [];
        cfg.data = data_dir;
        cfg.out = 'pupil';
        cfg.ses = ses;
        cfg.sub=sub;
        cfg.pspm_path = '/data/u_dabbagh_software/PsPM_v6.1/';
        epoch_pupil = 1;            % epoch data into trials and create one datafile for all
        %% prepare the files %%
        cd(cfg.data)

        %get filenames
         if subject==16 & session==1
             continue
         end
         if subject==22 & session==2
             continue
         end
         dir_list = dir(fullfile(cfg.data, '*ReliabilityRun*_eyetrack.tsv'));
         all_files = {dir_list.name};
         for i=1:length(all_files)
              dotLocations = find(all_files{i} == '.');
            if isempty(dotLocations);
                % No dots at all found so just take entire name.
                all_files = all_files{i};
            else
                % Take up to , but not including, the first dot.
                all_files{i} = all_files{i}(1:dotLocations(1)-1);
            end
         end
        task_runs = sort(all_files);
        cfg.runs = task_runs
        if ~exist(fullfile(cfg.data, cfg.out),'dir')
            mkdir(fullfile(cfg.data, cfg.out));
        end
        % cut data into trial wise epochs
        pupil_dilation_epoch(cfg);
        close all
    end
end


