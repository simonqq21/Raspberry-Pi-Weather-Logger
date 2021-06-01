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
import argparse
import csv
import sqlite3
import os
import re
import sys
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME
from config import WEATHER_DATA, STATS, DB_WEATHER_TABLES, UNITS
from config import DAILY_TRENDS_PREFIX
from functions import deleteAllSimilar, appendNewline

# set float print precision
np.set_printoptions(precision=3, suppress=True)

# get the two dates
# argument specs: date1 (-y year -m month -d day) date2 (-y year -m month -d day) -g
parser = argparse.ArgumentParser()
# date1 = parser.add_argument_group('date1')
# date2 = parser.add_argument_group('date2')
# date1.add_argument('startyear', type=int, help='year of starting date')
# date1.add_argument('startmonth', type=int, help='month of starting date')
# date1.add_argument('startday', type=int, help='day of starting date')
# date2.add_argument('endyear', type=int, help='year of ending date')
# date2.add_argument('endmonth', type=int, help='month of ending date')
# date2.add_argument('endday', type=int, help='day of ending date')
parser.add_argument('-g', '--graph', help="graph the data and save it to an image file if \
specified", action='store_true')
args = parser.parse_args()
# print(args)

# get the start and end date and format them as strings for sqlite to use
# startdate = date(args.startyear, args.startmonth, args.startday)
# enddate = date(args.endyear, args.endmonth, args.endday)

# testing code
startdate = date(2021, 2, 12)
enddate = date(2021, 4, 17)
# startdate = date(2021, 3, 31)
# enddate = date(2021, 4, 1)

startdatestr = startdate.strftime("%Y-%m-%d")
enddatestr = enddate.strftime("%Y-%m-%d")
# print(startdatestr, enddatestr)

# create array of column headers and stat measures
header = np.array(WEATHER_DATA)
stats = np.array(STATS)

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
WHERE d.date BETWEEN ? AND ? \
ORDER BY d.date ASC', (startdatestr, enddatestr))

# save overall results to numpy array
results_matrix = np.empty((1,18))
results = list(dict(row) for row in results.fetchall())
for dict_row in results:
    temp_matrix_row = np.hstack(list(dict_row[key] for key in dict_row))
    results_matrix = np.vstack((results_matrix, temp_matrix_row))
# print(results_matrix.shape)
if results_matrix.shape[0] > 1:
    results_matrix = results_matrix[1:,:]
else:
    print('No results in those dates.')
    sys.exit(0)
# print(results_matrix)

# generate csv file header
csv_header = 'date,'
for h in range(len(header)):
    for s in range(len(stats)):
        csv_header += header[h] + '_' + stats[s]
        if h < len(header) - 1 or s < len(stats) - 1:
            csv_header += ','
# print(csv_header)

# delete any existing daily trends csv file before generating new csv file
deleteAllSimilar(APP_DATA_PATH, DAILY_TRENDS_PREFIX)

# save the database results as a csv file for download
np.savetxt(APP_DATA_PATH + DAILY_TRENDS_PREFIX + '{}_{}.csv'.format(startdatestr, enddatestr), \
results_matrix[:,1:], delimiter=',', fmt=['%s'] * 17, header=csv_header, comments='')

# save the array of dates to numpy array
dates_arr = results_matrix[:,1].astype(np.datetime64)
# print(dates_arr)

# save the numerical data to a numpy array
numbers = np.hstack((results_matrix[:,2:6], results_matrix[:,6:10], \
                    results_matrix[:,10:14], results_matrix[:,14:18]))
numbers = numbers.astype(np.float64)
# print(numbers)
# print(numbers.shape)
# print(numbers.dtype)
# print()

# create a 3d numpy array to hold the data for processing
stat_numbers = np.empty((len(stats), numbers.shape[0], len(header)))
for i in range(len(stats)):
    stat_numbers[i] = numbers[:,i::4]
stat_numbers = stat_numbers.transpose()
print(stat_numbers)
aggregated_results = {}

# get the mean, std, min, and max of the data per day
for i in range(len(header)):
    aggregated_results[header[i]] = {}
    for j in range(len(stats)):
        aggregated_results[header[i]][stats[j]] = {}
        # get the mean, std, min, and max of each stat
        aggregated_results[header[i]][stats[j]]['mean'] = stat_numbers[i,:,j].mean(axis=0)
        if stats[j] != 'std':
            aggregated_results[header[i]][stats[j]]['std'] = stat_numbers[i,:,j].std(axis=0)
        aggregated_results[header[i]][stats[j]]['min'] = stat_numbers[i,:,j].min(axis=0)
        aggregated_results[header[i]][stats[j]]['max'] = stat_numbers[i,:,j].max(axis=0)
        # get the days when a value is min and max
        aggregated_results[header[i]][stats[j]]['min_days'] = \
        dates_arr[np.where(stat_numbers == stat_numbers[i,:,j].min(axis=0))[1]]
        aggregated_results[header[i]][stats[j]]['max_days'] = \
        dates_arr[np.where(stat_numbers == stat_numbers[i,:,j].max(axis=0))[1]]
# print(aggregated_results)

# generate a report text file
with open(APP_DATA_PATH + DAILY_TRENDS_PREFIX + '{}_{}.txt'.format(startdatestr, enddatestr), 'w') as file:
    file.write(appendNewline('---------- Weather Data Daily Trends Report ----------'))
    file.write(appendNewline('start date: {}'.format(startdatestr)))
    file.write(appendNewline('end date: {}'.format(enddatestr)))
    file.write(appendNewline(''))
    file.write(appendNewline('---------- Key Data -----------'))
    file.write(appendNewline(''))
    for t in range(len(DB_WEATHER_TABLES)):
        file.write(appendNewline('{} mean mean: {:.3f}{}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['mean']['mean'], UNITS[t])))
        file.write(appendNewline('{} mean min: {:.3f}{}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['mean']['min'], UNITS[t])))
        file.write(appendNewline('{} mean min_days: {}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['mean']['min_days'])))
        file.write(appendNewline('{} mean max: {:.3f}{}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['mean']['max'], UNITS[t])))
        file.write(appendNewline('{} mean max_days: {}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['mean']['max_days'])))
        file.write(appendNewline('{} min min: {:.3f}{}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['min']['min'], UNITS[t])))
        file.write(appendNewline('{} min min_days: {}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['min']['min_days'])))
        file.write(appendNewline('{} max max: {:.3f}{}'.format(DB_WEATHER_TABLES[t].lower(), \
        aggregated_results[header[t]]['max']['max'], UNITS[t])))
        file.write(appendNewline('{} max max_days: {}'.format(DB_WEATHER_TABLES[t].lower(),
        aggregated_results[header[t]]['max']['max_days'])))
        file.write(appendNewline(''))
    file.write(appendNewline(''))
    file.write(appendNewline('---------- Complete aggregated data ----------'))
    file.write(appendNewline(''))
    for h in range(len(header)):
        for s in stats:
            for s2 in aggregated_results[header[h]][s]:
                file.write(appendNewline("{} {} {}: {}".format(header[h], s, s2, \
                aggregated_results[header[h]][s][s2])))
            file.write(appendNewline(''))
        file.write(appendNewline(''))
    file.write(appendNewline(''))

# generate graph if graph option is set
if args.graph:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib

    # save the data to graph
    graph_data = {}
    for h in range(len(header)):
        graph_data[header[h]] = {}
        for s in range(len(stats)):
            if stats[s] != 'std':
                graph_data[header[h]][stats[s]] = stat_numbers[h,:,s]
    # print(graph_data)

    # fonts
    suptitlefont = {'family':'monospace','color':'black'}
    titlefont = {'family':'monospace','color':'black','size':20}
    axisfont = {'family':'monospace','color':'black','size':20}
    plt.rc('legend', fontsize=20)

    # set the time format to HH:MM
    timeformat = mdates.DateFormatter('%Y/%m/%d')

    # set the subplots and figure size
    figure, axes = plt.subplots(4,1, figsize=(22, 15), sharex=True)

    # super title
    figure.suptitle('Weather Data Trends from {} to {}'.format(startdate.strftime('%m%d%Y'), \
    enddate.strftime('%m%d%Y')), fontdict=suptitlefont, fontsize=40)

    # subgraph for humidity
    axes[0].set_title(WEATHER_DATA[0], fontdict=titlefont)
    axes[0].set_ylabel(WEATHER_DATA[0], fontdict=axisfont)
    axes[0].plot(dates_arr, graph_data[WEATHER_DATA[0]]['mean'], label="humidity_mean", linestyle='-', color='#0000ff', linewidth=4)
    axes[0].plot(dates_arr, graph_data[WEATHER_DATA[0]]['min'], label="humidity_min", linestyle='-', color='#000099', linewidth=4)
    axes[0].plot(dates_arr, graph_data[WEATHER_DATA[0]]['max'], label="humidity_max", linestyle='-', color='#9999ff', linewidth=4)
    axes[0].legend()

    # subgraph for temperature
    axes[1].set_title(WEATHER_DATA[1], fontdict=titlefont)
    axes[1].set_ylabel(WEATHER_DATA[1], fontdict=axisfont)
    axes[1].plot(dates_arr, graph_data[WEATHER_DATA[1]]['mean'], label="temperature_mean", linestyle='-', color='#cd3299', linewidth=4)
    axes[1].plot(dates_arr, graph_data[WEATHER_DATA[1]]['min'], label="temperature_min", linestyle='-', color='#90236b', linewidth=4)
    axes[1].plot(dates_arr, graph_data[WEATHER_DATA[1]]['max'], label="temperature_max", linestyle='-', color='#ebadd6', linewidth=4)
    axes[1].legend()

    # subgraph for bmp_temperature
    axes[2].set_title(WEATHER_DATA[2], fontdict=titlefont)
    axes[2].set_ylabel(WEATHER_DATA[2], fontdict=axisfont)
    axes[2].plot(dates_arr, graph_data[WEATHER_DATA[2]]['mean'], label="bmp_temperature_mean", linestyle='-', color='#ff0000', linewidth=4)
    axes[2].plot(dates_arr, graph_data[WEATHER_DATA[2]]['min'], label="bmp_temperature_min", linestyle='-', color='#990000', linewidth=4)
    axes[2].plot(dates_arr, graph_data[WEATHER_DATA[2]]['max'], label="bmp_temperature_max", linestyle='-', color='#ff8080', linewidth=4)
    axes[2].legend()

    # subgraph for pressure
    axes[3].set_title(WEATHER_DATA[3], fontdict=titlefont)
    axes[3].set_ylabel(WEATHER_DATA[3], fontdict=axisfont)
    axes[3].plot(dates_arr, graph_data[WEATHER_DATA[3]]['mean'], label="pressure_mean", linestyle='-', color='#00b300', linewidth=4)
    axes[3].plot(dates_arr, graph_data[WEATHER_DATA[3]]['min'], label="pressure_min", linestyle='-', color='#003300', linewidth=4)
    axes[3].plot(dates_arr, graph_data[WEATHER_DATA[3]]['max'], label="pressure_max", linestyle='-', color='#1aff1a', linewidth=4)
    axes[3].legend()

    # specify time format of x-axis
    for axis in axes:
        axis.xaxis.set_major_formatter(timeformat)
        axis.xaxis_date()
        # set tick font size and rotation for all subplots
        axis.tick_params(labelsize=18)
        axis.tick_params(axis='x',labelrotation=30)

    figure.subplots_adjust(top=0.92)
    # plt.tight_layout()
    plt.savefig(APP_DATA_PATH + DAILY_TRENDS_PREFIX + '{}_{}.png'.format(startdatestr, enddatestr), dpi=200, bbox_inches='tight')
    print('saved')
con.close()
