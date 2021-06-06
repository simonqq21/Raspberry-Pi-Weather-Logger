#!/usr/bin/python3
import os

'''
This is the global configuration file for this application. It contains file paths and file prefixes
of the application.
absolute paths are used to access files from Python scripts, while Flask static paths are used
to access files from the webpage in the web browser.
'''

# create path if it does not exist
def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

logging_duration = 30 # logging delay
DEBUG = False

# path for the python scripts
APP_PATH = os.path.abspath(os.path.dirname(__file__))
# used for building Flask URLs
STATIC_PATH = '/static/files/'
# absolute path for the generated data of the weather logger
APP_DATA_PATH = '/media/weather_logs/'

# sqlite3 database filename
DB_FILENAME = 'weather_logs.db'

# folder names within the static path
WEATHER_LOGS_FOLDER = 'weather_logs/'
SUMMARIES_FOLDER = 'summaries/'
REPORTS_FOLDER = 'reports/'
PLOTS_FOLDER = 'plots/'

# filename prefixes
# filename prefix for raw weather logs
RAW_LOG_PREFIX = 'weather_log'
# filename prefix for processed weather logs
PROCESSED_LOG_PREFIX = 'processed_' + RAW_LOG_PREFIX
# filename prefix for summarized text files
SUMMARY_PREFIX = 'summary_'
# filename prefix for reports
REPORT_PREFIX = 'report_'
# filename prefix for plot image files
PLOT_PREFIX = 'plot_'

# datalogging frequencies in minutes
RAW_LOGGING_FREQ = 1
PROCESSED_LOGGING_FREQ = 5

# database table names
DB_WEATHER_TABLES = ["Humidity", "Temperature", "BMP_temperature", "Pressure"]
# database table abbreviations
DB_WEATHER_TABLES_ABBREVS = ['h', 't', 'btp', 'p']
# weather data units
UNITS = ['%', '°C', '°C', 'HPa']
# weather data columns
WEATHER_DATA = list('{} ({})'.format(DB_WEATHER_TABLES[w], UNITS[w]) for w in range(len(DB_WEATHER_TABLES_ABBREVS)))
# print(WEATHER_DATA)
# statistics
STATS = ('mean', 'std', 'min', 'max')

# weather data daily trends csv output filename
DAILY_TRENDS_PREFIX = 'dailyweathertrends'

create_path(APP_PATH)
create_path(APP_DATA_PATH)
create_path(APP_DATA_PATH + WEATHER_LOGS_FOLDER)
create_path(APP_DATA_PATH + SUMMARIES_FOLDER)
create_path(APP_DATA_PATH + REPORTS_FOLDER)
create_path(APP_DATA_PATH + PLOTS_FOLDER)
