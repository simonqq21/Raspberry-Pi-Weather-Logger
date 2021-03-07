#!/usr/bin/python3

import os
import csv
from datetime import datetime, date, time, timedelta
import argparse

'''
This script converts a raw CSV file from the logger into a new CSV file with
a different measuring interval.
eg. convert the RAW CSV script from the Pi logger into weather data logged every
5 minutes
Usage: python3 weatherlogreader.py -m <month> -d <day> -y <year> (-m <minutes> | -h <hours>)
The default interval is 1 minute.
'''

# file path and filename for weather logs
path = os.path.abspath(os.path.dirname(__file__)) + '/weather_logs/'
filenameprefix = "weather_log"

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        return 0
    f.close()
    return 1

# subtracts two datetime.time objects, assuming they are from the same day
# returns time1 - time2
def subtract_time(time1, time2):
    return (datetime.combine(date.min, time1) - datetime.combine(date.min, time2))

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

# get the new logging interval_minutes in minutes
if args.hour is None:
    interval_minutes = args.minute
else:
    interval_minutes = args.hour * 60

# get the log file name from the date specified and open it
filename = (filenameprefix + '{:02}'.format(args.m) + '{:02}'.format(args.d)
+ str(args.y) + '.csv')
print(filename)
filepath = path + filename
# if exists(filepath):
file = open(filepath, 'r', newline='')
filereader = csv.reader(file, delimiter=',')
# else:
#     print("file does not exist")
#     exit()

# copy all records from the input file into memory
records = []
header = next(filereader)
for row in filereader:
    records.append(row)
print("done")
file.close()

# commenting this will overwrite the raw log file
filename = ('processed_' + filenameprefix + '{:02}'.format(args.m) + '{:02}'.format(args.d)
+ str(args.y) + '.csv')
print(filename)
filepath = path + filename

# overwrite the file
try:
    file = open(filepath, 'w')
    filewriter = csv.writer(file, delimiter=',')
    # write the csv file header to the output file
    filewriter.writerow(header)
except IOError:
    print("Write error")
    exit()

# initialize variables
outputTime = time(0,0,0)
inputTime = time(0,0,0)
temperature, humidity, bmp_temperature, pressure = 0, 0, 0, 0
n = 0

for row in records:
    # get the time of each row
    hms  = row[0].split(':')

    # save the time as a time object
    hms = [int(n) for n in hms]
    inputTime = time(hms[0], hms[1], hms[2])

    # get the sum of the data
    humidity += float(row[1])
    temperature += float(row[2])
    bmp_temperature += float(row[3])
    pressure += float(row[4])
    n += 1

    # log the mean of the data for every division
    if subtract_time(inputTime, outputTime).seconds >= interval_minutes * 60:
        # get the average
        temperature /= n
        humidity /= n
        bmp_temperature /= n
        pressure /= n
        # write the data to the csv file
        filewriter.writerow([outputTime, '{:.3f}'.format(humidity),
        '{:.3f}'.format(temperature),
        '{:.3f}'.format(bmp_temperature),
        '{:.3f}'.format(pressure)])
        outputTime = inputTime
        outputTime = outputTime.replace(second=0)
        # reset the average
        temperature, humidity, bmp_temperature, pressure = 0, 0, 0, 0
        n = 0

# average the remaining values
if n > 0:
    temperature /= n
    humidity /= n
    bmp_temperature /= n
    pressure /= n
    filewriter.writerow([outputTime, '{:.3f}'.format(humidity),
    '{:.3f}'.format(temperature),
    '{:.3f}'.format(bmp_temperature),
    '{:.3f}'.format(pressure)])

file.close()
