% segments data from each block into trials from 1s before heat onset to 10s
% after cue onset (1s after rating), concatenates data from all blocks
% and saves it in pd_epo_all.mat
% events are stored in a combined file related to the epoch
% additionally creates single trial plots so that one can check data
% quality

function pupil_dilation_epoch(cfg)

interval = [-1 10]; % trial interval in s relative to heat onset
new_file_path = fullfile(cfg.data, cfg.out);
raw_file_path = fullfile(cfg.data);

fighandle = figure('units','normalized','outerposition',[0 0 1 1]);
fighandle2 = figure('units','normalized','outerposition',[0 0 1 1]);

pd_epo_all = [];
blink_epo_all = [];
for irun = 1:numel(cfg.runs)
    disp(cfg.runs{irun})
    name_stem = fullfile([cfg.runs{irun}]);
    filt_file = fullfile(raw_file_path, [name_stem '.tsv']);
    if ~exist(filt_file,'file')
        error('No filtered files found!')
    end
    data = readtable(filt_file, "FileType","text",'Delimiter', '\t');
    events = readtable(fullfile(raw_file_path, [name_stem '_events.tsv']),...
        'FileType','text','Delimiter','\t','TreatAsEmpty',{'n/a'});
    sr = 100;
    % onsets in samples
    heat_onsets = events.onset_eyetrackfile;
    epoch_info = events(strcmp(events.event, 'heat'),:); 
    epoch_info.epoch_heat_onset = repmat((-interval(1)*sr)/sr,height(heat_onsets),1);
    epoch_info.epoch_sr = repmat(sr,height(epoch_info),1);
    epoch_info.run = repmat(irun,height(epoch_info),1);
    num_trials = length(heat_onsets);
    num_samples = interval(2)*sr - interval(1)*sr;
    blink_epo = zeros(num_samples,num_trials);
    pd_epo = zeros(num_samples,num_trials);
    for trial = 1:num_trials
        pd_epo(:,trial) = data.pupil_size(round(heat_onsets(trial) + interval(1)*sr):round(heat_onsets(trial) + interval(2)*sr)-1,1);
        blink_epo(:,trial) = data.blinks(round(heat_onsets(trial) + interval(1)*sr):...
            round(heat_onsets(trial) + interval(2)*sr)-1,1) | ...
            data.artifacts_manual(round(heat_onsets(trial) + interval(1)*sr):...
            round(heat_onsets(trial) + interval(2)*sr)-1,1);
    end
    %discard_trials?
    trial_discard_crit = 0.5; % ratio of samples in a trial that is 'too many'
    run_discard_crit = 0.5; % ratio of trials in a run that is 'too many'
    subj_discard_crit = 0.5; % ratio of runs for a subject that is 'too many'
    epoch_info.discard_trial = zeros(height(epoch_info),1);
    for trial = 1:height(epoch_info)
        if sum(blink_epo(:,trial))>trial_discard_crit*size(blink_epo,1)
            epoch_info.discard_trial(trial) = 1;
        end
    end

    % start at zero with heat onset
    interval_samples = (-interval(1))*sr;
    for trial=1:num_trials
        pd_epo(:,trial) = pd_epo(:,trial) - pd_epo(interval_samples+1,trial);
    end
    
    x = (1-interval_samples:1:size(pd_epo,1)-interval_samples)/sr;
    
    pd_epo_all = [pd_epo_all pd_epo];
    blink_epo_all = [blink_epo_all blink_epo];
    if ~exist('epoch_info_all','var')
        epoch_info_all = epoch_info;
    else
        epoch_info_all = [epoch_info_all; epoch_info];
    end
    
    % plot average response per block
    figure(fighandle)
    mean_response = nanmean(pd_epo, 2)';
    sem_response = (nanstd(pd_epo, 0, 2)/sqrt(size(pd_epo,2)))';
    color_pain_high = [135,3,1]/255;
    subplot(2,3,irun)
    hold on
    h1a = fill([x fliplr(x)],[mean_response + sem_response fliplr(mean_response - ...
        sem_response)],...
        color_pain_high, 'FaceAlpha', 0.2,'linestyle','none');
    h1 = plot(x, mean_response, 'Color', color_pain_high, 'LineWidth',3);
    h7 = line([0 0], get(gca,'ylim'),'LineWidth',2,'Color','k');
    hold off
    set(gca,'fontsize',14)
    xlabel('seconds')
    ylabel('pupil dilation')
    title(['block ' num2str(irun)])
    
    % plot single responses per block
    figure(fighandle2)
    % leave the third column, second row subplot for the legend
    subplot(2,3,irun)
    
    my_color_start = [0 0 1];
    new_color = my_color_start;
    legend_label = {};
    hold on
    h7 = line([0 0], get(gca,'ylim'),'LineWidth',2,'Color','k','DisplayName',...
        'heat onset');
    for trial = 1:num_trials
        plot(x, pd_epo(:,trial), 'Color', new_color, 'DisplayName',...
            ['trial ' num2str(trial)], 'LineWidth',2);
            legend_label{end+1}= ['trial ' num2str(trial)];
        new_color = new_color + [0 0.0195 -0.0100]; % winter colormap every 5th entry
    end
    line([0 0], get(gca,'ylim'),'LineWidth',2,'Color','k','DisplayName',...
        'trial onset');
    hold off
    set(gca,'fontsize',14)
    xlabel('seconds')
    ylabel('pupil dilation')
    title(['block ' num2str(irun)])
end

new_name = [cfg.sub,'_',cfg.ses];
writematrix(pd_epo_all, [new_file_path,'/',new_name,'_pupil_epochs_CombinedRuns.csv']);
writematrix(blink_epo_all, [new_file_path,'/',new_name,'_blinks_CombinedRuns.csv']);
writetable(epoch_info_all,fullfile(new_file_path,[new_name '_epoch_info_CombinedRuns.csv']),...
    'FileType','text','Delimiter',',');

% % cheat to get the legend to the right as if it were a seperate subplot
figure(fighandle2)
subplot(2,3,6)
my_color_start = [0 0 1];
new_color = my_color_start;
hold on
for i=1:num_trials
    plot(0,0, 'Color', new_color);
    new_color = new_color + [0 0.0195 -0.0100]; % winter colormap every 5th entry
end
hold off
axis off
legend(legend_label, 'Location', 'southeastoutside')
saveas(fighandle,fullfile(new_file_path,[new_name '_run_average_CombinedRuns.png']))
saveas(fighandle2,fullfile(new_file_path,[new_name '_single_trial_CombinedRuns.png']))
% close(fighandle)
% close(fighandle2)
end
