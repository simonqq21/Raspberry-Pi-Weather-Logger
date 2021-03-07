import os
import subprocess
import re
from datetime import timedelta, date, time, datetime
import csv

INTERVAL = 1

# subtracts two datetime.time objects, assuming they are from the same day
# returns time1 - time2
def subtract_time(time1, time2):
    return (datetime.combine(date.min, time1) - datetime.combine(date.min, time2))

# get the absolute path of the app and append the relative path inside the app dir
APP_PATH = os.path.abspath(os.path.dirname(__file__))
APP_DATA_PATH = APP_PATH + '/static/files/'
# absolute path of raw weather logs
weather_logs_path = APP_DATA_PATH + "weather_logs/"
today = datetime.now().date()
print(today.strftime("%m%d%Y"))

# get the list of files in the weather log dir and sort it
filenames = os.listdir(weather_logs_path)
filenames.sort()

for filename in filenames:
    # get files starting with "weather_log"
    if re.search("^weather_log", filename) is not None:
        # get the date of the log
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        # if the date is before today, check it and if not yet averaged, overwrite it with averaged data
        if date1 < today:
            print(filename + " " + re.search("\d{8}", filename).group())
            # get the year, month, and day to pass as parameters
            year = date1.year
            month = date1.month
            day = date1.day

            # open file to check the time intervals
            raw_file = open(weather_logs_path + filename, 'r')
            raw_file_reader = csv.reader(raw_file, delimiter=',')
            next(raw_file_reader);

            # get the first row of the data
            row1 = next(raw_file_reader);
            time0 = datetime.strptime(row1[0], "%H:%M:%S").time()
            time1 = time0

            # check if the data is raw or has been previously averaged by checking the difference
            # in time per reading.
            for row in raw_file_reader:
                time0 = time1
                time1 = datetime.strptime(row[0], "%H:%M:%S").time()
                # If it is not exactly 1 minute, call the process to average it.
                if subtract_time(time1, time0).seconds < INTERVAL * 60:
                    print("RAW")
                    proc1 = subprocess.Popen('python3 {}/weatherlogaverage.py -m {} -d {} -y {} -o'
                    .format(APP_PATH, month, day, year), stdout=subprocess.PIPE, shell=True)
                    output = proc1.communicate()[0]
                    output = str(output, 'UTF-8')
                    print(output)
                    break;
