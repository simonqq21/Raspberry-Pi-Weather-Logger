#!/usr/bin/python3

import numpy as np
import pandas as pd
import os
import csv
from datetime import datetime, date, time
import argparse
import subprocess
from config import APP_PATH, APP_DATA_PATH
from config import HEADER, STATS
from config import DEBUG
from config import logging_interval
from config import FILENAME_DATEFORMAT
from functions import exists, nl
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather

# set float print precision
np.set_printoptions(precision=3, suppress=True)

'''
This program takes optional year, month, day, and interval as parameters.
This program computes for the mean, standard deviation, maximum value and minimum value for temperature, pressure,
and humidity of a particular day.
This program is not meant to be run standalone unless during testing. It is called by the process_incomplete_reports.py file
iteratively to generate aggregate data, reports, and plots for the past days.
'''

# parse arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument('-m', help='numeric month from 1-12', default=date.today().month, type=int)
parser.add_argument('-d', help='numeric day from 1-31', default=date.today().day, type=int)
parser.add_argument('-y', help='numeric four digit year', default=date.today().year, type=int)
args = parser.parse_args()

# create date object from parameters
month = args.m
day = args.d
year = args.y
day = date(year, month, day)

dataDict = {}
dataDict['datetime'] = []
for k in HEADER.keys():
    dataDict[k] = []

# load the data from the db
weather_logs = WeatherLog.selectMultiple(date1=day)
# exit if no data exists
if len(weather_logs) == 0:
	print('no records, exiting')
	exit(0)

for w in weather_logs:
    dataDict['datetime'].append(w.datetime.datetime)
    for k in HEADER.keys():
        dataDict[k].append(w.log[k].value)

# weather data DataFrame
weather_df = pd.DataFrame(data=dataDict)
print(weather_df)
# print(weather_df.dtypes)
# print(weather_df.columns[1:5])
# print(weather_df.info())
# print(weather_df.loc[1])

# create results dataframe
# get the mean, std, min, and max for each item in the header and save it to the results dataframe
mean = weather_df.mean(numeric_only=True)
std = weather_df.std(numeric_only=True)
min = weather_df.min(numeric_only=True)
max = weather_df.max(numeric_only=True)
# print(mean)
# print(std)
# print(min)
# print(max)
results_df = pd.concat([mean, std, min, max], axis=1)
results_df.columns = STATS
print(day)
print(results_df)
# results_df.to_csv('testresult.csv')
print('\n')

# insert aggregated data for the day into the database
aggdayweather = AggDayWeather.select(day)
print(aggdayweather)
if aggdayweather is not None:
    aggdayweather.delete()
daterow = DateRow(date=day)
aggdata = {'aggdhttemp': AggDHTTemperature(mean=results_df['mean']['dhttemp'], \
    std=results_df['std']['dhttemp'], min=results_df['min']['dhttemp'], \
    max=results_df['max']['dhttemp']), \
    'aggdhthumd': AggDHTHumidity(mean=results_df['mean']['dhthumd'], \
    std=results_df['std']['dhthumd'], min=results_df['min']['dhthumd'], \
    max=results_df['max']['dhthumd']),
    'aggbmptemp': AggBMPTemperature(mean=results_df['mean']['bmptemp'], \
    std=results_df['std']['bmptemp'], min=results_df['min']['bmptemp'], \
    max=results_df['max']['bmptemp']),
    'aggbmppres': AggBMPPressure(mean=results_df['mean']['bmppres'], \
    std=results_df['std']['bmppres'], min=results_df['min']['bmppres'], \
                                        max=results_df['max']['bmppres'])}
aggdayweather = AggDayWeather(daterow, aggdata)
aggdayweather.insert()
