from config import APP_PATH, APP_DATA_PATH, \
WEATHER_LOGS_FOLDER, PLOTS_FOLDER, SUMMARIES_FOLDER, REPORTS_FOLDER, \
RAW_LOG_PREFIX, PROCESSED_LOG_PREFIX, PLOT_PREFIX, SUMMARY_PREFIX, REPORT_PREFIX
from config import RAW_LOGGING_FREQ, PROCESSED_LOGGING_FREQ
from config import DEBUG
import argparse
from datetime import datetime, date
import re
import subprocess
import os
from functions import exists, generatereport

# algorithm to decide whether to generate summarized data
# or if the summarized data is already complete and does not need regenerating.

logs_path = APP_DATA_PATH + WEATHER_LOGS_FOLDER
plots_path = APP_DATA_PATH + PLOTS_FOLDER
summaries_path = APP_DATA_PATH + SUMMARIES_FOLDER
reports_path = APP_DATA_PATH + REPORTS_FOLDER

# ratio required for a complete processed weather log file
complete_ratio = PROCESSED_LOGGING_FREQ / RAW_LOGGING_FREQ

today = date.today()

# get the list of files in the weather log dir and sort it
filenames = os.listdir(logs_path)
filenames.sort()

for filename in filenames:
    # get the name of a raw log file
    if re.search("^" + RAW_LOG_PREFIX, filename) is not None:
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        # only process weather log files before today
        if date1 < today:
            strdate = date1.strftime('%m%d%Y')
            print(strdate)
            raw_log_path = logs_path + filename
            processed_log_path = logs_path + PROCESSED_LOG_PREFIX + strdate + '.csv'
            plot_path = plots_path + PLOT_PREFIX + strdate + '.png'
            summary_path = summaries_path + SUMMARY_PREFIX + strdate + '.txt'
            report_path = reports_path + REPORT_PREFIX + strdate + '.txt'

            # if the processed log file exists,
            if exists(processed_log_path) and exists(plot_path) and exists(summary_path) \
            and exists(report_path):
                # get the line count of the raw log file
                raw_log_lc = sum(1 for line in open(raw_log_path))
                print('raw log line count: {}'.format(raw_log_lc))

                # get the line count of the processed log file
                processed_log_lc = sum(1 for line in open(processed_log_path))
                print('processed log line count: {}'.format(processed_log_lc))

                # check the ratio
                ratio = round(raw_log_lc/processed_log_lc)
                print('ratio of raw to processed: {}'.format(ratio))

                # if ratio is higher than the complete ratio value, regenerate the reports
                if ratio > complete_ratio:
                    print('regeneration needed')
                    generatereport(date1.month, date1.day, date1.year)
                else:
                    print('OK')
                print()

            # else the processed log file does not exist, generate the reports
            else:
                print('generation needed')
                generatereport(date1.month, date1.day, date1.year)

# add statistical data to the database
subprocess.Popen('python3 {}/db_weather_logger.py'.format(APP_PATH), shell=True)
