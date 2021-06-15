import os
import csv
from datetime import datetime, date
import argparse
import pandas as pd
import numpy as np 
from functions import deleteAllSimilar
from config import APP_DATA_PATH, DB_FILENAME
from config import HEADER, STATS, UNITS, TABLE_ABBREVS
from config import EXPORT_PREFIX, AGG_EXPORT_PREFIX
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
from db_module import getAllAggDates

#get the minimum and maximum dates of aggregated weather data in the db 
datesList = getAllAggDates()
if len(datesList) == 0:
	print('no records, exiting')
	exit(0)
mindate = min(datesList)
maxdate = max(datesList)

# parse cmd arguments
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

startdate = date(args.startyear, args.startmonth, args.startday)
enddate = date(args.endyear, args.endmonth, args.endday)

startdatestr = startdate.strftime("%Y-%m-%d")
enddatestr = enddate.strftime("%Y-%m-%d")

# delete the previous exported data
deleteAllSimilar(APP_DATA_PATH, EXPORT_PREFIX)
deleteAllSimilar(APP_DATA_PATH, AGG_EXPORT_PREFIX)

dataDict = {}
dataDict['datetime'] = []
for k in HEADER.keys():
    dataDict[k] = []

# load all weather data rows between the two dates from the db
weather_logs = WeatherLog.selectMultiple(date1=startdate, date2=enddate)
if len(weather_logs) == 0:
	print('no records, exiting')
	exit(0)
	
for w in weather_logs:
    dataDict['datetime'].append(w.datetime.datetime)
    for k in HEADER.keys():
        dataDict[k].append(w.log[k].value)

# weather data DataFrame
weather_df = pd.DataFrame(data=dataDict)
# ~ print(weather_df)
# export weather data dataframe as csv
weather_df.to_csv(APP_DATA_PATH + EXPORT_PREFIX + startdatestr + '_' + enddatestr + '.csv')

# load all daily aggregated data between the two dates from the db
results = AggDayWeather.selectMultiple(startdate, enddate)
if len(results) == 0:
	print('no records, exiting')
	exit(0)
	
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
# pivot the dataframe to get the desired representation
pivoted_aggdata_df = pd.pivot_table(aggdata_tb, values='value', index='date', columns=['WEATHER_DATA_LIST', 'stat_type'])
# export aggregated weather data dataframe as csv
pivoted_aggdata_df.to_csv(APP_DATA_PATH + AGG_EXPORT_PREFIX + startdatestr + '_' + enddatestr + '.csv')
