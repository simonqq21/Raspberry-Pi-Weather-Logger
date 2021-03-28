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
print(args)

# get the start and end date and format them as strings for sqlite to use
startdate = date(args.startyear, args.startmonth, args.startday)
enddate = date(args.endyear, args.endmonth, args.endday)
startdatestr = startdate.strftime("%Y-%m-%d")
enddatestr = enddate.strftime("%Y-%m-%d")
print(startdatestr, enddatestr)

# connect to sqlite db
con = sqlite3.connect(APP_DATA_PATH + DB_FILENAME)
# set connection to return query results as Rows
con.row_factory = sqlite3.Row
cur = con.cursor()

# read the data of the days between the two dates from the db
results = cur.execute('SELECT d.id, d.date, \
t.mean AS t_mean, t.std AS t_std, t.min AS t_min, t.max AS t_max, \
btp.mean AS btp_mean, btp.std AS btp_std, btp.min AS btp_min, btp.max AS btp_max, \
h.mean AS h_mean, h.std AS h_std, h.min AS h_min, h.max AS h_max, \
p.mean AS p_mean, p.std AS p_std, p.min AS p_min, p.max AS p_max \
FROM dates d \
JOIN temperature t ON d.id = t.id \
JOIN bmp_temperature btp ON d.id = btp.id \
JOIN humidity h ON d.id = h.id \
JOIN pressure p ON d.id = p.id \
WHERE d.date BETWEEN ? AND ?', (startdatestr, enddatestr))

results_matrix = np.empty((18,))
print(results_matrix.shape)
results = list(dict(row) for row in results.fetchall())
for dict_row in results:
    # print(dict_row)
    temp_matrix_row = np.hstack(list(dict_row[key] for key in dict_row))
    results_matrix = np.vstack((results_matrix, temp_matrix_row))
results_matrix = results_matrix[1:,:]

print(results_matrix)

# save the numerical data to a numpy array
numbers = np.hstack((results_matrix[:,2:6], results_matrix[:,6:10], \
                    results_matrix[:,10:14], results_matrix[:,14:18]))
print(numbers)
print(numbers.shape)
print()
con.close()
