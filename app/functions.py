import os
import datetime
from datetime import datetime, date, timedelta
import csv
import subprocess
import re
try:
    from config import HEADER, STATS
    from config import APP_DATA_PATH, APP_PATH
    from config import DEBUG
except:
    from app.config import HEADER, STATS
    from app.config import APP_DATA_PATH, APP_PATH
    from app.config import DEBUG

# check if a file exists
def exists(filename):
    try:
        f = open(filename, 'r')
    except IOError:
        print("file does not exist")
        return 0
    f.close()
    return 1

# append  to string
def newline(str):
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

# call the aggregate generation script with the date parameters
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
