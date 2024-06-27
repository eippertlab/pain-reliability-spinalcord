% uses PSPM toolbox
% https://github.com/bachlab/PsPM
% version used here: PsPM6.1

%% Prep code
addpath('/data/u_dabbagh_software/PsPM6.1', '-end');
write_data=1
prep_events=1
run_glm=1
run_sf=1
excluded_subjects = [16, 39]; % Define excluded subjects
my_sr = 100;

%% Loop over subject and sessions
for isub=1:40
    if any(isub == excluded_subjects)
        continue
    else
        sub=['sub-',num2str(isub,'%02.f')];
        for session=1:2
            ses=['ses-',num2str(session,'%02.f')];
            eventdir = ['/data/pt_02306/main/data/pain-reliability-spinalcord/', sub, '/', ses, '/func/'];
            data_dir    = ['/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/', sub, '/', ses, '/physio/'];     
            out_dir = [data_dir,'pspm/'];
            if ~exist(out_dir,'dir') mkdir(out_dir); end
            dir_list = dir(fullfile(data_dir, '*ReliabilityRun*scr.tsv'));
            all_files = {dir_list.name};
            for i=1:length(all_files)
                 dotLocations = find(all_files{i} == '.');
                 % Take up to , but not including, the first dot.
                 all_files{i} = all_files{i}(1:dotLocations(1)-1);
            end
            all_files = sort(all_files);
            if length(all_files)> 1
                disp("WARNING, check number of files!")
            end
            task_run = all_files{1};
            % Load the TSV file
            opts = detectImportOptions([data_dir, task_run, '.tsv'], 'FileType', 'text', 'Delimiter', '\t');
            tsvData = readtable([data_dir, task_run, '.tsv'], opts);
            % Save as a CSV file
            writetable(tsvData, [out_dir, task_run,'.csv']);
            %% 
            if write_data==1
                import = {struct('channel', 1, 'type', 'scr', 'delimiter', ',')};
                [sts, data, sourceinfo] = pspm_get_csv([out_dir, task_run,'.csv'], import);
                % Creating the header struct within data{1,1}
                data{1,1}.header.chantype = 'scr';
                data{1,1}.header.units = 'unknown';
                data{1,1}.header.sr = my_sr;
                
                % Creating the transfer struct within the header
                data{1,1}.header.transfer.RS = 0;
                data{1,1}.header.transfer.offset = 0;
                data{1,1}.header.transfer.c = 1;
                data{1,1}.header.transfer.recsys = 'conductance';
                % create info field
                infos = struct();
                infos.duration = length(data{1}.data)/data{1,1}.header.sr;  
                infos.durationinfo = "Recording duration in seconds";
                save([out_dir, task_run, '_datafile.mat'], 'data', 'infos');
                
                % Initialize 'import' as an empty structure to get event info
                task_run_base = regexprep(task_run, '_scr$', '');
                % Assuming event_onsets_seconds contains your event onset times in seconds
                events = readtable([eventdir,task_run_base, '_events.tsv'], "FileType","text",'Delimiter', '\t');
                event_onsets = events.onset_scr;
                event_onsets_seconds = event_onsets / 100;
                timing_info = struct();
                timing_info.names = {'Heat'}; % If you have only one type of event. Replace 'Event' with the actual event name if you have it.
                timing_info.onsets = {event_onsets_seconds}; % Cell array of onset times
                timing_info.durations = {ones(size(event_onsets_seconds))}; % Durations are zeros for event-related designs
            end
            
            %%
            if run_glm
                % Now, this timing_info can be used in the model structure for pspm_glm
                model.timing = {timing_info};
                model.timeunits = 'seconds';
                model.modelfile = [out_dir, task_run,'_glm.mat'];  % Filename for saving the model output
                model.datafile = {[out_dir, task_run, '_datafile.mat']}; % Directly use the data variable
                model.modelspec = 'scr';               % Model specification
                model.filter.sr = my_sr;      % Current sample rate
                model.filter.lpfreq = NaN;         % Disable low-pass filter
                model.filter.lporder = 1;          % Set to a default value
                model.filter.hpfreq = NaN;         % Disable high-pass filter
                model.filter.hporder = 1;          % Set to a default value
                model.filter.direction = 'bi';     % Set filter direction
                model.filter.down = my_sr; 
                % Define options (if necessary)
                options.overwrite = 1; % Overwrite existing files
                % Run the GLM
                glm = pspm_glm(model, options);
            end
    
            %% %import the glm output and transform into a format that is equal to
            if run_sf==1
                load([out_dir, task_run, '_datafile.mat']);
                data{1,1}.data= glm.e;
                data = data([1],:);
                infos = glm.infos;
                data{1,1}.header.sr=glm.infos.sr;
                save([out_dir, task_run,'_glm_residual.mat'], 'data', 'infos');
                sf_model.datafile = [out_dir, task_run,'_glm_residual.mat']; % Path to the file with residuals
                sf_model.modelfile = [out_dir, task_run,'_sf_output.mat']; % Filename to save the SF analysis output
                sf_model.timing = 'whole'; % Analyze the entire duration of the residuals
                sf_model.timeunits = 'whole'; % Indicates that the entire file is used for analysis
                sf_model.method = 'auc'; % Method for SF analysis, Dynamic Causal Modeling
                sf_model.channel = 1; % Use the first channel from the residuals file
                sf_options.overwrite = true;
                pspm_sf(sf_model, sf_options);
            end
        end

    end
end





