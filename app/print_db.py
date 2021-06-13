from db_module import session
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
from sqlalchemy import func, cast
from sqlalchemy import select 
from sqlalchemy.orm import aliased
from datetime import date

print('# rowcount')
dt = aliased(DateTimeRow, name='dt')
stmt = select(func.count(dt.id).label('rowcount'))
for r in session.execute(stmt):
    print(r)
print('\n')

# select all rows from each table
print('# rows')
results = WeatherLog.selectMultiple()
for r in results:
    print(r)
    
print('# rowcount')
d = aliased(DateRow, name='d')
# stmt = select(func.count(d.id).label('rowcount'))
stmt = select(d.id, d.date)
for r in session.execute(stmt):
    print(r)
print('\n')

# select all rows from each table
print('# rows')
results = AggDayWeather.selectMultiple(date.min, date.max)
if results is not None:
	print(results)
	print(len(results))
