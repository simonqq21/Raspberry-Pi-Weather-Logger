import os
import subprocess
import re
from datetime import timedelta, date, time, datetime

# get the absolute path of the app and append the relative path inside the app dir
APP_DATA_PATH = os.path.abspath(os.path.dirname(__file__)) + '/static/files/'
# absolute path of raw weather logs
weather_logs_path = APP_DATA_PATH + "weather_logs/"
today = datetime.now().date()
print(today.strftime("%m%d%Y"))

filenames = os.listdir(weather_logs_path)
filenames.sort()

for filename in filenames:
    if re.search("^weather_log", filename) is not None:
        # print(filename + " " + re.search("\d{8}", filename).group())
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        if date1 < today:
            print(filename + " " + re.search("\d{8}", filename).group())
