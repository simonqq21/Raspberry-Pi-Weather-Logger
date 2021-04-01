import sqlite3
import os
import re
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME
from config import SUMMARIES_FOLDER, SUMMARY_PREFIX
from config import WEATHER_DATA, STATS
from functions import read_summary

debug = True

'''
This python program inserts the weather data statistics per day (mean, std, min, max) into
an sqlite3 database in the data directory. It checks if the data for a specific day already
exists in the db. It reads the data per day from summary files, then inserts all nonexistent
days into the db. This program is automatically executed by the weather logger, which is started
on boot.
'''

# connect to sqlite db
con = sqlite3.connect(APP_DATA_PATH + DB_FILENAME)
# set connection to return query results as Rows
con.row_factory = sqlite3.Row
cur = con.cursor()

#create dates table if not exists
cur.execute('CREATE TABLE IF NOT EXISTS dates (id INTEGER NOT NULL PRIMARY KEY,date TEXT NOT NULL)')
# create weather data tables if not exists
for data in WEATHER_DATA:
    sql = ('CREATE TABLE IF NOT EXISTS {} (id INTEGER NOT NULL PRIMARY KEY, {} REAL, \
    {} REAL, {} REAL, {} REAL, FOREIGN KEY(id) REFERENCES dates(id))'.format(data, *STATS))
    cur.execute(sql)

# get the list of files in the summary file dir and sort it
summary_files_path = APP_DATA_PATH + SUMMARIES_FOLDER
filenames = os.listdir(summary_files_path)
filenames.sort()

# data1 is data from the summary files
# data2 is data from the database
data1, data2 = {}, {}
for filename in filenames:
    # get the name of a summary file
    if re.search("^" + SUMMARY_PREFIX, filename) is not None:
        # get date
        date1 = datetime.strptime(re.search("\d{8}", filename).group(), '%m%d%Y').date();
        # convert date to ISO format for storage to DB
        date1str = date1.strftime('%Y-%m-%d')
        if debug:
            print(date1str)
        # read the summary file into dictionary
        data1 = read_summary(filename)

        # look for the date in the db
        cur.execute('SELECT * FROM dates WHERE dates.date = ?', (date1str,))
        # if date does not exist, insert it into dates table
        if cur.fetchone() is None:
            cur.execute('INSERT INTO dates(date) VALUES(?)', (date1str,))

        # for each weather data table
        for data in WEATHER_DATA:
            data2 = {}
            # get the weather data from the db that is associated with the date
            sql = "SELECT * FROM {} WHERE {}.id = (SELECT id FROM dates WHERE dates.date = \
            '{}')".format(data, data, date1str)
            cur.execute(sql)
            r = cur.fetchone()
            # convert query results into dictionary format

            if r is not None:
                data2 = dict(zip(r.keys(), tuple(r)))
                # remove the id value to test for equality with the database data
                data2 = {key: data2[key] for key in data2.keys() if key != 'id'}

            # if there are any differences between the data from the summary file and the
            # data from the db file or if the data for a certain date does not exist, update it.
            if data1[data] != data2:
                if debug:
                    print(data1[data])
                    print(data2)
                    print()

                # insert data on receiving empty result
                if data2 == {}:
                    sql = "INSERT INTO {}(id, {}, {}, {}, {}) VALUES ((SELECT id FROM dates \
                    where dates.date = '{}'), ?, ?, ?, ?)".format(data, *STATS, date1str)
                    cur.execute(sql, tuple(data1[data][stat] for stat in STATS))
                # update data on receiving different nonempty result
                else:
                    sql = "UPDATE {} SET {}=?, {}=?, {}=?, {}=? WHERE id=(SELECT id FROM dates \
                    where dates.date = '{}')".format(data, *STATS, date1str)
                    cur.execute(sql, tuple(data1[data][stat] for stat in STATS))

con.commit()
con.close()
print('DONE')
