'''

csv log file with mean, std, min, and max of each column of each day within the range
- date, temp mean, temp std, temp min, temp max, humid mean, ...
save aggregated data for the date range in a report file
file contents:
- date range (start and end date)
- overall mean value of the means per column
- overall std value of the means per column
- overall min value of the means per column
- overall max value of the means per column
- overall mean value of the min values per column
- overall std value of the min values per column
- overall min value of the min values per column
- overall max value of the min values per column
- overall mean value of the max values per column
- overall std value of the max values per column
- overall min value of the max values per column
- overall max value of the max values per column
- array of days with the lowest mean value per column
- array of days with the highest mean value per column
- array of days with the lowest minimum value per column
- array of days with the highest maximum value per column
image plot of mean, std, min, and max per column per day, if graph is selected
'''

import numpy as np
# import matplotlib.pyplot as plt
import argparse
import csv
import sqlite3
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME
from config import WEATHER_DATA, STATS

# set float print precision
np.set_printoptions(precision=3, suppress=True)

# get the two dates
# argument specs: date1 (-y year -m month -d day) date2 (-y year -m month -d day) -g
# parser = argparse.ArgumentParser()
# date1 = parser.add_argument_group('date1')
# date2 = parser.add_argument_group('date2')
# date1.add_argument('startyear', type=int, help='year of starting date')
# date1.add_argument('startmonth', type=int, help='month of starting date')
# date1.add_argument('startday', type=int, help='day of starting date')
# date2.add_argument('endyear', type=int, help='year of ending date')
# date2.add_argument('endmonth', type=int, help='month of ending date')
# date2.add_argument('endday', type=int, help='day of ending date')
# parser.add_argument('-g', '--graph', help="graph the data and save it to an image file if \
# specified", action='store_true')
# args = parser.parse_args()
# print(args)

# get the start and end date and format them as strings for sqlite to use
# startdate = date(args.startyear, args.startmonth, args.startday)
# enddate = date(args.endyear, args.endmonth, args.endday)
# testing
startdate = date(2021, 3, 12)
enddate = date(2021, 3, 16)
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
h.mean AS h_mean, h.std AS h_std, h.min AS h_min, h.max AS h_max, \
t.mean AS t_mean, t.std AS t_std, t.min AS t_min, t.max AS t_max, \
btp.mean AS btp_mean, btp.std AS btp_std, btp.min AS btp_min, btp.max AS btp_max, \
p.mean AS p_mean, p.std AS p_std, p.min AS p_min, p.max AS p_max \
FROM dates d \
JOIN temperature t ON d.id = t.id \
JOIN bmp_temperature btp ON d.id = btp.id \
JOIN humidity h ON d.id = h.id \
JOIN pressure p ON d.id = p.id \
WHERE d.date BETWEEN ? AND ?', (startdatestr, enddatestr))

# get overall results
results_matrix = np.empty((18,))
print(results_matrix.shape)
results = list(dict(row) for row in results.fetchall())
for dict_row in results:
    # print(dict_row)
    temp_matrix_row = np.hstack(list(dict_row[key] for key in dict_row))
    results_matrix = np.vstack((results_matrix, temp_matrix_row))
results_matrix = results_matrix[1:,:]

print(results_matrix)

# save the array of dates to numpy array
dates_arr = 

# save the numerical data to a numpy array
numbers = np.hstack((results_matrix[:,2:6], results_matrix[:,6:10], \
                    results_matrix[:,10:14], results_matrix[:,14:18]))
numbers = numbers.astype(np.float64)
print(numbers)
print(numbers.shape)
print(numbers.dtype)
print()

# create array of column headers and stat measures
header = np.array(WEATHER_DATA)
stats = np.array(STATS)
print(header)
print(stats)

'''
create a 3d numpy array with first dimension the number of statistical measures ie. (min, std,
min, max) = 4, the second dimension the number of days in the date interval, and the third
dimension the number of column headers ie. (humd, temp, bmptemp, pres) = 4
'''
stat_numbers = np.empty((len(stats),numbers.shape[0], len(header)))
for i in range(len(stats)):
    stat_numbers[i] = numbers[:,i::4]
print(stat_numbers)

# get the mean, std, min, and max of the means per day


con.close()
