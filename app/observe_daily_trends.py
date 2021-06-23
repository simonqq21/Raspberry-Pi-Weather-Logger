'''
save aggregated data for the date range in a report file

Things to determine per weather data column:
mean value
lowest mean value
highest mean value
lowest value 
highest value 
days with the lowest mean value
days with the highest mean value
days with the lowest value 
days with the highest value 

output data:
- date range (start and end date)
- overall mean value of the means per column
- overall min value of the means per column
- overall max value of the means per column
- overall min value of the min values per column
- overall max value of the max values per column
- array of days with the lowest mean value per column
- array of days with the highest mean value per column
- array of days with the lowest minimum value per column
- array of days with the highest maximum value per column
image plot of mean, std, min, and max per column per day, if graph is enabled
'''

import numpy as np
import pandas as pd
import argparse
import os
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME
from config import WEATHER_DATA_LIST, STATS, UNITS, TABLE_ABBREVS
from config import DAILY_TRENDS_PREFIX
from config import EXPORTEDS_FOLDER, FILENAME_DATEFORMAT
from functions import deleteAllSimilar, nl
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
from db_module import getAllAggDates

# set float print precision
np.set_printoptions(precision=3, suppress=True)

#get the minimum and maximum dates of aggregated weather data in the db 
datesList = getAllAggDates()
if len(datesList) == 0:
	print('no records, exiting')
	exit(0)
mindate = min(datesList)
maxdate = max(datesList)

# date1, date2, and graph arguments
parser = argparse.ArgumentParser()
date1 = parser.add_argument_group('date1')
date2 = parser.add_argument_group('date2')
date1.add_argument('-y1', '--startyear', type=int, default=mindate.year, help='year of starting date')
date1.add_argument('-m1', '--startmonth', type=int, default=mindate.month, help='month of starting date')
date1.add_argument('-d1', '--startday', type=int, default=mindate.day, help='day of starting date')
date2.add_argument('-y2', '--endyear', type=int, default=maxdate.year, help='year of ending date')
date2.add_argument('-m2', '--endmonth', type=int, default=maxdate.month, help='month of ending date')
date2.add_argument('-d2', '--endday', type=int, default=maxdate.day, help='day of ending date')
parser.add_argument('-g', '--graph', help="graph the data and save it to an image file if \
specified", action='store_true')
args = parser.parse_args()
# print(args)

startdate = date(args.startyear, args.startmonth, args.startday)
enddate = date(args.endyear, args.endmonth, args.endday)

startdatestr = startdate.strftime(FILENAME_DATEFORMAT)
enddatestr = enddate.strftime(FILENAME_DATEFORMAT)

# connect to db using sqlalchemy
# read the daily aggregated data between the two dates from the db
results = AggDayWeather.selectMultiple(startdate, enddate)
# ~ print(results)
print(len(results))
if len(results) == 0:
	print('no records, exiting')
	exit(0)

'''
expected dataframe output
date, WEATHER_DATA_LIST, agg, value
6/13/2021, dhttemp, mean, 29
6/13/2021, dhttemp, std, 0.1
6/13/2021, dhttemp, min, 28
6/13/2021, dhttemp, max, 30
'''
# create dictionary to create the dataframe that represents each table from the db
dataDict = {}
dataDict['date'] = []
dataDict['WEATHER_DATA_LIST'] = [] # dhttemp, dhthumd, bmptemp, or bmppres
dataDict['stat_type'] = [] # mean, std, min, max
dataDict['value'] = []
if results is not None:
	for result in results:
		for t in TABLE_ABBREVS:
			for s in STATS:
				dataDict['date'].append(result.daterow.date)
				dataDict['WEATHER_DATA_LIST'].append(t)
				dataDict['stat_type'].append(s)
				if s == 'mean':
					dataDict['value'].append(result.aggdata['agg'+t].mean)
				elif s == 'std':
					dataDict['value'].append(result.aggdata['agg'+t].std)
				elif s == 'min':
					dataDict['value'].append(result.aggdata['agg'+t].min)
				elif s == 'max':
					dataDict['value'].append(result.aggdata['agg'+t].max)
		
# save overall results to pd dataframe
aggdata_tb = pd.DataFrame(data=dataDict)
# ~ print(aggdata_tb)
# pivot the dataframe to represent each date as one row
pivoted_aggdata_df = pd.pivot_table(aggdata_tb, values='value', index='date', columns=['WEATHER_DATA_LIST', 'stat_type'])
# ~ print(pivoted_aggdata_df)

# delete any existing daily trends csv file before generating new csv file
# ~ deleteAllSimilar(APP_DATA_PATH, DAILY_TRENDS_PREFIX)

# save the database results as a csv file for download
# ~ pivoted_aggdata_df.to_csv('pivoted_aggdata.csv')

# get the mean, std, min, and max of each data column
aggdata_overall = {}
for t in TABLE_ABBREVS:
	aggdata_overall[t] = {}
	aggdata_overall[t]['mean_mean'] = pivoted_aggdata_df[t]['mean'].mean()
	aggdata_overall[t]['min_mean'] = pivoted_aggdata_df[t]['mean'].min()
	aggdata_overall[t]['max_mean'] = pivoted_aggdata_df[t]['mean'].max()
	aggdata_overall[t]['min_min'] = pivoted_aggdata_df[t]['min'].min()
	aggdata_overall[t]['max_max'] = pivoted_aggdata_df[t]['max'].max()
	aggdata_overall[t]['min_mean_days'] = \
		pivoted_aggdata_df.index[pivoted_aggdata_df[t]['mean'] == \
		pivoted_aggdata_df[t]['mean'].min()].values
	aggdata_overall[t]['max_mean_days'] = \
		pivoted_aggdata_df.index[pivoted_aggdata_df[t]['mean'] == \
		pivoted_aggdata_df[t]['mean'].max()].values
	aggdata_overall[t]['min_min_days'] = \
		pivoted_aggdata_df.index[pivoted_aggdata_df[t]['min'] == \
		pivoted_aggdata_df[t]['min'].min()].values
	aggdata_overall[t]['max_max_days'] = \
		pivoted_aggdata_df.index[pivoted_aggdata_df[t]['max'] == \
		pivoted_aggdata_df[t]['max'].max()].values
# ~ print(aggdata_overall)

# generate the daily trends report text file
with open(APP_DATA_PATH + EXPORTEDS_FOLDER + DAILY_TRENDS_PREFIX + '{}_{}.txt'.format(startdatestr, enddatestr), 'w') as file:
    file.write(nl('---------- Weather Data Daily Trends Report ----------'))
    file.write(nl('start date: {}'.format(startdatestr)))
    file.write(nl('end date: {}'.format(enddatestr)))
    file.write(nl(''))
    for t in TABLE_ABBREVS:
        file.write(nl('{} mean_mean: {:.3f}'.format(t, aggdata_overall[t]['mean_mean'])))
        file.write(nl('{} min_mean: {:.3f}'.format(t, aggdata_overall[t]['min_mean'])))
        file.write(nl('{} min_mean_days: {}'.format(t, aggdata_overall[t]['min_mean_days'])))
        file.write(nl('{} max_mean: {:.3f}'.format(t, aggdata_overall[t]['max_mean'])))
        file.write(nl('{} max_mean_days: {}'.format(t, aggdata_overall[t]['max_mean_days'])))
        file.write(nl('{} min_min: {:.3f}'.format(t, aggdata_overall[t]['min_min'])))
        file.write(nl('{} min_min_days: {}'.format(t, aggdata_overall[t]['min_min_days'])))
        file.write(nl('{} max_max: {:.3f}'.format(t, aggdata_overall[t]['max_max'])))
        file.write(nl('{} max_max_days: {}'.format(t, aggdata_overall[t]['max_max_days'])))
        file.write(nl(''))
    file.write(nl(''))

# generate graph if graph option is set
if args.graph:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib

    # fonts
    suptitlefont = {'family':'monospace','color':'black'}
    titlefont = {'family':'monospace','color':'black','size':20}
    axisfont = {'family':'monospace','color':'black','size':20}
    plt.rc('legend', fontsize=20)

    # set the time format to HH:MM
    timeformat = mdates.DateFormatter('%Y/%m/%d')
    # one major x tick per day
    fmt_day = mdates.DayLocator()

    # set the subplots and figure size
    figure, axes = plt.subplots(4,1, figsize=(22, 15), sharex=True)
    
    # super title
    figure.suptitle('Weather Data Trends from {} to {}'.format(startdate.strftime(FILENAME_DATEFORMAT), \
    enddate.strftime(FILENAME_DATEFORMAT)), fontdict=suptitlefont, fontsize=40)

    # subgraph for temperature
    dhttempgraph = axes[0]
    dhttempgraph.set_title(WEATHER_DATA_LIST[0], fontdict=titlefont)
    dhttempgraph.set_ylabel(WEATHER_DATA_LIST[0], fontdict=axisfont)
    dhttempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhttemp']['mean'], label="temperature_mean", linestyle='-', color='#cd3299', linewidth=4)
    dhttempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhttemp']['min'], label="temperature_min", linestyle='-', color='#90236b', linewidth=4)
    dhttempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhttemp']['max'], label="temperature_max", linestyle='-', color='#ebadd6', linewidth=4)
    dhttempgraph.legend()
    
    # subgraph for humidity
    dhthumdgraph = axes[1]
    dhthumdgraph.set_title(WEATHER_DATA_LIST[1], fontdict=titlefont)
    dhthumdgraph.set_ylabel(WEATHER_DATA_LIST[1], fontdict=axisfont)
    dhthumdgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhthumd']['mean'], label="humidity_mean", linestyle='-', color='#0000ff', linewidth=4)
    dhthumdgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhthumd']['min'], label="humidity_min", linestyle='-', color='#000099', linewidth=4)
    dhthumdgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['dhthumd']['max'], label="humidity_max", linestyle='-', color='#9999ff', linewidth=4)
    dhthumdgraph.legend()

    # subgraph for bmp_temperature
    bmptempgraph = axes[2]
    bmptempgraph.set_title(WEATHER_DATA_LIST[2], fontdict=titlefont)
    bmptempgraph.set_ylabel(WEATHER_DATA_LIST[2], fontdict=axisfont)
    bmptempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmptemp']['mean'], label="bmp_temperature_mean", linestyle='-', color='#ff0000', linewidth=4)
    bmptempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmptemp']['min'], label="bmp_temperature_min", linestyle='-', color='#990000', linewidth=4)
    bmptempgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmptemp']['max'], label="bmp_temperature_max", linestyle='-', color='#ff8080', linewidth=4)
    bmptempgraph.legend()

    # subgraph for pressure
    bmppresgraph = axes[3]
    bmppresgraph.set_title(WEATHER_DATA_LIST[3], fontdict=titlefont)
    bmppresgraph.set_ylabel(WEATHER_DATA_LIST[3], fontdict=axisfont)
    bmppresgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmppres']['mean'], label="pressure_mean", linestyle='-', color='#00b300', linewidth=4)
    bmppresgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmppres']['min'], label="pressure_min", linestyle='-', color='#003300', linewidth=4)
    bmppresgraph.plot(pivoted_aggdata_df.index.values, pivoted_aggdata_df['bmppres']['max'], label="pressure_max", linestyle='-', color='#1aff1a', linewidth=4)
    bmppresgraph.legend()

    for axis in axes:
		# specify time format of x-axis
        axis.xaxis.set_major_formatter(timeformat)
        # set tick font size and rotation for all subplots
        axis.tick_params()
        axis.tick_params(labelsize=18, axis='x',labelrotation=30)
        # treat x axis ticks as dates
        axis.xaxis_date()
    # set major x tick interval to be one day
    plt.gca().xaxis.set_major_locator(fmt_day)

    figure.subplots_adjust(top=0.92)
    # plt.tight_layout()
    plt.savefig(APP_DATA_PATH + EXPORTEDS_FOLDER + DAILY_TRENDS_PREFIX + '{}_{}.png'.format(startdatestr, enddatestr), dpi=200, bbox_inches='tight')
    print('saved')
