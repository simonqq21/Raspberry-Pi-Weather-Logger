'''
get 2 input dates as arguments
get aggregated weather data from the database of daily weather data ranging between the 2 input dates and
place them in a numpy array
save numpy array as CSV file for download
get the mean, std, min, and max of the data
get the days with the minimum and maximum data
save aggregated data for the date range in a report file
generate the plot of mean, std, min, and max per day with matplotlib
'''

import numpy as np
import matplotlib.pyplot as plt
import argparse
import csv
import sqlite3
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME

# get the two dates
# argument specs: date1 (-y year -m month -d day) date2 (-y year -m month -d day) -g
parser = argparse.ArgumentParser()
date1 = parser.add_argument_group('date1')
date2 = parser.add_argument_group('date2')
date1.add_argument('startyear', type=int, help='year of starting date')
date1.add_argument('startmonth', type=int, help='month of starting date')
date1.add_argument('startday', type=int, help='day of starting date')
date2.add_argument('endyear', type=int, help='year of ending date')
date2.add_argument('endmonth', type=int, help='month of ending date')
date2.add_argument('endday', type=int, help='day of ending date')
parser.add_argument('-g', '--graph', help="graph the data and save it to an image file if \
specified", action='store_true')
args = parser.parse_args()
# print(args)


# read the data of the days between the two dates from the db
