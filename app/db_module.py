from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float, Date, DateTime
from sqlalchemy import select, insert, update, delete
from sqlalchemy import func, cast
from sqlalchemy.orm import Bundle, aliased
from sqlalchemy import and_, or_
from datetime import datetime, time, timedelta

from config import APP_DATA_PATH, DB_FILENAME

# sqlite db engine
engine = create_engine("sqlite+pysqlite:///" + APP_DATA_PATH + DB_FILENAME, echo=False, future=True)
session = Session(engine)
Base = declarative_base()

# log timestamp class
class DateTimeRow(Base):
    __tablename__ = 'log_datetime'

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
    datetime_id = Column(ForeignKey('log_datetime.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_temperature")

    def __repr__(self):
        return f"DHTTemperature(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# DHT humidity table
class DHTHumidity(Base):
    __tablename__ = 'dht_humidity'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_datetime.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="dht_humidity")

    def __repr__(self):
        return f"DHTHumidity(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# BMP temperature table
class BMPTemperature(Base):
    __tablename__ = 'bmp_temperature'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_datetime.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_temperature")

    def __repr__(self):
        return f"BMPTemperature(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# BMP pressure table
class BMPPressure(Base):
    __tablename__ = 'bmp_pressure'

    id = Column(Integer, primary_key=True)
    datetime_id = Column(ForeignKey('log_datetime.id'))
    value = Column(Float, nullable=False)
    datetimerow = relationship("DateTimeRow", back_populates="bmp_pressure")

    def __repr__(self):
        return f"BMPPressure(id={self.id!r}, datetime_id={self.datetime_id!r}, value={self.value!r})"

# class for daily aggregated weather data
class DateRow(Base):
    __tablename__ = 'date'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    aggDHTTemp = relationship('AggDHTTemperature', uselist=False, back_populates='date')
    aggDHTHumd = relationship('AggDHTHumidity', uselist=False, back_populates='date')
    aggBMPTemp = relationship('AggBMPTemperature', uselist=False, back_populates='date')
    aggBMPPres = relationship('AggBMPPressure', uselist=False, back_populates='date')

    def __repr__(self):
        return f"DateRow(id={self.id!r}, date={self.date!r})"

# class for daily aggregated DHT temperature
class AggDHTTemperature(Base):
    __tablename__ = 'agg_dht_temperature'
    id = Column(Integer, primary_key=True)
    date_id = Column(ForeignKey('date.id'))
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    date = relationship('DateRow', back_populates='aggDHTTemp')

    def __repr__(self):
        return f"AggDHTTemperature(id={self.id!r}, date_id={self.date_id!r}, \
        mean={self.mean!r}, std={self.std!r}, min={self.min!r}, max={self.max!r})"

# class for daily aggregated DHT humidity
class AggDHTHumidity(Base):
    __tablename__ = 'agg_dht_humidity'
    id = Column(Integer, primary_key=True)
    date_id = Column(ForeignKey('date.id'))
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    date = relationship('DateRow', back_populates='aggDHTHumd')

    def __repr__(self):
        return f"AggDHTHumidity(id={self.id!r}, date_id={self.date_id!r}, \
        mean={self.mean!r}, std={self.std!r}, min={self.min!r}, max={self.max!r})"

# class for daily aggregated BMP temperature
class AggBMPTemperature(Base):
    __tablename__ = 'agg_bmp_temperature'
    id = Column(Integer, primary_key=True)
    date_id = Column(ForeignKey('date.id'))
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    date = relationship('DateRow', back_populates='aggBMPTemp')

    def __repr__(self):
        return f"AggBMPTemperature(id={self.id!r}, date_id={self.date_id!r}, \
        mean={self.mean!r}, std={self.std!r}, min={self.min!r}, max={self.max!r})"

# class for daily aggregated BMP pressure
class AggBMPPressure(Base):
    __tablename__ = 'agg_bmp_pressure'
    id = Column(Integer, primary_key=True)
    date_id = Column(ForeignKey('date.id'))
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)
    date = relationship('DateRow', back_populates='aggBMPPres')

    def __repr__(self):
        return f"AggBMPPressure(id={self.id!r}, date_id={self.date_id!r}, \
        mean={self.mean!r}, std={self.std!r}, min={self.min!r}, max={self.max!r})"

# create the tables on the db
Base.metadata.create_all(engine)

# class that represents a single weather log
class WeatherLog():
    def __init__(self, datetime_, log):
        self.datetime = datetime_
        self.log = log
        
        self.datetime.dht_temperature = self.log['dhttemp']
        self.datetime.dht_humidity = self.log['dhthumd']
        self.datetime.bmp_temperature = self.log['bmptemp']
        self.datetime.bmp_pressure = self.log['bmppres']

    def __repr__(self):
        str= f"WeatherLog(time={self.datetime}, "
        for key in self.log.keys():
            str += f"{key}={self.log[key]}"
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
                self.log[key].value = self.log[key].value if key not in data.keys() else data[key].value
            self.datetime.dht_temperature = self.log['dhttemp']
            self.datetime.dht_humidity = self.log['dhthumd']
            self.datetime.bmp_temperature = self.log['bmptemp']
            self.datetime.bmp_pressure = self.log['bmppres']
            session.commit()

    def delete(self):
        session.delete(self.datetime)
        session.commit()

# class that represents a single day of aggregated weather data
class AggDayWeather():
    def __init__(self, date_, aggdata):
        self.daterow = date_
        self.aggdata = aggdata

        self.daterow.aggDHTTemp = self.aggdata['aggdhttemp']
        self.daterow.aggDHTHumd = self.aggdata['aggdhthumd']
        self.daterow.aggBMPTemp = self.aggdata['aggbmptemp']
        self.daterow.aggBMPPres = self.aggdata['aggbmppres']

    def __repr__(self):
        str = f"AggDayWeather(daterow={self.daterow}, "
        for key in self.aggdata.keys():
            str += f"{key}={self.aggdata[key]}, "
        str += ")"
        return str

    def insert(self):
        session.add(self.daterow)
        session.commit()

    @staticmethod
    def select(date):
        d = aliased(DateRow, name='d')
        stmt = select(d).where(d.date == date)
        row = session.execute(stmt).first()
        if row is not None:
            aggdata = {'aggdhttemp': row.d.aggDHTTemp, 'aggdhthumd': row.d.aggDHTHumd, \
                   'aggbmptemp': row.d.aggBMPTemp, 'aggbmppres': row.d.aggBMPPres}
            return AggDayWeather(row.d, aggdata)

    @staticmethod
    def selectMultiple(datelow, datehigh):
        d = aliased(DateRow, name='d')
        stmt = select(d).where(and_((d.date >= datelow), (d.date <= datehigh)))
        aggweatherlogs = []
        for row in session.execute(stmt):
            aggdata = {'aggdhttemp': row.d.aggDHTTemp, 'aggdhthumd': row.d.aggDHTHumd, \
                   'aggbmptemp': row.d.aggBMPTemp, 'aggbmppres': row.d.aggBMPPres}
            return AggDayWeather(row.d, aggdata)
            aggweatherlog = AggDayWeather(row.d, aggdata)
            aggweatherlogs.append(aggweatherlog)
        return aggweatherlogs

    def update(self, data=None):
        if data is not None:
            for key in data.keys():
                self.aggdata[key].mean = data[key].mean
                self.aggdata[key].std = data[key].std
                self.aggdata[key].min = data[key].min
                self.aggdata[key].max = data[key].max
        self.daterow.aggDHTTemp = self.aggdata['aggdhttemp']
        self.daterow.aggDHTHumd = self.aggdata['aggdhthumd']
        self.daterow.aggBMPTemp = self.aggdata['aggbmptemp']
        self.daterow.aggBMPPres = self.aggdata['aggbmppres']
        session.commit()

    def delete(self):
        session.delete(self.daterow)
        session.commit()
