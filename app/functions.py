import os
import datetime
from datetime import datetime, date, timedelta
import csv
import subprocess
import re
from config import HEADER, STATS
from config import APP_DATA_PATH, APP_PATH
from config import DEBUG

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        print("file does not exist")
        return 0
    f.close()
    return 1

# append newline to string
def appendNewline(str):
    return str + '\n'

# return True if file size is below a certain size, return False otherwise
def isEmpty(filename, size):
    if DEBUG:
        print(os.stat(filename).st_size)
    if os.stat(filename).st_size <= size:
        return True
    return False

# subtracts two datetime.time objects, assuming they are from the same day
# returns time1 - time2
def subtract_time(time1, time2):
    return (datetime.combine(date.min, time1) - datetime.combine(date.min, time2))

# generate csv filename with date today
# def generateFileName(filenameprefix):
#     filename = filenameprefix + date.today().strftime('%m%d%Y') + '.csv'
#     if DEBUG: print(filename)
#     return filename

# create the complete file path of the log file
# try to create the dir for logs if it does not exist
# def generateFilePath(path, filenameprefix):
#     if path != '':
#         if not os.path.exists(path):
#             os.mkdir(path)
#     filename = generateFileName(filenameprefix)
#     filepath = path + filename
#     return filepath

# # create a new csv file and write the csv file header
# def createOpenLogFile(path, filenameprefix):
#     filepath = generateFilePath(path, filenameprefix)
#     csvfile = open(filepath, 'a', newline='')
#     writer = csv.writer(csvfile, delimiter=',')
#     # write the file header only if the file is empty
#     if os.stat(filepath).st_size == 0:
#         writer.writerow(["Time"] + WEATHER_DATA_HEADER_DICT)
#     csvfile.close()
#     return filepath

# call the report generation script with the date parameters
def generatereport(month, day, year):
    proc1 = subprocess.Popen('python3 {}/weatherdataanalyzer.py -m {} -d {} -y {} -g'.format
    (APP_PATH, month, day, year), shell=True)
    proc1.wait()

# delete any matching files in a given path
def deleteAllSimilar(path, prefix):
    filenames = os.listdir(path)
    for filename in filenames:
        if re.search('^' + prefix, filename) is not None:
            os.remove(path + filename)
