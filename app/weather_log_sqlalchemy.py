from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Float
from sqlalchemy import select, insert, update, delete
from sqlalchemy import func, cast
from sqlalchemy.orm import Bundle, aliased
from sqlalchemy import and_, or_

# sqlite db engine
engine = create_engine("sqlite+pysqlite:///weather_logs.db", echo=True, future=True)
session = Session(engine)
Base = declarative_base()

# log timestamp class
class LogTime(Base):
    __tablename__ = 'log_time'
    
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    
    def __repr__(self):
        return f"LogTime(id={self.id!r}, datetime={self.datetime!r})"

# DHT temperature table
class DHTTemperature(Base):
    __tablename__ = 'dht_temperature'
    
    id = Column(Integer, primary_key=True)
    time_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"DHTTemperature(id={self.id!r}, time_id={self.time_id!r}, value={self.value!r})"
    
# DHT humidity table 
class DHTHumidity(Base):
    __tablename__ = 'dht_humidity'
    
    id = Column(Integer, primary_key=True)
    time_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"DHTHumidity(id={self.id!r}, time_id={self.time_id!r}, value={self.value!r})"

# BMP temperature table 
class BMPTemperature(Base):
    __tablename__ = 'bmp_temperature'
    
    id = Column(Integer, primary_key=True)
    time_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"BMPTemperature(id={self.id!r}, time_id={self.time_id!r}, value={self.value!r})"

# BMP pressure table
class BMPPressure(Base):
    __tablename__ = 'bmp_pressure'
    
    id = Column(Integer, primary_key=True)
    time_id = Column(ForeignKey('log_time.id'))
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"BMPPressure(id={self.id!r}, time_id={self.time_id!r}, value={self.value!r})"

# create the tables on the db
Base.metadata.create_all(engine)



