#!/usr/bin/python3

import csv
from datetime import datetime, date, time, timedelta
import argparse

'''
This script converts a raw CSV file from the logger into a new CSV file with
a different measuring interval.
eg. convert the RAW CSV script from the Pi logger into weather data logged every
5 minutes
Usage: python3 weatherlogreader.py <date> (-m <minutes> | -h <hours>)
'''

# file path and filename for weather logs
path = 'weather_logs/'
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
inputfilename = (filenameprefix + '{:02}'.format(args.m) + '{:02}'.format(args.d)
+ str(args.y) + '.csv')
print(inputfilename)
inputfilepath = path + inputfilename
if exists(inputfilepath):
    inputfile = open(inputfilepath, 'r', newline='')
    inputfilereader = csv.reader(inputfile, delimiter=',')
else:
    print("file does not exist")
    exit()

# open a new file where the output will be saved
outputfilename = 'c_' + inputfilename
outputfilepath = path + outputfilename
try:
    outputfile = open(outputfilepath, 'w')
    outputfilewriter = csv.writer(outputfile, delimiter=',')
    # write the csv file header to the output file
    outputfilewriter.writerow(next(inputfilereader))
    outputfile.close()
except IOError:
    print("Write error")
    exit()

# initialize variables
outputTime = time(0,0,0)
inputTime = time(0,0,0)
temperature, humidity, bmp_temperature, pressure = 0, 0, 0, 0
n = 0

for row in inputfilereader:
    # get the time of each row
    hms  = row[0].split(':')

    # save the time as a time object
    if len(hms) == 3:
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
        outputfile = open(outputfilepath, 'a')
        outputfilewriter = csv.writer(outputfile, delimiter=',')
        outputfilewriter.writerow([outputTime, '{:.3f}'.format(humidity),
        '{:.3f}'.format(temperature),
        '{:.3f}'.format(bmp_temperature),
        '{:.3f}'.format(pressure)])
        outputfile.close()
        outputTime = inputTime
        outputTime = outputTime.replace(second=0)
        # reset the average
        temperature, humidity, bmp_temperature, pressure = 0, 0, 0, 0
        n = 0
