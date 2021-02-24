#!/usr/bin/python3

from gpiozero import LED
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from time import sleep
import csv
import os
from datetime import datetime, date, timedelta
from threading import Thread, Event
import signal

debug = False # setting debug to True will print data
delay = 30 # logging delay
flash_duration = 0.5 # status LED flash duration
# specify weather log path and filename
path = os.path.abspath(os.path.dirname(__file__)) + '/weather_logs/'
filenameprefix = 'weather_log'

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
def generateFileName(filenameprefix):
    filename = filenameprefix + date.today().strftime('%m%d%Y') + '.csv'
    if debug: print(filename)
    return filename


# create the complete file path of the log file
def generateFilePath(path, filenameprefix):
    # try to create the dir for logs if it does not exist
    if path != '':
        if not os.path.exists(path):
            os.mkdir(path)
    filename = generateFileName(filenameprefix)
    filepath = path + filename
    return filepath

# create a new csv file and write the csv file header
def createOpenLogFile(path, filenameprefix):
    filepath = generateFilePath(path, filenameprefix)
    csvfile = open(filepath, 'a', newline='')
    writer = csv.writer(csvfile, delimiter=',')
    if os.stat(filepath).st_size == 0:
        writer.writerow(["Time", "Humidity", "Temperature", "BMP_temperature", "Pressure"])
    csvfile.close()
    return filepath

# read BMP180 sensor
def BMP180read():
    bmp_temperature, pressure = None, None
    while bmp_temperature is None or pressure is None:
        try:
            bmp_temperature, pressure = sensor.read_temperature(), sensor.read_pressure()
        except OSError:
            if debug: print("Cannot read BMP180 sensor")
        except NameError:
            if debug: print("BMP180 sensor not initialized, please check your sensor wiring.")
    return bmp_temperature, pressure

# read DHT11 sensor
def DHT11read():
    instTemperature, instHumidity = None, None
    while instHumidity is None or instTemperature is None:
        instHumidity, instTemperature = Adafruit_DHT.read(dsensor, pin)
        if instHumidity is None or instTemperature is None:
            if debug: print("Faulty DHT11 reading")
        else:
            humidity, temperature = instHumidity, instTemperature
            if debug: print("Good DHT11 reading")
    return instTemperature, instHumidity

# flash the status LED
def flashStatusLED(led, duration):
    while True:
        if statusLedEvent.is_set():
            led.on()
            terminateEvent.wait(duration)
            led.off()
            statusLedEvent.clear()
        if terminateEvent.is_set():
            break
        # stop thread from running too fast and eating CPU resources
        terminateEvent.wait(0.1)

# Ctrl-C KeyboardInterrupt signal handler
# set the Event to terminate all threads
def signal_handler(signum, frame):
    terminateEvent.set()

filepath = ""
newfiledate = datetime.min # initial value

# KeyboardInterrupt signal
signal.signal(signal.SIGINT, signal_handler)
# status LED
statusled = LED(18)
# status LED thread
statusLedThread = Thread(target=flashStatusLED, name="statusledthread", args=(statusled, flash_duration))
# status LED trigger event
statusLedEvent = Event()
# thread termination event
terminateEvent = Event()

statusLedThread.start()
# define DHT sensor type and pin
dsensor = Adafruit_DHT.DHT11
pin = 4
# initialize BMP180 sensor
# loop until the sensor is properly connected and detected
sensor = None
while sensor is None:
    try:
        sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
    except OSError:
        if debug: print("Cannot initialize BMP180 sensor")

# weather condition variables
temperature, humidity, bmp_temperature, pressure = -999, -999, -999, -999

statusled.on()

# read sensor and write to log file indefinitely
while True:
    # if a new day has started, create a new log file for the day
    if date.today() > newfiledate.date():
        if (date.today() - newfiledate.date()).days == 1:
            if debug:
                print("closing current file and opening a new file")
        else:
            if debug:
                print("Opening file initially")
        filepath = createOpenLogFile(path, filenameprefix)
        newfiledate = datetime.now()

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
        if debug:
            print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, humidity, temperature, bmp_temperature, pressure))

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
