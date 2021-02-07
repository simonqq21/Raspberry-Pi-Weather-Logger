import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from time import sleep
import csv
import os
import datetime

debug = False # setting debug to True will print data
delay = 4 # logging delay

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
def generateFileName(filenameprefix0):
    dnow = datetime.date.today()
    filepath = filenameprefix0 + dnow.strftime('%m%d%Y') + '.csv'
    return filepath

'''
specify weather log path, filename, and filepath
'''
path = "/home/pi/weather_logs/"
filenameprefix = "weather_log"
filepath = path + generateFileName(filenameprefix)
print(filepath)

# try to create the dir for logs
try:
    os.mkdir(path)
except FileExistsError:
    print("dir exists")
    pass

# open csv file and write the csv file header
csvfile = open(filepath, 'a', newline='')
writer = csv.writer(csvfile, delimiter=',')
if os.stat(filepath).st_size == 0:
    writer.writerow(["Time", "Humidity", "Temperature", "BMP_temperature", "Pressure"])
csvfile.close()

# define DHT sensor type
dsensor = Adafruit_DHT.DHT11
pin = 4
sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

# read sensor and write to log file indefinitely
while True:
    try:
        # read sensors
        humidity, temperature = Adafruit_DHT.read(dsensor, pin)
        bmp_temperature, pressure = sensor.read_temperature(), sensor.read_pressure()
        # errors may occur due to the precise timing required by the DHT11 sensor
        if humidity is not None and temperature is not None and bmp_temperature is not None and pressure is not None:
            csvfile = open(filepath, 'a', newline='')
            writer = csv.writer(csvfile, delimiter=',')
            dtnow = datetime.datetime.now()
            timeStr = dtnow.strftime('%H:%M:%S')
            if debug:
                print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, humidity, temperature, bmp_temperature, pressure))
            # write csv data to file
            writer.writerow([timeStr, humidity, temperature, bmp_temperature, pressure])
            csvfile.close()
        else:
            if debug:
                print("Error")
        sleep(delay)
    except KeyboardInterrupt:
        print("Exiting")
        break;
csvfile.close()
