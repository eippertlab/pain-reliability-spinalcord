clc 
clear all

%%  enable FSL
setenv('FSLDIR', '/afs/cbs.mpg.de/software/fsl/5.0.11/ubuntu-xenial-amd64/'); %insert your FSL dir here
fsldir = getenv('FSLDIR');
fsldirmpath = sprintf('%s/etc/matlab',fsldir);
path(path, fsldirmpath);
setenv('FSLOUTPUTTYPE', 'NIFTI_GZ'); % this to tell what the output type would be

%% Identification %% 
for subject=1::40
    for session=1:2
        clearvars -except subject session
        sub=['sub-',num2str(subject,'%02.f')]
        ses=['ses-',num2str(session,'%02.f')]

        %% Directories and files%%
        %change to your own
        project_dir = ['/data/pt_02306/main/data/pain-reliability-spinalcord/derivatives/']
        func_dir = [project_dir, sub, '/',ses, '/func/preprocessing/']
        data_dir = [func_dir, 'outliers/']
        out_dir = [data_dir, 'feat_input/']
        if exist(data_dir, 'dir')
            %make folders
            if ~exist(out_dir, 'dir')
              mkdir(out_dir);
            end
            cd(data_dir);

            createConfoundMat = 1;
            plotMetricTS      = 0;

            %% get filenames
             dir_list = dir(fullfile(func_dir, '*te40ReliabilityRun*denoised_moco_refined.nii.gz'));
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

            %get task runs and baseline
            runs = sort(all_files);
            %%  LOOP OVER BLOCKS
            for g = 1:length(runs)
                % set everything up
                name = runs{g};
                disp(['Working on block ' name]);

                % load raw metric data
                metricDVARS{:,g}  = load([name,'_dvars2020.txt']);
                metricREFRMS{:,g} = load([name,'_refrms2020.txt']);
                metricTMP{:,g}    = load([name,'_refrms2020edited.txt']);
                metricNEWRMS{:,g} = metricTMP{g}(2:end,1); % in order to remove the initial zero and bring to 1600

                % calculate own thresholds
                tmpThreshDeDVARS  = prctile(metricDVARS{:,g},75) + iqr(metricDVARS{:,g});
                tmpThreshZ2DVARS  = mean(metricDVARS{:,g}) + 2*std(metricDVARS{:,g});
                tmpThreshZ3DVARS  = mean(metricDVARS{:,g}) + 3*std(metricDVARS{:,g});
                tmpThresh95DVARS  = prctile(metricDVARS{:,g},95);
                tmpThresh99DVARS  = prctile(metricDVARS{:,g},99);

                tmpThreshDeREFRMS = prctile(metricREFRMS{:,g},75) + iqr(metricREFRMS{:,g});
                tmpThreshZ2REFRMS = mean(metricREFRMS{:,g}) + 2*std(metricREFRMS{:,g});
                tmpThreshZ3REFRMS = mean(metricREFRMS{:,g}) + 3*std(metricREFRMS{:,g});
                tmpThresh95REFRMS = prctile(metricREFRMS{:,g},95);
                tmpThresh99REFRMS = prctile(metricREFRMS{:,g},99);

                tmpThreshDeNEWRMS = prctile(metricNEWRMS{:,g},75) + iqr(metricNEWRMS{:,g});
                tmpThreshZ2NEWRMS = mean(metricNEWRMS{:,g}) + 2*std(metricNEWRMS{:,g});
                tmpThreshZ3NEWRMS = mean(metricNEWRMS{:,g}) + 3*std(metricNEWRMS{:,g});
                tmpThresh95NEWRMS = prctile(metricNEWRMS{:,g},95);
                tmpThresh99NEWRMS = prctile(metricNEWRMS{:,g},99);

                % get number of outliers according to own thresholds
                thresh95DVARS{g}  = find(metricDVARS{g} >= tmpThresh95DVARS);
                thresh99DVARS{g}  = find(metricDVARS{g} >= tmpThresh95DVARS);
                threshZ2DVARS{g}  = find(metricDVARS{g} >= tmpThreshZ2DVARS);
                threshZ3DVARS{g}  = find(metricDVARS{g} >= tmpThreshZ3DVARS);
                thresh95REFRMS{g} = find(metricREFRMS{g} >= tmpThresh95REFRMS);
                thresh99REFRMS{g} = find(metricREFRMS{g} >= tmpThresh99REFRMS) ;
                threshZ2REFRMS{g} = find(metricREFRMS{g} >= tmpThreshZ2REFRMS);
                threshZ3REFRMS{g} = find(metricREFRMS{g} >= tmpThreshZ3REFRMS);
                thresh95NEWRMS{g} = find(metricNEWRMS{g} >= tmpThresh95NEWRMS);
                thresh99NEWRMS{g} = find(metricNEWRMS{g} >= tmpThresh99NEWRMS) ;
                threshZ2NEWRMS{g} = find(metricNEWRMS{g} >= tmpThreshZ2NEWRMS);
                threshZ3NEWRMS{g} = find(metricNEWRMS{g} >= tmpThreshZ3NEWRMS);


                nvol=size(metricDVARS{g},1);
                % plot data with thresholds
                if plotMetricTS == 1
                    figure;
                    subplot(3,1,1); title([name ', DVARS'],'Interpreter','none'); hold on; plot(metricDVARS{g}(1:nvol), 'k');
                    plot(1:nvol, tmpThresh95DVARS *ones(1,nvol), 'r--'); plot(1:nvol, tmpThresh99DVARS *ones(1,nvol), 'r');
                    plot(1:nvol, tmpThreshZ2DVARS *ones(1,nvol), 'b--'); plot(1:nvol, tmpThreshZ3DVARS *ones(1,nvol), 'b');
                    plot(1:nvol, tmpThreshDeDVARS *ones(1,nvol), 'g'); grid on; grid minor;
                    subplot(3,1,2); title(['Block ' num2str(g) ', REFRMS']); hold on; plot(metricREFRMS{g}(1:nvol), 'k');
                    plot(1:nvol, tmpThresh95REFRMS*ones(1,nvol), 'r--'); plot(1:nvol, tmpThresh99REFRMS*ones(1,nvol), 'r');
                    plot(1:nvol, tmpThreshZ2REFRMS*ones(1,nvol), 'b--'); plot(1:nvol, tmpThreshZ3REFRMS*ones(1,nvol), 'b');
                    plot(1:nvol, tmpThreshDeREFRMS *ones(1,nvol), 'g'); grid on; grid minor;
                    subplot(3,1,3); title(['Block ' num2str(g) ', NEWRMS']); hold on; plot(metricNEWRMS{g}(1:nvol), 'k');
                    plot(1:nvol, tmpThresh95NEWRMS*ones(1,nvol), 'r--'); plot(1:nvol, tmpThresh99NEWRMS*ones(1,nvol), 'r');
                    plot(1:nvol, tmpThreshZ2NEWRMS*ones(1,nvol), 'b--'); plot(1:nvol, tmpThreshZ3NEWRMS*ones(1,nvol), 'b');
                    plot(1:nvol, tmpThreshDeNEWRMS *ones(1,nvol), 'g'); grid on; grid minor;
                end

                % get number of outliers according to default threshold
                try
                    [threshDefaultDVARS{g},  ~] = find(load([name,'_dvars2020']));
                    [threshDefaultREFRMS{g}, ~] = find(load([name,'_refrms2020']));
                    [threshDefaultNEWRMS{g}, ~] = find(load([name,'_refrms2020edited']));
                catch
                    disp('No outliers for this block');
                end

                numTotalOutliers(g)  = numel(       [cell2mat(threshZ2DVARS(g)); cell2mat(threshZ2NEWRMS(g))])
                numUniqueOutliers(g) = numel(unique([cell2mat(threshZ2DVARS(g)); cell2mat(threshZ2NEWRMS(g))]))
                indicesOutliers{g}   = unique(      [cell2mat(threshZ2DVARS(g)); cell2mat(threshZ2NEWRMS(g))])


            % SAVE FILES
                block_outliers=indicesOutliers{g};
                if createConfoundMat == 1
                    cols=numel(block_outliers);
                    if sum(numel(block_outliers))==0
                        cols=1;
                    end
                    outlierMatrix=zeros(nvol,cols);
                    numOutliers = numel(block_outliers);
                    for j = 1:numOutliers
                        if numOutliers > 1
                        outlierMatrix(block_outliers(j),j) = 1; 
                        end
                    end
                    writematrix(outlierMatrix, [out_dir,name,'_outlier.txt'],'Delimiter', 'space')
                end
            end
        end
    end
end
