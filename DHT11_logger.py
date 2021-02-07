import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from time import sleep
import csv
import os
import datetime

debug = False
delay = 4

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        print("file does not exist")
        return 0
    f.close()
    return 1

# # create csv file
# # "dht_log" + 4 digit number with leading zeroes starting from 1 + ".csv"
# def generateFileName(filepathO):
#     filenum = 0
#     exists1 = 1
#     while exists1 == 1:
#         filepath = filepathO
#         filepath += '{:04d}'.format(filenum)
#         filepath += '.csv'
#         filenum += 1
#         exists1 = exists(filepath)
#     return filepath

def generateFileName(filenameprefix0):
    dnow = datetime.date.today()
    filepath = filenameprefix0 + dnow.strftime('%m%d%Y') + '.csv'
    return filepath

path = "/home/pi/dht_logs/"
filenameprefix = "dht_log"
filepath = path + generateFileName(filenameprefix)
print(filepath)

# try to create the dir for logs
try:
    os.mkdir(path)
except FileExistsError:
    pass

# open csv file
# if exists(filepath) == 0:
#     csvfile = open(filepath, 'w', newline='')
#     writer = csv.writer(csvfile, delimiter=',')
#     writer.writerow(["Date", "Time", "Humidity", "Temperature"])
#     csvfile.close()
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
        humidity, temperature = Adafruit_DHT.read(dsensor, pin)
        bmp_temperature, pressure = sensor.read_temperature(), sensor.read_pressure()
        if humidity is not None and temperature is not None and bmp_temperature is not None and pressure is not None:
            csvfile = open(filepath, 'a', newline='')
            writer = csv.writer(csvfile, delimiter=',')
            dtnow = datetime.datetime.now()
            timeStr = dtnow.strftime('%H:%M:%S')
            if debug:
                print("{} {:0.3f}% {:0.3f}C {:0.3f}C {:0.3f}Pa".format(timeStr, humidity, temperature, bmp_temperature, pressure))
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
