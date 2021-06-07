from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy import select, insert, update, delete
from sqlalchemy import func, cast
from sqlalchemy.orm import Bundle, aliased
from sqlalchemy import and_, or_
from datetime import datetime, time, timedelta

# sqlite db engine
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, future=True)
session = Session(engine)
Base = declarative_base()

# log timestamp class
class DateTimeRow(Base):
    __tablename__ = 'log_time'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    
    dht_temperature = relationship("DHTTemperature", uselist=False, back_populates="datetimerow")
    dht_humidity = relationship("DHTHumidity", uselist=False, back_populates="datetimerow")
    bmp_temperature = relationship("BMPTemperature", uselist=False, back_populates="datetimerow")
    bmp_pressure = relationship("BMPPressure", uselist=False, back_populates="datetimerow")

    def __repr__(self):
        return f"DateTimeRow(id={self.id!r}, datetime={self.datetime!r})"

# DHT temperature table
class DHTTemperature(Base):
    __tablename__ = 'dht_temperature'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_temperature")

    def __repr__(self):
        return f"DHTTemperature(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# DHT humidity table
class DHTHumidity(Base):
    __tablename__ = 'dht_humidity'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_humidity")

    def __repr__(self):
        return f"DHTHumidity(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# BMP temperature table
class BMPTemperature(Base):
    __tablename__ = 'bmp_temperature'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_temperature")

    def __repr__(self):
        return f"BMPTemperature(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# BMP pressure table
class BMPPressure(Base):
    __tablename__ = 'bmp_pressure'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_pressure")

    def __repr__(self):
        return f"BMPPressure(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# create the tables on the db
Base.metadata.create_all(engine)

# class that represents a single weather log
# datetime_ is the DateTimeRow object
# log is a dictionary containing the weather logs
class WeatherLog():
    def __init__(self, datetime_, log):
        self.datetime = datetime_
        self.log = log
        
        self.datetime.dht_temperature = self.log['dhttemp']
        self.datetime.dht_humidity = self.log['dhthumd']
        self.datetime.bmp_temperature = self.log['bmptemp']
        self.datetime.bmp_pressure = self.log['bmppres']

    def __repr__(self):
        str= f"WeatherLog(datetime={self.datetime}, "
        for key in self.log.keys():
            str += f"{key}={self.log[key]}, "
        str += ")"
        return str

    def insert(self):
        session.add(self.datetime)
        session.commit()

    @staticmethod
    def select(datetime):
        dt = aliased(DateTimeRow, name='dt')
        stmt = select(dt).where(dt.datetime == datetime)
        row = session.execute(stmt).first()
        if row is not None:
            log = {'dhttemp': row.dt.dht_temperature, 'dhthumd': row.dt.dht_humidity, \
                   'bmptemp': row.dt.bmp_temperature, 'bmppres': row.dt.bmp_pressure}
            return WeatherLog(row.dt, log)

    @staticmethod
    def selectMultiple(date):
        datetimelow = datetime.combine(date, time(0,0,0))
        datetimehigh = datetime.combine(date, time(23,59,59))
        dt = aliased(DateTimeRow, name='dt')
        stmt = select(dt).where(and_((dt.datetime >= datetimelow), (dt.datetime <= datetimehigh)))
        weatherlogs = []
        for row in session.execute(stmt):
            log = {'dhttemp': row.dt.dht_temperature, 'dhthumd': row.dt.dht_humidity, \
                   'bmptemp': row.dt.bmp_temperature, 'bmppres': row.dt.bmp_pressure}
            weatherlog = WeatherLog(row.dt, log)
            weatherlogs.append(weatherlog)
        return weatherlogs

    @staticmethod
    def createNew(datetime, data):
        dt = DateTimeRow(datetime=datetime)
        log = {'dhttemp' : DHTTemperature(value=data['dhttemp']), \
        'dhthumd' : DHTHumidity(value=data['dhthumd']), \
        'bmptemp' : BMPTemperature(value=data['bmptemp']), \
        'bmppres' : BMPPressure(value=data['bmppres'])}
        
        return WeatherLog(dt, log)

    def update(self, data=None):
        if data is not None:
            for key in data.keys():
                self.log[key].value = data[key].value
            self.datetime.dht_temperature = self.log['dhttemp']
            self.datetime.dht_humidity = self.log['dhthumd']
            self.datetime.bmp_temperature = self.log['bmptemp']
            self.datetime.bmp_pressure = self.log['bmppres']
            session.commit()

    def delete(self):
        session.delete(self.datetime)
        session.commit()

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
weather_data2.update(data={'dhttemp': DHTTemperature(value=27), 'bmptemp': BMPTemperature(value=26.6)})
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
print('# delete one row of weather data given the time and date')
weather_data0.delete()
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
weather_data3 = WeatherLog.selectMultiple(dt2)
for i in range(len(weather_data3)):
    print(weather_data3[i])
print('\n')
