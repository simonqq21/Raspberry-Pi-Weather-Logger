#!/usr/bin/python3
from time import sleep
import os
from datetime import datetime, date, time, timedelta
from threading import Thread, Event
import signal
import subprocess
from config import APP_PATH, APP_DATA_PATH
from config import logging_duration, average_samples, logging_interval
from config import DEBUG
from functions import exists
from rpi_functions import terminateEvent
from rpi_functions import statusled, BMP180read, DHT11read
from db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from db_module import WeatherLog, AggDayWeather
flash_duration = 5 # status LED flash duration

# Ctrl-C KeyboardInterrupt signal handler
# set the Event to terminate all threads
def signal_handler(signum, frame):
    terminateEvent.set()
# KeyboardInterrupt signal
signal.signal(signal.SIGINT, signal_handler)

# weather condition variables
weather_data = {'dhttemp': 0, 'dhthumd': 0, 'bmptemp': 0, 'bmppres': 0}

# read sensor and write to log file indefinitely
newfiledate = date.min
print('init')
statusled.off()
while True:
    # if a new day has started, run the code to generate incomplete daily reports and plot files
    if date.today() > newfiledate:
        newfiledate = date.today()

        # call a process to (re)generate report data for days with incomplete or missing reports
        proc1 = subprocess.Popen('python3 {}/process_incomplete_reports.py'.format(APP_PATH),
        stdout = subprocess.PIPE, shell=True)

    for d in weather_data:
        weather_data[d] = 0

    for i in range(average_samples):
        print(i)
        # read DHT11 sensor
        dhttemp, dhthumd = DHT11read()
        weather_data['dhttemp'] += dhttemp
        weather_data['dhthumd'] += dhthumd
        # read BMP180 sensor
        bmptemp, bmppres = BMP180read()
        weather_data['bmptemp'] += bmptemp
        weather_data['bmppres'] += bmppres
        # delay per reading that also checks for the terminating event triggered by Ctrl-C
        terminateEvent.wait(logging_interval)
        if terminateEvent.is_set():
            print("Exiting")
            break;
        statusled.blink(on_time=1, off_time=0, n=1, background=True)

    # terminate main thread when Ctrl-C is entered
    if terminateEvent.is_set():
        print("Exiting")
        break;

    # average
    for d in weather_data:
        weather_data[d] /= average_samples
    # insert data into db
    dtnow = datetime.now().replace(second=0, microsecond=0)
    timeStr = dtnow.strftime('%H:%M:%S')
    if DEBUG:
        print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, weather_data['dhttemp'], \
        weather_data['dhthumd'], weather_data['bmptemp'], weather_data['bmppres']))
    newlog = WeatherLog.createNew(dtnow, weather_data)
    newlog.insert()

    # long blink signifying a log collection
    statusled.blink(on_time=10, off_time=0, n=1, background=True)

print("Program exit")
