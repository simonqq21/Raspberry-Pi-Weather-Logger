from config import APP_PATH, APP_DATA_PATH, PLOTS_FOLDER, REPORTS_FOLDER, \
PLOT_PREFIX, REPORT_PREFIX
from config import DEBUG
import argparse
from datetime import datetime, date
import re
import subprocess
import os
from functions import exists, generatereport
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
from db_module import getAllDates
from sqlalchemy.orm import aliased

'''
generate the text report and image plot for a specific date if that date is before
today and if either the report or plot does not exist
'''

# generate absolute paths
plots_path = APP_DATA_PATH + PLOTS_FOLDER
reports_path = APP_DATA_PATH + REPORTS_FOLDER

# get all dates existing in the db
dates = getAllDates()
today = date.today()

for date in dates:
    # process all dates before today
    if date < today:
        strdate = date.strftime('%m%d%Y')
        plot_path = plots_path + PLOT_PREFIX + strdate + '.png'
        report_path = reports_path + REPORT_PREFIX + strdate + '.txt'

        # check for the existence of the image plot and text report
        if not exists(plot_path) or not exists(report_path):
            print(f'{strdate}: regeneration needed')
            generatereport(date.month, date.day, date.year)
        else:
            print('OK')
        print()
