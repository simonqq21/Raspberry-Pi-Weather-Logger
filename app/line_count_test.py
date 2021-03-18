from config import APP_PATH, APP_DATA_PATH, \
WEATHER_LOGS_FOLDER, \
RAW_LOG_PREFIX, PROCESSED_LOG_PREFIX
from config import RAW_LOGGING_FREQ, PROCESSED_LOGGING_FREQ
import argparse
from datetime import datetime, date

# test to determine line count between raw and processed weather logs
# this will be used to create the algorithm to decide whether to generate summarized data
# or if the summarized data is already complete and does not need regenerating.

complete_ratio = PROCESSED_LOGGING_FREQ / RAW_LOGGING_FREQ

# arguments for date
parser = argparse.ArgumentParser()
parser.add_argument('-m', help='numeric month from 1-12', default=date.today().month, type=int)
parser.add_argument('-d', help='numeric day from 1-31', default=date.today().day, type=int)
parser.add_argument('-y', help='numeric four digit year', default=date.today().year, type=int)
args = parser.parse_args()

# get file paths of raw and processed logs
logs_file_path = APP_DATA_PATH + WEATHER_LOGS_FOLDER
raw_log_path = (logs_file_path + RAW_LOG_PREFIX +
    '{:02}{:02}{}'.format(args.m, args.d, args.y) +
    '.csv' )
processed_log_path = (logs_file_path + PROCESSED_LOG_PREFIX +
    '{:02}{:02}{}'.format(args.m, args.d, args.y) +
    '.csv' )

print(raw_log_path)
print(processed_log_path)

raw_log_lc = sum(1 for line in open(raw_log_path))
processed_log_lc = sum(1 for line in open(processed_log_path))
print('raw log line count: {}'.format(raw_log_lc))
print('processed log line count: {}'.format(processed_log_lc))
ratio = round(raw_log_lc/processed_log_lc)
print('ratio of raw to processed: {}'.format(ratio))

if ratio > complete_ratio:
    print('regeneration needed')
else:
    print('OK')
