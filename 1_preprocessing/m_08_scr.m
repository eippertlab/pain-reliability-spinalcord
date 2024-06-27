% wrapper for epoching skin conductance data
% uses eeglab
% https://sccn.ucsd.edu/eeglab/index.php
% version used here: eglab2019_0
close all 
clear all
addpath '/data/pt_02306/main/code/github/pain-reliability-spinalcord/1_preprocessing/'
addpath '/data/pt_02306/main/code/github/pain-reliability-spinalcord/helper_functions/'
addpath(genpath('/data/pt_02098/Toolbox/eeglab2019_0/'))
eeglab
close

%% 
for isub=1:40
    sub=['sub-',num2str(isub,'%02.f')];
    for session=1:2
        ses=['ses-',num2str(session,'%02.f')];
        cfg = [];
        cfg.sub=sub
        cfg.eventdir = ['/data/pt_02306/main/data/pain-reliability-spinalcord/', sub, '/', ses, '/func/'];
        cfg.data    = ['/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/', sub, '/', ses, '/physio/'];
        cfg.out     = 'scr';
        cfg.ses = ses;
        epoch_scr = 1;          % epoch data into trials and create one datafile for all
        %% get filenames
        dir_list = dir(fullfile(cfg.data, '*ReliabilityRun*scr.tsv'));
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
        task_runs = sort(all_files)
        cfg.runs = task_runs;
        if ~exist(fullfile(cfg.data, cfg.out),'dir')
            mkdir(fullfile(cfg.data, cfg.out));
        end
        %for isub=1%:num_subjects
        cfg.sub = sub;

        if epoch_scr
            skin_conductance_epoch(cfg);
        end
        close all
    end
end


