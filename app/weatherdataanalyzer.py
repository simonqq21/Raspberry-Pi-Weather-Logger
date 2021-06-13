#!/usr/bin/python3

import numpy as np
import pandas as pd
import os
import csv
from datetime import datetime, date, time
import argparse
import subprocess
from config import APP_PATH, APP_DATA_PATH, REPORTS_FOLDER, PLOTS_FOLDER, PLOT_PREFIX, REPORT_PREFIX
from config import HEADER, STATS
from config import DEBUG
from config import logging_interval
from functions import exists, appendNewline
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather

# set float print precision
np.set_printoptions(precision=3, suppress=True)

'''
This program takes optional year, month, day, and interval as parameters.
This program calls the datalog averager program to process the raw datalog file, then computes
for the mean, standard deviation, maximum value and minimum value for temperature, pressure,
and humidity of a particular day. The data will be graphed and saved as an image file.
'''

# parse arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument('-m', help='numeric month from 1-12', default=date.today().month, type=int)
parser.add_argument('-d', help='numeric day from 1-31', default=date.today().day, type=int)
parser.add_argument('-y', help='numeric four digit year', default=date.today().year, type=int)
parser.add_argument('-g', '--graph', help='graph the data and save it to an image file if specified', action='store_true')
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

print('i')

# save the data as a dictionary for ease of data representation and saving to file
min_max_times_dict = {}
for k in HEADER.keys():
    min_max_times_dict[k] = {}
# Get the times when the weather data was at maximum and minimum values
print('min and max datetimes')
for k in HEADER.keys():
    print(f"max {k} = {max[k]}")
    min_max_times_dict[k]['max_times'] = weather_df['datetime'][weather_df[k] == max[k]]
    # print(weather_df['datetime'][weather_df[k] == max[k]])
print('\n')
print('min datetimes')
for k in HEADER.keys():
    print(f"min {k} = {min[k]}")
    min_max_times_dict[k]['min_times'] = weather_df['datetime'][weather_df[k] == min[k]]
print('\n')

print(min_max_times_dict)

#
# weather_df
# results_df
# min_max_times_dict

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
for k in HEADER.keys():
    for st in STATS:
        str = '{} {}: {:.3f}'.format(k, st, results_df[st][k])
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))
    if DEBUG:
        print()
    report_file.write('\n')

# save the times of the day with the minimum and maximum weather conditions to the report file
for k in HEADER.keys():
    str = "Times of the day with minimum {}".format(k)
    if DEBUG:
        print(str)
    report_file.write(appendNewline(str))
    for time in min_max_times_dict[k]['min_times']:
        str = time.strftime('%H:%M:%S')
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))

    str = "Times of the day with maximum {}".format(k)
    if DEBUG:
        print(str)
    report_file.write(appendNewline(str))

    for time in min_max_times_dict[k]['max_times']:
        str = time.strftime('%H:%M:%S')
        if DEBUG:
            print(str)
        report_file.write(appendNewline(str))
    if DEBUG:
        print()
    report_file.write('\n')


if args.graph:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib
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
    axes[0].plot(dataDict['datetime'], dataDict['dhthumd'], linestyle='-', color='slateblue', linewidth=2)

    # subgraph for barometric pressure
    axes[1].set_title('Barometric Pressure over Time', fontdict=titlefont)
    axes[1].set_ylabel('Barometric Pressure (Pa)', fontdict=axisfont)
    axes[1].plot(dataDict['datetime'], dataDict['bmppres'], linestyle='-', color='seagreen', linewidth=2)

    # subgraph for both temperature sensors
    axes[2].set_title('Temperature over Time', fontdict=titlefont)
    axes[2].set_ylabel('Temperature (°C)', fontdict=axisfont)
    axes[2].plot(dataDict['datetime'], dataDict['dhttemp'], label='DHT11_Temperature', linestyle='-', color='red', linewidth=2)
    axes[2].legend(fontsize=20)
    axes[2].plot(dataDict['datetime'], dataDict['bmptemp'], label='BMP180_temperature', linestyle='-', color='magenta', linewidth=2)
    axes[2].legend()

    # set tick font size and rotation for all subplots
    for axis in axes:
        axis.tick_params(labelsize=18)
        axis.tick_params(axis='x',labelrotation=30)
        # specify time format of x-axis
        axis.xaxis.set_major_formatter(timeformat)
        axis.xaxis_date()

    # adjust subplots to make room for the supertitle
    figure.subplots_adjust(top=0.92)
    # save the graph to a file
    plt.savefig(APP_DATA_PATH + PLOTS_FOLDER + PLOT_PREFIX + '{}.png'.format(day.strftime('%m%d%Y')),
    dpi=200, bbox_inches='tight')
