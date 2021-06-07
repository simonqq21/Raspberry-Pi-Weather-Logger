import os
import datetime
from datetime import datetime, date, timedelta
import csv
import subprocess
import re
from config import WEATHER_DATA, STATS
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
#         writer.writerow(["Time"] + WEATHER_DATA)
#     csvfile.close()
#     return filepath

# process a summary file and return the data as a dictionary
# def read_summary(filename):
#     summary_path = APP_DATA_PATH + SUMMARIES_FOLDER + filename
#     # read file
#     with open(summary_path, 'r') as summaryfile:
#         summarydata = summaryfile.readlines()
#     # data dictionary
#     weather_data_dict = {}
#     # extract data
#     for line in summarydata:
#         curr_header = line.split(':')[0]
#         weather_data_dict[curr_header] = {}
#         data = line.strip('\n').split(':', maxsplit=1)[1].split(',',maxsplit=4)
#         # convert data to float so it can be compared to the data from the db
#         for i in range(len(STATS)):
#             weather_data_dict[curr_header][STATS[i]] = float(data[i])
#     # fill in the data that does not exist with None values
#     # used so that it will be easy to add more sensors and weather data columns in the future
#     for d in WEATHER_DATA:
#         if d not in weather_data_dict:
#             weather_data_dict[d] = {}
#             for i in range(len(STATS)):
#                 weather_data_dict[d][STATS[i]] = None
#     # print(weather_data_dict)
#     return weather_data_dict

# call the report generation script with the date parameters
# def generatereport(month, day, year):
#     proc1 = subprocess.Popen('python3 {}/weatherdataanalyzer.py -m {} -d {} -y {} -g'.format
#     (APP_PATH, month, day, year), shell=True)
#     proc1.wait()

# delete any matching files in a given path
# def deleteAllSimilar(path, prefix):
#     filenames = os.listdir(path)
#     for filename in filenames:
#         if re.search('^' + prefix, filename) is not None:
#             os.remove(path + filename)
