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

# obtain and parse arguments from the command line
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
# get the logging in minutes
if args.hour is None:
    interval_minutes = args.minute
else:
    interval_minutes = args.hour * 60

# initial averaging of weather data of the specified day to the specified interval
# call a subprocess of the weatherlogaverage.py to average the weather data
filename = (filenameprefix + '{:02}'.format(month) + '{:02}'.format(day) + str(year) + '.csv')
filepath = path + filename
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
filename = 'processed_' + filename
filepath = path + filename
# load the processed weather data CSV file into a numpy 2D array
filearr = np.genfromtxt(filepath, delimiter=',', dtype=str)
# get the header
header = filearr[0]
header = header[1:]
# print(header)

day = date(year, month, day)
print(day)

# get the time array from filearr
timeList = list(filearr[1:,0])
datetimeList = list(datetime.combine(day, datetime.strptime(time,'%H:%M:%S').time()) for time in timeList)
datetimeArr = np.array(datetimeList, dtype=np.datetime64)
# print(datetimeArr)
# print(datetimeArr.shape)

# get the data arrays from filearr and format it as np.float64
dataArr = filearr[1:, 1:].astype(np.float64)
# print(dataArr)
# print(dataArr.shape)

# create datatype definition for results structured array
Dtype = [('data', 'U16')]
Dtype.append(('mean', np.float64))
Dtype.append(('std', np.float64))
Dtype.append(('min', np.float64))
Dtype.append(('max', np.float64))
# Dtype.append(('time_of_min', np.datetime64))
# Dtype.append(('time_of_max', np.datetime64))

# create empty results array
resulting_values = np.array(np.zeros([len(header)]), dtype=Dtype)
# getting the mean, std, min, and max for each item in the header
resulting_values['data'] = header
resulting_values['mean'] = dataArr.mean(axis=0)
resulting_values['std'] = dataArr.std(axis=0)
resulting_values['min'] = dataArr.min(axis=0)
resulting_values['max'] = dataArr.max(axis=0)
# resulting_values['time_of_min'] = dataArr[np.where(dataArr[:] == resulting_values['max'])]
# resulting_values['time_of_max'] = dataArr[np.where(dataArr[:] == resulting_values['max'])]
print(resulting_values)
# print(dataArr)
# print(dataArr.shape)
# print(dataArr.max(axis=0))
# print(resulting_values[:]['max'])
# get the indices in the array where humidity is the highest
# print(np.where(dataArr[:,0] == resulting_values[0]['max'])[0])
# print(np.where(dataArr[:,1] == resulting_values[1]['max'])[0])
# print(np.where(dataArr[:,2] == resulting_values[2]['max'])[0])
# print(np.where(dataArr[:,3] == resulting_values[3]['max'])[0])


maxWhere = np.where(dataArr == resulting_values['max'])
maxDateIndices = np.sort(np.dstack((maxWhere[1], maxWhere[0])).reshape(-1,2), axis=0)
minWhere = np.where(dataArr == resulting_values['min'])
minDateIndices = np.sort(np.dstack((minWhere[1], minWhere[0])).reshape(-1,2), axis=0)
print(maxDateIndices)
print(minDateIndices)

# print(np.where(dataArr == resulting_values[:]['max']))

# print the results to terminal
for result in resulting_values:
    print('{} mean: {:.3f}'.format(result['data'], result['mean']))
    print('{} std: {:.3f}'.format(result['data'], result['std']))
    print('{} min: {:.3f}'.format(result['data'], result['min']))
    print('{} max: {:.3f}'.format(result['data'], result['max']))
    print()


# get the time of the day with the minimum and maximum weather conditions
'''
time of minimum temperature:
time of maximum temperature:
'''

    # for value in result:
        # print(value)

# print(dataArr[:,0].mean())
# print(dataArr.mean(axis=0))
