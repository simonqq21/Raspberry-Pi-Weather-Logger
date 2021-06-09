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

logging_duration = 300 # logging delay in sec, default 300secs for 5mins
average_samples = 5 # samples per averaged log, default 6 times 
DEBUG = True

# path for the python scripts
APP_PATH = os.path.abspath(os.path.dirname(__file__))
print(APP_PATH)
# used for building Flask URLs
STATIC_PATH = '/static/files/'
# absolute path for the generated data of the weather logger
APP_DATA_PATH = APP_PATH + '/'
# APP_DATA_PATH = '/media/pi/weather_logger'

# sqlite3 database filename
DB_FILENAME = 'weather_logs.db'

# folder names within the static path
REPORTS_FOLDER = 'reports/'
PLOTS_FOLDER = 'plots/'

# filename prefixes
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
create_path(APP_DATA_PATH + REPORTS_FOLDER)
create_path(APP_DATA_PATH + PLOTS_FOLDER)
