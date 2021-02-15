#!/usr/bin/python3

import numpy as np
import matplotlib as plt
import os
from datetime import datetime, date, time, timedelta
import argparse
import csv
import subprocess

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
# get the new logging interval_minutes in minutes
if args.hour is None:
    interval_minutes = args.minute
else:
    interval_minutes = args.hour * 60

filename = (filenameprefix + '{:02}'.format(month) + '{:02}'.format(day) + str(year) + '.csv')
filepath = path + filename
# call a subprocess of the weather log averager to average the
if exists(filepath):
    proc1 = subprocess.Popen('python3 {}/weatherlogaverage.py -m {} -d {} -y {} --minute {}'
    .format(script_path, month, day, year, interval_minutes), stdout=subprocess.PIPE, shell=True)
    output = proc1.communicate()[0]
    output = str(output, 'UTF-8')
    print(output)
else:
    print("file for specified date does not exist")
    exit()
