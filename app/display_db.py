import sqlite3
from datetime import datetime, date
from config import APP_DATA_PATH, DB_FILENAME

debug = True

# connect to sqlite db
con = sqlite3.connect(APP_DATA_PATH + DB_FILENAME)
# set connection to return query results as Rows
con.row_factory = sqlite3.Row
cur = con.cursor()

# list all tables in the db
tables = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%"')
for t in tables:
    print(list(t))

results = cur.execute('SELECT d.id, d.date, \
t.mean AS t_mean, t.std AS t_std, t.min AS t_min, t.max AS t_max, \
btp.mean AS btp_mean, btp.std AS btp_std, btp.min AS btp_min, btp.max AS btp_max, \
h.mean AS h_mean, h.std AS h_std, h.min AS h_min, h.max AS h_max, \
p.mean AS p_mean, p.std AS p_std, p.min AS p_min, p.max AS p_max, \
w.mean AS w_mean, w.std AS w_std, w.min AS w_min, w.max AS w_max \
FROM dates d \
JOIN temperature t ON d.id = t.id \
JOIN bmp_temperature btp ON d.id = btp.id \
JOIN humidity h ON d.id = h.id \
JOIN pressure p ON d.id = p.id \
JOIN windspeed w on d.id = w.id')

for row in results:
    dict_row = dict(row)
    print({key: dict_row[key] for key in dict_row if key in ('id', 'date')})
    print({key: dict_row[key] for key in dict_row if key in ('h_mean', 'h_std', 'h_min', 'h_max')})
    print({key: dict_row[key] for key in dict_row if key in ('t_mean', 't_std', 't_min', 't_max')})
    print({key: dict_row[key] for key in dict_row if key in ('btp_mean', 'btp_std', 'btp_min', 'btp_max')})
    print({key: dict_row[key] for key in dict_row if key in ('p_mean', 'p_std', 'p_min', 'p_max')})
    print({key: dict_row[key] for key in dict_row if key in ('w_mean', 'w_std', 'w_min', 'w_max')})
    print()

results = cur.execute('SELECT * FROM dates')
for row in results:
    print(dict(row))

con.close()
