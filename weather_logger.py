#!/usr/bin/python3

import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from time import sleep
import csv
import os
from datetime import datetime, date, timedelta

debug = False # setting debug to True will print data
delay = 5 # logging delay
# specify weather log path and filename
path = "/home/pi/weather_logs/"
filenameprefix = "weather_log"

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        print("file does not exist")
        return 0
    f.close()
    return 1

# generate csv filename
# filename + 4 digit number with leading zeroes starting from 0000 + ".csv"
def generateFileName():
    global filenameprefix
    dnow = date.today()
    filename = filenameprefix + dnow.strftime('%m%d%Y') + '.csv'
    return filename


# create the complete file path of the log file
def generateFilePath():
    global path
    filepath = path + generateFileName()
    return filepath

# create a new csv file and write the csv file header
def createOpenLogFile():
    global filepath
    filepath = generateFilePath()
    csvfile = open(filepath, 'a', newline='')
    writer = csv.writer(csvfile, delimiter=',')
    if os.stat(filepath).st_size == 0:
        writer.writerow(["Time", "Humidity", "Temperature", "BMP_temperature", "Pressure"])
    csvfile.close()
    print(filepath)

# try to create the dir for logs if it does not exist
try:
    os.mkdir(path)
except FileExistsError:
    print("dir exists")

filepath = ""
newfiledate = datetime(1, 1, 1) # initial value

# define DHT sensor type and pin
dsensor = Adafruit_DHT.DHT11
pin = 4
# initialize BMP180 sensor
# loop until the sensor is properly connected
sensor = None
while sensor is None:
    try:
        sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
    except OSError:
        if debug: print("Cannot initialize BMP180 sensor")

# weather condition variables
temperature, humidity, bmp_temperature, pressure = -999, -999, -999, -999

# read sensor and write to log file indefinitely
while True:
    try:
        # if a new day has started, create a new log file for the day
        if date.today() > newfiledate.date():
            if debug:
                if (date.today() - newfiledate.date()).days == 1:
                    print("closing current file and opening a new file")
                else:
                    print("Opening file initially")
            createOpenLogFile()
            newfiledate = datetime.now()

        # read DHT11 sensor
        instTemperature, instHumidity = None, None
        while instHumidity is None or instTemperature is None:
            instHumidity, instTemperature = Adafruit_DHT.read(dsensor, pin)
            if instHumidity is None or instTemperature is None:
                if debug: print("Faulty DHT11 reading")
            else:
                humidity, temperature = instHumidity, instTemperature
                if debug: print("Good DHT11 reading")

        # read BMP180 sensor
        try:
            bmp_temperature, pressure = sensor.read_temperature(), sensor.read_pressure()
        except OSError:
            if debug: print("Cannot read BMP180 sensor")
        except NameError:
            if debug: print("BMP180 sensor not initialized, please check your sensor wiring.")

        # errors may occur due to the precise timing required by the DHT11 sensor

        if temperature > -999 and humidity > -999 and bmp_temperature > -999 and pressure > -999:
            csvfile = open(filepath, 'a', newline='')
            writer = csv.writer(csvfile, delimiter=',')
            dtnow = datetime.now()
            timeStr = dtnow.strftime('%H:%M:%S')
            if debug:
                print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, humidity, temperature, bmp_temperature, pressure))

            # write csv data to file
            writer.writerow([timeStr, humidity, temperature, bmp_temperature, pressure])
            csvfile.close()
            sleep(delay)

    except KeyboardInterrupt:
        print("Exiting")
        break;

print("Program exit")
# debug
csvfile = open(filepath, 'a', newline='')
csvfile.write("Program exit")
csvfile.close()
