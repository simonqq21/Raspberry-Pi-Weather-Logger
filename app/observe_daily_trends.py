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

This script deletes all weather data logs within a single day once the aggregated data has
been saved.
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
