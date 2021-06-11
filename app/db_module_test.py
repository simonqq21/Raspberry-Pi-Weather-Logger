from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
from db_module import session
from sqlalchemy import func, cast
from sqlalchemy import select
from sqlalchemy.orm import aliased
import sqlalchemy
from datetime import datetime, date, timedelta

# db operations:
# insert one row of weather data with the time and date
# insert many rows of weather data given the date
# select one row of weather data given the time and date
# select many rows of weather data given the date
# update values of one row of weather data given the time, date, and update values
# delete one row of weather data given the time and date
# delete many rows of weather data given the date

###### DRIVER CODE #######
# insert one new row of weather data with the time and date
print('# insert one row of weather data with the time and date')
dt1 = datetime(2021,6,1,12,0)
data = {'dhttemp': 28.0, 'dhthumd': 79, 'bmptemp': 28.2, 'bmppres': 100125}
weather_data0 = WeatherLog.createNew(dt1, data)
weather_data0.insert()
print('weather_data0 = '+ str(weather_data0))
print('\n')

# insert many new rows of weather data given the date
print('# insert many rows of weather data given the date')
dt2 = datetime(2021,6,4,12,0)
weatherdataarr = [{'dhttemp':26, 'dhthumd':10, 'bmptemp':25.4, 'bmppres':100110},
                  {'dhttemp':27, 'dhthumd':30, 'bmptemp':26.0, 'bmppres':100150},
                  {'dhttemp':28, 'dhthumd':50, 'bmptemp':27.8, 'bmppres':100200},
                  {'dhttemp':29, 'dhthumd':70, 'bmptemp':28.9, 'bmppres':100250},
                  {'dhttemp':30, 'dhthumd':90, 'bmptemp':29.3, 'bmppres':100300}]
for i in range(len(weatherdataarr)):
    weather_data = WeatherLog.createNew(dt2, weatherdataarr[i])
    weather_data.insert()
    dt2 = dt2.replace(minute=dt2.minute+5)
print('\n')

# select one row of weather data given the time and date
print('# select one row of weather data given the time and date')
weather_data1 = WeatherLog.select(dt1)
print('weather_data1 = ' + str(weather_data1))
print('\n')

# select many rows of weather data given the date
print('# select many rows of weather data given the date')
weather_data3 = WeatherLog.selectMultiple(dt2)
for i in range(len(weather_data3)):
    print(weather_data3[i])
print('\n')

# update values of one row of weather data given the time, date, and update values
print('# update values of one row of weather data given the time, date, and update values')
weather_data2 = WeatherLog.select(dt1)
weather_data2.update()
print('# update with no update values')
print('weather_data2 = ' + str(weather_data2))
weather_data2.update(data={'dhttemp': DHTTemperature(value=27), 'bmptemp': BMPTemperature(value=26.6), 'bmppres':BMPPressure(value=999999)})
print('# update with two update values')
print('weather_data2 = ' + str(weather_data2))
weather_data2.update(data={'dhttemp':DHTTemperature(value=28), 'dhthumd':DHTHumidity(value=32), \
                     'bmptemp':BMPTemperature(value=27.4), 'bmppres':BMPPressure(value=100200)})
print('# update with four update values')
print('weather_data2 = ' + str(weather_data2))
print('check if update was applied by selecting the data back from db')
weather_data1 = WeatherLog.select(dt1)
print('weather_data1 = ' + str(weather_data1))
print('\n')

# delete one row of weather data given the time and date
# print('# delete one row of weather data given the time and date')
weather_data1 = WeatherLog.select(dt1)
weather_data1.delete()
weather_data1 = WeatherLog.select(dt1)
if weather_data1 is not None:
    print('weather_data1 = ' + str(weather_data1))
else:
    print('successfully deleted')
print('\n')

# delete many rows of weather data given the date
print('# delete many rows of weather data given the date')
print('before deletion')
weather_data3 = WeatherLog.selectMultiple(dt2)
for i in range(len(weather_data3)):
    print(weather_data3[i])
print('\n')

weather_data3 = WeatherLog.selectMultiple(dt2)
for i in range(len(weather_data3)):
    weather_data3[i].delete()
print('\n')
print('after deletion')
weather_data3 = WeatherLog.selectMultiple(datetime.min, datetime.max)
for i in range(len(weather_data3)):
    print(weather_data3[i])
print('\n')

d1 = date.today()
d2 = date.today()
daterow = DateRow(date=d1)
daterow2 = DateRow(date=d2)
try:
    session.add(daterow)
    session.commit()
except:
    print('Unique constraint error!')
    session.rollback()

try:
    session.add(daterow2)
    session.commit()
except:
    print('Unique constraint error 2!')
    session.rollback()

stmt = select(DateRow)
for row in session.execute(stmt):
    print(row)
