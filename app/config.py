#!/usr/bin/python3

# This is the global configuration file for this application. It contains file paths of the
# application.

import os

# path for the python scripts
APP_PATH = os.path.abspath(os.path.dirname(__file__))
# path for the generated data of the weather logger
APP_DATA_PATH = APP_PATH + '/static/files/'
# path of weather logs
WEATHER_LOGS_PATH = APP_DATA_PATH + 'weather_logs/'
# absolute path of summarized data
SUMMARIES_PATH = APP_DATA_PATH + 'summaries/'
# absolute path of weather plot images
PLOTS_PATH = APP_DATA_PATH + 'plots/'
# filename prefix for raw weather logs
RAW_LOG_PREFIX = 'weather_log'
# filename prefix for processed weather logs
PROCESSED_LOG_PREFIX = 'processed_' + RAW_LOG_PREFIX
# filename prefix for summarized text files
SUMMARY_PREFIX = 'summary_'
# filename prefix for plot image files
PLOT_PREFIX = 'plot_'
