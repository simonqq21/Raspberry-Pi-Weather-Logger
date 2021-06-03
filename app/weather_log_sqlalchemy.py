from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy import select, insert, update, delete
from sqlalchemy import func, cast
from sqlalchemy.orm import Bundle, aliased
from sqlalchemy import and_, or_
from datetime import datetime, time, timedelta

# sqlite db engine
engine = create_engine("sqlite+pysqlite:///weather_logs.db", echo=True, future=True)
session = Session(engine)
Base = declarative_base()

# log timestamp class
class DateTimeRow(Base):
    __tablename__ = 'log_time'
    
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    dht_temperature = relationship("DHTTemperature", back_populates="datetimerow")
    dht_humidity = relationship("DHTHumidity", back_populates="datetimerow")
    bmp_temperature = relationship("BMPTemperature", back_populates="datetimerow")
    bmp_pressure = relationship("BMPPressure", back_populates="datetimerow")
    
    def __repr__(self):
        return f"LogTime(id={self.id!r}, datetime={self.datetime!r})"

# DHT temperature table
class DHTTemperature(Base):
    __tablename__ = 'dht_temperature'
    
    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_temperature")
    
    def __repr__(self):
        return f"DHTTemperature(id={self.id!r}, datetime_id={self.time_id!r}, value={self.value!r})"
    
# DHT humidity table 
class DHTHumidity(Base):
    __tablename__ = 'dht_humidity'
    
    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_humidity")
    
    def __repr__(self):
        return f"DHTHumidity(id={self.id!r}, datetime_id={self.time_id!r}, value={self.value!r})"

# BMP temperature table 
class BMPTemperature(Base):
    __tablename__ = 'bmp_temperature'
    
    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_temperature")
    
    def __repr__(self):
        return f"BMPTemperature(id={self.id!r}, datetime_id={self.time_id!r}, value={self.value!r})"

# BMP pressure table
class BMPPressure(Base):
    __tablename__ = 'bmp_pressure'
    
    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_pressure")
    
    def __repr__(self):
        return f"BMPPressure(id={self.id!r}, datetime_id={self.time_id!r}, value={self.value!r})"

# create the tables on the db
Base.metadata.create_all(engine)

#db operations:
# insert one row of weather data with the time and date
# insert many rows of weather data given the date
# select one row of weather data given the time and date
# select many rows of weather data given the date 
# update values of one row of weather data given the time, date, and update values
# delete one row of weather data given the time and date
# delete many rows of weather data given the date

# insert one row of weather data with the time and date

# insert many rows of weather data given the date

# select one row of weather data given the time and date

# select many rows of weather data given the date

# update values of one row of weather data given the time, date, and update values

# delete one row of weather data given the time and date

# delete many rows of weather data given the date