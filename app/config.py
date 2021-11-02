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
logging_interval = logging_duration / average_samples
DEBUG = True

# path for the python scripts
APP_PATH = os.path.abspath(os.path.dirname(__file__))
print(APP_PATH)
# absolute path for the generated data of the weather logger
APP_DATA_PATH = 'testdata/'

# sqlite3 database filename
DB_FILENAME = 'weather_logs.db'

# folder names within the static path
REPORTS_FOLDER = 'reports/'
PLOTS_FOLDER = 'plots/'
EXPORTEDS_FOLDER = 'exporteds/'

# filename dateformat
FILENAME_DATEFORMAT = '%m%d%Y'
# filename prefixes
REPORT_PREFIX = 'report_'
# filename prefix for plot image files
PLOT_PREFIX = 'plot_'
# ex[prted data prefix
EXPORT_PREFIX = 'export_'
AGG_EXPORT_PREFIX = 'aggexport_'

# database table names
TABLES = ["Temperature", "Humidity", "BMP_temperature", "Pressure"]
# database table abbreviations
TABLE_ABBREVS = ['dhttemp', 'dhthumd', 'bmptemp', 'bmppres']
# weather data units
UNITS = ['°C', '%', '°C', 'HPa']
# weather data columns
WEATHER_DATA_LIST = list('{} ({})'.format(TABLES[w], UNITS[w]) for w in range(len(TABLES)))
HEADER = dict(zip(TABLE_ABBREVS,WEATHER_DATA_LIST))
# ~ print(HEADER)

# print(WEATHER_DATA)
# statistics
STATS = ('mean', 'std', 'min', 'max')

# weather data daily trends csv output filename
DAILY_TRENDS_PREFIX = 'dailyweathertrends_'

create_path(APP_PATH)
create_path(APP_DATA_PATH)
create_path(APP_DATA_PATH + REPORTS_FOLDER)
create_path(APP_DATA_PATH + PLOTS_FOLDER)
create_path(APP_DATA_PATH + EXPORTEDS_FOLDER)
