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
class WeatherLog():
    def __init__(self, datetime_, dhttemp, dhthumd, bmptemp, bmppres):
        self.datetime = datetime_
        self.dhttemp = dhttemp
        self.dhthumd = dhthumd
        self.bmptemp = bmptemp
        self.bmppres = bmppres
        self.datetime.dht_temperature = self.dhttemp
        self.datetime.dht_humidity = self.dhthumd
        self.datetime.bmp_temperature = self.bmptemp
        self.datetime.bmp_pressure = self.bmppres
        
    def __repr__(self):
        return f"WeatherLog(time={self.datetime}," \
            f"dhttemp={self.dhttemp}," \
            f"dhthumd={self.dhthumd}," \
            f"bmptemp={self.bmptemp}," \
            f"bmppres={self.bmppres})"
    
    def insert(self):
        session.add(self.datetime)
        session.commit()
    
    @staticmethod
    def select(datetime):
        dt = aliased(DateTimeRow, name='dt')
        stmt = select(dt).where(dt.datetime == datetime)
        row = session.execute(stmt).first()
        if row is not None:
            return WeatherLog(row.dt, row.dt.dht_temperature, \
                              row.dt.dht_humidity, \
                              row.dt.bmp_temperature, \
                              row.dt.bmp_pressure)
    
    @staticmethod
    def selectMultiple(date):
        datetimelow = datetime.combine(date, time(0,0,0))
        datetimehigh = datetime.combine(date, time(23,59,59))
        dt = aliased(DateTimeRow, name='dt')
        stmt = select(dt).where(and_((dt.datetime >= datetimelow), (dt.datetime <= datetimehigh)))
        weatherlogs = []
        for row in session.execute(stmt):
            weatherlog = WeatherLog(row.dt, row.dt.dht_temperature, \
                              row.dt.dht_humidity, \
                              row.dt.bmp_temperature, \
                              row.dt.bmp_pressure)
            weatherlogs.append(weatherlog)
        return weatherlogs
        
    def update(self, dhttemp=None, dhthumd=None, bmptemp=None, bmppres=None):
        self.dhttemp.value = self.dhttemp.value if dhttemp is None else dhttemp
        self.dhthumd.value = self.dhthumd.value if dhthumd is None else dhthumd
        self.bmptemp.value = self.bmptemp.value if bmptemp is None else bmptemp
        self.bmppres.value = self.bmppres.value if bmppres is None else bmppres
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

# insert one row of weather data with the time and date
print('# insert one row of weather data with the time and date')
dt1 = datetime(2021,6,1,12,0)
time0 = DateTimeRow(datetime=dt1)
dhttemp = DHTTemperature(value=28.0)
dhthumd = DHTHumidity(value=79)
bmptemp = BMPTemperature(value=28.2)
bmppres = BMPPressure(value=100125)
weather_data0 = WeatherLog(time0, dhttemp, dhthumd, bmptemp, bmppres)
print('weather_data0 = '+ str(weather_data0))
weather_data0.insert()
print('\n')

# insert many rows of weather data given the date
print('# insert many rows of weather data given the date')
dt2 = datetime(2021,6,4,12,0)
weatherdataarr = [{dhttemp:26, dhthumd:10, bmptemp:25.4, bmppres:100110},
                  {dhttemp:27, dhthumd:30, bmptemp:26.0, bmppres:100150},
                  {dhttemp:28, dhthumd:50, bmptemp:27.8, bmppres:100200},
                  {dhttemp:29, dhthumd:70, bmptemp:28.9, bmppres:100250},
                  {dhttemp:30, dhthumd:90, bmptemp:29.3, bmppres:100300}]
for i in range(len(weatherdataarr)):
    dtORM = DateTimeRow(datetime=dt2)
    dhttempORM = DHTTemperature(value=weatherdataarr[i][dhttemp])
    dhthumdORM = DHTHumidity(value=weatherdataarr[i][dhthumd])
    bmptempORM = BMPTemperature(value=weatherdataarr[i][bmptemp])
    bmppresORM = BMPPressure(value=weatherdataarr[i][bmppres])
    weather_data = WeatherLog(dtORM, dhttempORM, dhthumdORM, bmptempORM, bmppresORM)
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
print('weather_data2 = ' + str(weather_data2))
weather_data2.update(dhttemp=27, bmptemp=26.6)
print('weather_data2 = ' + str(weather_data2))
weather_data2.update(dhttemp=28, dhthumd=32, bmptemp=27.4, bmppres=100200)
print('weather_data2 = ' + str(weather_data2))
print('weather_data0 = '+ str(weather_data0))
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
