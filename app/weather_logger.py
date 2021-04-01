#!/usr/bin/python3
from time import sleep
import csv
import os
from datetime import datetime, date, time, timedelta
from threading import Thread, Event
import signal
import subprocess
from config import APP_PATH, APP_DATA_PATH, WEATHER_LOGS_FOLDER, RAW_LOG_PREFIX
from config import DEBUG
from functions import exists, generateFileName, generateFilePath, createOpenLogFile
from rpi_functions import statusled, BMP180read, DHT11read, flashStatusLED, statusLedEvent, terminateEvent

DEBUG=True
delay = 5 # logging delay
flash_duration = 0.5 # status LED flash duration

# Ctrl-C KeyboardInterrupt signal handler
# set the Event to terminate all threads
def signal_handler(signum, frame):
    terminateEvent.set()

filepath = ""
newfiledate = datetime.min # initial value

# KeyboardInterrupt signal
signal.signal(signal.SIGINT, signal_handler)
# status LED thread
statusLedThread = Thread(target=flashStatusLED, name="statusledthread", args=(statusled, flash_duration))
statusLedThread.start()

# weather condition variables
temperature, humidity, bmp_temperature, pressure = -999, -999, -999, -999

# read sensor and write to log file indefinitely
while True:
    # if a new day has started, create a new log file for the day
    if date.today() > newfiledate.date():
        if (date.today() - newfiledate.date()).days == 1:
            if DEBUG:
                print("closing current file and opening a new file")
        else:
            if DEBUG:
                print("Opening file initially")
        filepath = createOpenLogFile(APP_DATA_PATH + WEATHER_LOGS_FOLDER, RAW_LOG_PREFIX)
        newfiledate = datetime.now()

        # call a process to average all unaveraged raw log files to 1 minute intervals
        proc1 = subprocess.Popen('python3 {}/average_raw_logs.py'.format(APP_PATH),
        stdout = subprocess.PIPE, shell=True)

        # call a process to (re)generate report data for days with incomplete or missing reports
        proc1 = subprocess.Popen('python3 {}/process_incomplete_reports.py'.format(APP_PATH),
        stdout = subprocess.PIPE, shell=True)

    # read DHT11 sensor
    temperature, humidity = DHT11read()

    # read BMP180 sensor
    bmp_temperature, pressure = BMP180read()

    # errors may occur due to the precise timing required by the DHT11 sensor
    if temperature > -999 and humidity > -999 and bmp_temperature > -999 and pressure > -999:
        csvfile = open(filepath, 'a', newline='')
        writer = csv.writer(csvfile, delimiter=',')
        dtnow = datetime.now()
        timeStr = dtnow.strftime('%H:%M:%S')
        if DEBUG:
            print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, humidity, \
            temperature, bmp_temperature, pressure))
        # write csv data to file
        writer.writerow([timeStr, humidity, temperature, bmp_temperature, pressure])
        csvfile.close()

        # set the Event to flash the status LED
        statusLedEvent.set()
    # delay per reading that also checks for the terminating event triggered by Ctrl-C
    terminateEvent.wait(delay)

    # terminate main thread when Ctrl-C is entered
    if terminateEvent.is_set():
        print("Exiting")
        break;

print("Program exit")
