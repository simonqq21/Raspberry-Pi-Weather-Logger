from config import APP_PATH, APP_DATA_PATH, \
WEATHER_LOGS_FOLDER, \
RAW_LOG_PREFIX, PROCESSED_LOG_PREFIX
from config import RAW_LOGGING_FREQ, PROCESSED_LOGGING_FREQ
from config import DEBUG
import argparse
from datetime import datetime, date
import re
import subprocess
import os

# algorithm to decide whether to generate summarized data
# or if the summarized data is already complete and does not need regenerating.

# check if file exists
def exists(filepath):
    try:
        f = open(filepath)
    except IOError:
        return False
    f.close()
    return True

# call the report generation script with the date parameters
def generatereport(month, day, year):
    proc1 = subprocess.Popen('python3 {}/weatherdataanalyzer.py -m {} -d {} -y {} -g'.format
    (APP_PATH, month, day, year), stdout=subprocess.PIPE, shell=True)
    if DEBUG:
        output = proc1.communicate()[0]
        output = str(output, 'UTF-8')
        print(output)

logs_file_path = APP_DATA_PATH + WEATHER_LOGS_FOLDER

# ratio required for a complete processed weather log file
complete_ratio = PROCESSED_LOGGING_FREQ / RAW_LOGGING_FREQ

today = date.today()

# get the list of files in the weather log dir and sort it
filenames = os.listdir(logs_file_path)
filenames.sort()

for filename in filenames:
    # get the name of a raw log file
    if re.search("^" + RAW_LOG_PREFIX, filename) is not None:
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        # only process weather log files before today
        if date1 < today:
            raw_log_path = logs_file_path + filename
            processed_log_path = (logs_file_path + PROCESSED_LOG_PREFIX +
                date1.strftime('%m%d%Y') + '.csv' )

            print(raw_log_path)
            print(processed_log_path)

            # get the line count of the raw log file
            raw_log_lc = sum(1 for line in open(raw_log_path))
            print('raw log line count: {}'.format(raw_log_lc))

            # if the processed log file exists,
            if exists(processed_log_path):
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
