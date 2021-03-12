#!/usr/bin/python3

import os
import subprocess
import re
from datetime import timedelta, date, time, datetime
import csv
from config import APP_PATH, APP_DATA_PATH, WEATHER_LOGS_FOLDER, RAW_LOG_PREFIX

# This Python script averages all raw sensor data in the logging directory to a specified interval,
# default 1 minute. It overwrites raw data with its average, and ignores data that is already averaged.

DEBUG = False

# averaging interval in minutes
INTERVAL = 1

# subtracts two datetime.time objects, assuming they are from the same day
# returns time1 - time2
def subtract_time(time1, time2):
    return (datetime.combine(date.min, time1) - datetime.combine(date.min, time2))

today = datetime.now().date()

# get the list of files in the weather log dir and sort it
filenames = os.listdir(APP_DATA_PATH + WEATHER_LOGS_FOLDER)
filenames.sort()

for filename in filenames:
    # get files starting with "weather_log"
    if re.search("^" + RAW_LOG_PREFIX, filename) is not None:
        # get the date of the log
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        # check all weather logs except the log in progress for today
        if date1 < today:
            if DEBUG:
                print(filename + " " + re.search("\d{8}", filename).group())
            # get the year, month, and day to pass as parameters
            year = date1.year
            month = date1.month
            day = date1.day

            # open file to check the time intervals
            raw_file = open(APP_DATA_PATH + WEATHER_LOGS_FOLDER + filename, 'r')
            raw_file_reader = csv.reader(raw_file, delimiter=',')
            # skip the header
            next(raw_file_reader);

            # check if the data is raw or has been previously averaged by checking the difference
            # in time per reading.
            times = []
            # get the first 3 times of the data
            for i in range(3):
                row = next(raw_file_reader)
                times.append(datetime.strptime(row[0], "%H:%M:%S").time())

            # If it is not exactly 1 minute, call the process to overwrite it with its average.
            if subtract_time(times[1], times[0]).seconds < INTERVAL * 60 and \
            subtract_time(times[2], times[1]).seconds < INTERVAL * 60:
                if DEBUG:
                    print("RAW")
                proc1 = subprocess.Popen('python3 {}/weatherlogaverage.py -m {} -d {} -y {} -o'
                .format(APP_PATH, month, day, year), stdout=subprocess.PIPE, shell=True)
                output = proc1.communicate()[0]
                output = str(output, 'UTF-8')
                print(output)
