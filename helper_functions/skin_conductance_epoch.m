% segments data from each block into trials from 1s before onset
% to 7s after onset
% and saves it in scr_epo_all.mat
% additionally creates single trial plots so that one can check data
% quality

function skin_conductance_epoch(cfg)

interval = [-1 10]; % trial interval in s relative to heat onset
raw_file_path = fullfile(cfg.data);
new_file_path = fullfile(cfg.data,cfg.out);

fighandle = figure('units','normalized','outerposition',[0 0 1 1]);

scr_epo_all = [];
new_name = [cfg.sub,'_',cfg.ses];
for ifile=1:numel(cfg.runs)
    name_stem = fullfile([cfg.runs{ifile}]);
    scr_file = fullfile(raw_file_path, [name_stem '.tsv']);
    data = readtable(scr_file, "FileType","text",'Delimiter', '\t');
    data_t = table2array(data)';
    sr = 100;
    % get event info
    eventfile_list = dir(fullfile(cfg.eventdir, [cfg.sub,'*ReliabilityRun*','_events.tsv']));
    eventfile = fullfile(cfg.eventdir, [eventfile_list.name]);
    events = readtable(eventfile, "FileType","text",'Delimiter', '\t');
    onsets = events.onset_scr;
    
    scr_epo = epoch(data_t, onsets, [interval(1)*sr interval(2)*sr]);
    scr_epo = squeeze(scr_epo); % removes useless channel dimension
    
    interval_samples = (-interval(1))*sr;
    num_trials = size(scr_epo,2);
    for trial=1:num_trials
        % start at zero with cue onset
        scr_epo(:,trial) = scr_epo(:,trial) - scr_epo(interval_samples+1,trial);
    end
   
    % put all into one big data frame
    scr_epo_all = [scr_epo_all scr_epo];
    
%     % plot all single trials in one plot (for each block)
    clf(fighandle);
    x = (1-interval_samples:1:size(scr_epo,1)-interval_samples)/sr;
    for trial=1:num_trials
        hold on
        plot(x, scr_epo(:,trial), 'DisplayName', ['trial ' num2str(trial)],...
            'LineWidth', 2);
%         ylim([-1 2])
        xlabel('seconds')
        ylabel('skin conductance \muS')
    end
    line([0 0], get(gca,'ylim'),'LineWidth',2,'Color','k', 'DisplayName', 'heat onset');
    set(gca,'fontsize',16)
    legend show
    hold off
    saveas(fighandle,fullfile(cfg.data, cfg.out, [new_name '_single_trial_ReliabilityRun.png']));
    
    % make another plot with averages for each block
    
    mean_response = nanmean(scr_epo, 2)';
    sem_response = (nanstd(scr_epo_all, 0, 2)/sqrt(size(scr_epo_all,2)))';
    color_pain_high = [135,3,1]/255;
    subplot(2,3,ifile)
    hold on
    h1a = fill([x fliplr(x)],[mean_response + sem_response fliplr(mean_response - sem_response)],...
        color_pain_high, 'FaceAlpha', 0.2,'linestyle','none');
    h1 = plot(x, mean_response, 'Color', color_pain_high, 'LineWidth',3);
    ylim([-0.1 0.2])
    h7 = line([0 0], get(gca,'ylim'),'LineWidth',2,'Color','k');
    hold off
    set(gca,'fontsize',14)
    xlabel('seconds')
    ylabel('skin conductance \muS')
    title(['Run ' num2str(ifile)],'Interpreter','none') 
end
writematrix(scr_epo_all, [new_file_path,'/',name_stem,'_epochs_ReliabilityRun.csv']);
saveas(fighandle,strcat(new_file_path,'/',name_stem,'_run_averages_ReliabilityRun.png'))
close(fighandle)
end


