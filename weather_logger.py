import Adafruit_DHT
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
def generateFileName(filepathO):
    filenum = 0
    exists1 = 1
    while exists1 == 1:
        filepath = filepathO
        filepath += '{:04d}'.format(filenum)
        filepath += '.csv'
        filenum += 1
        exists1 = exists(filepath)
    return filepath

'''
specify weather log path, filename, and filepath
'''
path = "/home/pi/weather_logs/"
filenameprefix = "weather_log"
filepath = path + filenameprefix
filepath = generateFileName(filepath)
print(filepath)

# try to create the dir for logs
try:
    os.mkdir(path)
except FileExistsError:
    print("dir exists")
    pass

# open csv file and write the csv file header
csvfile = open(filepath, 'w', newline='')
writer = csv.writer(csvfile, delimiter=',')
writer.writerow(["Date", "Time", "Humidity", "Temperature"])
csvfile.close()

# define DHT sensor type
dsensor = Adafruit_DHT.DHT11
pin = 4

# read sensor and write to log file indefinitely
while True:
    try:
        # read sensor
        humidity, temperature = Adafruit_DHT.read(dsensor, pin)
        # errors may occur due to the precise timing required by the DHT11 sensor
        if humidity is not None and temperature is not None:
            csvfile = open(filepath, 'a', newline='')
            writer = csv.writer(csvfile, delimiter=',')
            dtnow = datetime.datetime.now()
            dateStr = dtnow.strftime('%m/%d/%Y')
            timeStr = dtnow.strftime('%H:%M:%S')
            if debug:
                print("{} {} {:0.3f}% {:0.3f}C".format(dateStr, timeStr, humidity, temperature))
            # write csv data to file
            writer.writerow([dateStr, timeStr, humidity, temperature])
            csvfile.close()
        else:
            if debug:
                print("Error")
        sleep(delay)
    except KeyboardInterrupt:
        print("Exiting")
        break;
csvfile.close()
