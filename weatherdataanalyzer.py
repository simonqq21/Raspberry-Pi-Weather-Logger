#!/usr/bin/python3

import numpy as np
import matplotlib as plt
import os
from datetime import datetime, date, time, timedelta
import argparse
import subprocess

# set float print precision
np.set_printoptions(precision=3, suppress=True)
'''
This program takes optional year, month, day, and interval as parameters.
This program calls the datalog averager program to process the raw datalog file, then computes
for the mean, standard deviation, maximum value and minimum value for temperature, pressure,
and humidity of a particular day. The data will be graphed and saved as an image file.
'''

# file path and filename for weather logs
script_path = os.path.abspath(os.path.dirname(__file__))
path = script_path + '/weather_logs/'
filenameprefix = "weather_log"

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        return 0
    f.close()
    return 1

# parse arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument('-m', help='numeric month from 1-12', default=date.today().month, type=int)
parser.add_argument('-d', help='numeric day from 1-31', default=date.today().day, type=int)
parser.add_argument('-y', help='numeric four digit year', default=date.today().year, type=int)
group2 = parser.add_mutually_exclusive_group()
group2.add_argument('-hr', '--hour', help='The new log interval in hours', type=float)
group2.add_argument('-min', '--minute', help='The new log interval in minutes. Default value is 1 minute',
type=int, default=1)
args = parser.parse_args()

# saving parameters to variables
month = args.m
day = args.d
year = args.y
# get the logging interval in minutes
if args.hour is None:
    interval_minutes = args.minute
else:
    interval_minutes = args.hour * 60

# initial averaging of weather data of the specified day to the specified interval
# get the filename and filepath of the raw log file based on the date from arguments
filename = (filenameprefix + '{:02}'.format(month) + '{:02}'.format(day) + str(year) + '.csv')
filepath = path + filename
# get the filename and filepath of the processed log file based on the date from arguments
processed_filename = 'processed_' + filename
processed_filepath = path + processed_filename
# call a subprocess of the weatherlogaverage.py to average the weather data
if exists(filepath):
    proc1 = subprocess.Popen('python3 {}/weatherlogaverage.py -m {} -d {} -y {} --minute {}'
    .format(script_path, month, day, year, interval_minutes), stdout=subprocess.PIPE, shell=True)
    output = proc1.communicate()[0]
    output = str(output, 'UTF-8')
    print(output)
else:
    print("file for specified date does not exist")
    exit()

# get the filename of the processed weather data file
# load the processed weather data CSV file into a numpy 2D string array
filearr = np.genfromtxt(processed_filepath, delimiter=',', dtype=str)
# get the CSV file header
header = filearr[0]
# remove 'Time' from the header array
header = header[1:]
# print(header)

# create date object from parameters
day = date(year, month, day)
# print(day)

# get the time array from filearr and convert it into datetime with the day
timeList = list(filearr[1:,0])
datetimeArr = np.array(list(datetime.combine(day, datetime.strptime(time,'%H:%M:%S').time()) for time in timeList))
# print(datetimeArr)
# print(datetimeArr.shape)

# get the log data arrays from filearr and format it as float64
dataArr = filearr[1:, 1:].astype(np.float64)
# print(dataArr)
# print(dataArr.shape)

# create empty results array
mean_std_min_max = np.zeros((4, len(header)), dtype=np.float64)
# get the mean, std, min, and max for each item in the header and save it to an array
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
# to get the sorted max date index array
maxDateIndices = np.lexsort((stackedMaxValIndices[:,1],stackedMaxValIndices[:,0]))
maxDateIndices = stackedMaxValIndices[maxDateIndices]
# print(maxDateIndices)
# list of the dates of maximum weather conditions
maxDateList = []
# for each value column
for i in range(len(header)):
    # get the dates of the indices of the maximum values for each value column and append
    # them to the ith sublist in the maxDateList
    indices = stackedMaxValIndices[stackedMaxValIndices[:,0] == i][:,1]
    # print(indices)
    times = datetimeArr[indices].tolist()
    maxDateList.append(times)
# print(maxDateList)

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
# to get the sorted min date index array
minDateIndices = np.lexsort((stackedMinValIndices[:,1], stackedMinValIndices[:,0]))
minDateIndices = stackedMinValIndices[minDateIndices]
print(minDateIndices)
# list of the dates of minimum weather conditions
minDateList = []
# for each value column
for i in range(len(header)):
    # get the dates of the indices of the minimum values for each value column and append
    # them to the ith sublist in the minDateList
    indices = minDateIndices[minDateIndices[:,0] == i][:,1]
    # print(indices)
    times = datetimeArr[indices].tolist()
    minDateList.append(times)
# print(minDateList)

# print the mean, standard deviation, minimum value, and maximum value of each value column
for i in range(len(header)):
    print('{} mean: {:.3f}'.format(header[i], mean_std_min_max[0,i]))
    print('{} std: {:.3f}'.format(header[i], mean_std_min_max[1,i]))
    print('{} min: {:.3f}'.format(header[i], mean_std_min_max[2,i]))
    print('{} max: {:.3f}'.format(header[i], mean_std_min_max[3,i]))
    print()

# print the times of the day with the minimum and maximum weather conditions
print('day: {}'.format(day.strftime('%m/%d/%Y')))
for i in range(len(header)):
    print("Times of the day with minimum {}".format(header[i]))
    for d in minDateList[i]:
        print(d.strftime('%H:%M:%S'))

    print("Times of the day with maximum {}".format(header[i]))
    for d in maxDateList[i]:
        print(d.strftime('%H:%M:%S'))
    print()
