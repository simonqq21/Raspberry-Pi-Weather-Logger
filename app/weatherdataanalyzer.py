#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import os
from datetime import datetime, date, time
import argparse
import subprocess
from config import APP_PATH, APP_DATA_PATH, \
WEATHER_LOGS_FOLDER, SUMMARIES_FOLDER, REPORTS_FOLDER, PLOTS_FOLDER, \
RAW_LOG_PREFIX, PROCESSED_LOG_PREFIX, SUMMARY_PREFIX, PLOT_PREFIX, REPORT_PREFIX
from config import DEBUG
from config import PROCESSED_LOGGING_FREQ

# set float print precision
np.set_printoptions(precision=3, suppress=True)

'''
This program takes optional year, month, day, and interval as parameters.
This program calls the datalog averager program to process the raw datalog file, then computes
for the mean, standard deviation, maximum value and minimum value for temperature, pressure,
and humidity of a particular day. The data will be graphed and saved as an image file.
'''

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        return 0
    f.close()
    return 1

# append newline to string
def appendNewline(str):
    return str + '\n'

# parse arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument('-m', help='numeric month from 1-12', default=date.today().month, type=int)
parser.add_argument('-d', help='numeric day from 1-31', default=date.today().day, type=int)
parser.add_argument('-y', help='numeric four digit year', default=date.today().year, type=int)
parser.add_argument('-g', '--graph', help='graph the data and save it to an image file', action='store_true')
group2 = parser.add_mutually_exclusive_group()
group2.add_argument('-hr', '--hour', help='The new log interval in hours', type=float)
group2.add_argument('-min', '--minute', help='The new log interval in minutes. Default value is {} minutes'.format(PROCESSED_LOGGING_FREQ),
type=int, default=PROCESSED_LOGGING_FREQ)
args = parser.parse_args()

# saving parameters to variables
month = args.m
day = args.d
year = args.y
# get the logging interval in minutes
if args.hour is None:
    interval_minutes = args.minute
else:
    interval_minutes = int(args.hour * 60)

# initial averaging of weather data of the specified day to the specified interval
# get the filename and filepath of the raw log file based on the date from arguments
strDate = '{:02}'.format(month) + '{:02}'.format(day) + str(year)
filename = RAW_LOG_PREFIX + strDate + '.csv'
weather_logs_path = APP_DATA_PATH + WEATHER_LOGS_FOLDER
filepath = weather_logs_path + filename
# get the filename and filepath of the processed log file based on the date from arguments
processed_filepath = weather_logs_path + PROCESSED_LOG_PREFIX + strDate + '.csv'
# call a subprocess of the weatherlogaverage.py to average the weather data
if exists(filepath):
    proc1 = subprocess.Popen('python3 {}/weatherlogaverage.py -m {} -d {} -y {} --minute {}'
    .format(APP_PATH, month, day, year, interval_minutes), stdout=subprocess.PIPE, shell=True)
    output = proc1.communicate()[0]
    output = str(output, 'UTF-8')
    print(output)
else:
    print("file for specified date does not exist")
    exit()

# get the filename of the processed weather data file
# load the processed weather data CSV file into a numpy 2D string array
try:
    filearr = np.genfromtxt(processed_filepath, delimiter=',', dtype=str)
except:
    print("Read error")
    exit()
# get the CSV file header
header = filearr[0]
# remove 'Time' from the header array
header = header[1:]
# print(header)

# create date object from parameters
day = date(year, month, day)

# get the time array from filearr and convert it into datetime with the day
timeList = list(filearr[1:,0])
datetimeArr = np.array(list(datetime.combine(day, datetime.strptime(time,'%H:%M:%S').time()) for time in timeList))
# print(datetimeArr)
# print(datetimeArr.shape)

# get the log data arrays from filearr and format it as float64
dataArr = filearr[1:, 1:].astype(np.float64)
# print(dataArr)
# print(dataArr.shape)

# create results array
mean_std_min_max = np.zeros((4, len(header)), dtype=np.float64)
# get the mean, std, min, and max for each item in the header and save it to the results array
mean_std_min_max[0] = dataArr.mean(axis=0)
mean_std_min_max[1] = dataArr.std(axis=0)
mean_std_min_max[2] = dataArr.min(axis=0)
mean_std_min_max[3] = dataArr.max(axis=0)
# print(mean_std_min_max)

# Get the times when the weather data was at maximum values
# get the indices in the array where the data in each field is the highest
maxValIndices = np.where(dataArr == dataArr.max(axis=0))
# print(maxValIndices)
# depth stack the resulting arrays to form a 2D array with 1st degree elements with 0th element
# as value index and 1st element as datetime index
stackedMaxValIndices = np.dstack((maxValIndices[1], maxValIndices[0])).reshape(-1,2)
# print(stackedMaxValIndices)
# lexsort() generates an array of the indices of the sorted array. It is used for sorting an
# array according to a specific order of dimensions
# make the indices that indicate how maxValIndices should be sorted the index of stackedMaxValIndices
# to get the sorted max times index array
sorted_indices = np.lexsort((stackedMaxValIndices[:,1],stackedMaxValIndices[:,0]))
maxTimeIndices = stackedMaxValIndices[sorted_indices]
# print(maxTimeIndices)
# list of the times of maximum weather conditions
maxTimeList = []
# for each value column, get the times of the indices of the maximum values for each value
# column and append them to the ith sublist in the maxTimeList
for i in range(len(header)):
    indices = stackedMaxValIndices[stackedMaxValIndices[:,0] == i][:,1]
    # print(indices)
    times = datetimeArr[indices].tolist()
    maxTimeList.append(times)
# print(maxTimeList)

# Get the times when the weather data was at minimum values
#  get the indices in the array where the data in each field is the lowest
minValIndices = np.where(dataArr == dataArr.min(axis=0))
# print(minValIndices)
# depth stack the resulting arrays to form a 2D array with 1st degree elements with 0th element
# as value index and 1st element as datetime index
stackedMinValIndices = np.dstack((minValIndices[1], minValIndices[0])).reshape(-1,2)
# print(stackedMinValIndices)
# lexsort() generates an array of the indices of the sorted array. It is used for sorting an
# array according to a specific order of dimensions
# make the indices that indicate how minValIndices should be sorted the index of stackedMinValIndices
# to get the sorted min times index array
sorted_indices = np.lexsort((stackedMinValIndices[:,1], stackedMinValIndices[:,0]))
minTimeIndices = stackedMinValIndices[sorted_indices]
# print(minTimeIndices)
# list of the times of minimum weather conditions
minTimeList = []
# for each value column, get the times of the indices of the minimum values for each value
# column and append them to the ith sublist in the minTimeList
for i in range(len(header)):
    indices = minTimeIndices[minTimeIndices[:,0] == i][:,1]
    # print(indices)
    times = datetimeArr[indices].tolist()
    minTimeList.append(times)
# print(minTimeList)

# save the data as a dictionary for ease of data representation and saving to file
summary_dict = {}
for i in range(len(header)):
    sub_dict1 = {}
    sub_dict1['mean'] =  mean_std_min_max[0][i]
    sub_dict1['std'] =  mean_std_min_max[1][i]
    sub_dict1['min'] =  mean_std_min_max[2][i]
    sub_dict1['max'] =  mean_std_min_max[3][i]
    sub_dict1['min_times'] = minTimeList[i]
    sub_dict1['max_times'] = maxTimeList[i]
    summary_dict[header[i]] = sub_dict1
# print(summary_dict)

stats = ['mean', 'std', 'min', 'max']

# generate report file
report_filepath = APP_DATA_PATH + REPORTS_FOLDER + REPORT_PREFIX + day.strftime('%m%d%Y') + '.txt'
try:
    report_file = open(report_filepath, 'w')
except:
    print('Write error')

# save data to report file
str = 'Day: {}'.format(day.strftime('%m/%d/%Y'))
if DEBUG:
    print(str)
report_file.write(appendNewline(str))

# save the mean, standard deviation, minimum value, and maximum value of each value column
# to the report file
for column_name in summary_dict.keys():

    for st in stats:
        str = '{} {}: {:.3f}'.format(column_name, st, summary_dict[column_name][st])
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))
    if DEBUG:
        print()
    report_file.write('\n')

# save the times of the day with the minimum and maximum weather conditions to the report file
for column_name in summary_dict.keys():
    str = "Times of the day with minimum {}".format(column_name)
    if DEBUG:
        print(str)
    report_file.write(appendNewline(str))

    for time in summary_dict[column_name]['min_times']:
        str = time.strftime('%H:%M:%S')
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))

    str = "Times of the day with maximum {}".format(column_name)
    if DEBUG:
        print(str)
    report_file.write(appendNewline(str))

    for time in summary_dict[column_name]['max_times']:
        str = time.strftime('%H:%M:%S')
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))
    if DEBUG:
        print()
    report_file.write('\n')


if args.graph:
    print('Creating weather data graph')
    # Plotting the weather data into a graph
    # fonts
    suptitlefont = {'family':'monospace','color':'black'}
    titlefont = {'family':'monospace','color':'black','size':20}
    axisfont = {'family':'monospace','color':'black','size':15}

    # set the time format to HH:MM
    timeformat = mdates.DateFormatter('%H:%M')

    # set the subplots and figure size
    figure, axes = plt.subplots(3,1, figsize=(22, 15), sharex=True)

    # super title
    figure.suptitle('Weather Data for {}'.format(day.strftime('%m%d%Y')), fontdict=suptitlefont, fontsize=40)

    # subgraph for humidity
    axes[0].set_title('Relative Humidity over Time', fontdict=titlefont)
    axes[0].set_ylabel('Relative Humidity (%)', fontdict=axisfont)
    axes[0].plot(datetimeArr, dataArr[:,0], linestyle='-', color='slateblue', linewidth=2)

    # subgraph for barometric pressure
    axes[1].set_title('Barometric Pressure over Time', fontdict=titlefont)
    axes[1].set_ylabel('Barometric Pressure (Pa)', fontdict=axisfont)
    axes[1].plot(datetimeArr, dataArr[:,3], linestyle='-', color='seagreen', linewidth=2)

    # subgraph for both temperature sensors
    axes[2].set_title('Temperature over Time', fontdict=titlefont)
    axes[2].set_ylabel('Temperature (°C)', fontdict=axisfont)
    axes[2].plot(datetimeArr, dataArr[:,1], label='DHT11_Temperature', linestyle='-', color='red', linewidth=2)
    axes[2].legend(fontsize=20)
    axes[2].plot(datetimeArr, dataArr[:,2], label='BMP180_temperature', linestyle='-', color='magenta', linewidth=2)
    axes[2].legend()

    # set tick font size and rotation for all subplots
    for axis in axes:
        axis.tick_params(labelsize=18)
        axis.tick_params(axis='x',labelrotation=30)

    # specify time format of x-axis
    for axis in axes:
        axis.xaxis.set_major_formatter(timeformat)
        axis.xaxis_date()

    # adjust subplots to make room for the supertitle
    figure.subplots_adjust(top=0.92)
    # save the graph to a file
    plt.savefig(APP_DATA_PATH + PLOTS_FOLDER + PLOT_PREFIX + '{}.png'.format(day.strftime('%m%d%Y')),
    dpi=200, bbox_inches='tight')

# open a new file to save the summarized data
summary_filename = SUMMARY_PREFIX + day.strftime('%m%d%Y') + '.txt'
print(summary_filename)
summary_filepath = APP_DATA_PATH + SUMMARIES_FOLDER + summary_filename
try:
    summary_file = open(summary_filepath, 'w')
except:
    print('Write error')

# save data to output file
# write mean, std, min, max, min times, and max times for each value column from the dictionary
for column_name in summary_dict.keys():
    str1 = column_name + ':'
    str1 += '{:.3f}'.format(summary_dict[column_name]['mean']) + ','
    str1 += '{:.3f}'.format(summary_dict[column_name]['std']) + ','
    str1 += '{:.3f}'.format(summary_dict[column_name]['min']) + ','
    str1 += '{:.3f}'.format(summary_dict[column_name]['max']) + ','

    str1 += '['
    for date in summary_dict[column_name]['min_times']:
        str1 += date.strftime('%H:%M:%S') + ','
    str1 += ']'

    str1 += '['
    for date in summary_dict[column_name]['max_times']:
        str1 += date.strftime('%H:%M:%S') + ','
    str1 += ']\n'
    # print(str1)
    summary_file.write(str1)

summary_file.close()
