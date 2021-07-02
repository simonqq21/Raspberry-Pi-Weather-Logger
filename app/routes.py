from flask import render_template, url_for, request, jsonify, send_from_directory
from app import App
from datetime import datetime, date
import os
import re
import subprocess
from app.config import APP_PATH, APP_DATA_PATH, REPORTS_FOLDER, PLOTS_FOLDER, EXPORTEDS_FOLDER, \
REPORT_PREFIX, PLOT_PREFIX, DAILY_TRENDS_PREFIX, EXPORT_PREFIX, AGG_EXPORT_PREFIX, FILENAME_DATEFORMAT
from app.config import APP_DATA_PATH, DB_FILENAME
from app.config import DEBUG
from app.db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from app.db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from app.db_module import WeatherLog, AggDayWeather
from app.db_module import getAllAggDates
from app.functions import exists

# ~ convert datestr received from javascript to ISO format
def fromisoformat(datestr):
	if re.search('\D', datestr[-1]) is not None:
		datestr = datestr[:-1]
	recvdate = datetime.fromisoformat(datestr).date()
	return recvdate

# download URL
@App.route('/download/<path:filename>')
def downloadFile(filename):
    return send_from_directory(APP_DATA_PATH, filename)

# render base page
@App.route('/', methods=['GET'])
@App.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

# render single day page
@App.route('/singleday', methods=['GET'])
def singleday():
	return render_template('singleday.html')

# render multiple day page
@App.route('/multiday', methods=['GET'])
def multiday():
	return render_template('multiday.html')

# render render about page
@App.route('/about', methods=['GET'])
def about():
	return render_template('about.html')

# return the latest row of weather data values
@App.route('/getLatestData', methods=['GET'])
def getLatestData():
	lastRow = WeatherLog.selectLast()
	if lastRow is not None:
		datadict = {"datetime": lastRow.datetime.datetime.isoformat(), "dhttemp": lastRow.log['dhttemp'].value, \
		"dhthumd": lastRow.log['dhthumd'].value, "bmptemp": lastRow.log['bmptemp'].value, \
		"bmppres": lastRow.log['bmppres'].value}
		print(datadict)
		return jsonify(datadict)
	return None

# return the URL of the image plot given the date, the URL of the report file given the date, and the
# download URLs of the exported csv data given the date
@App.route('/getURLsWithDate', methods=['GET'])
def getURLsWithDate():
# ~ get date from frontend
	datestr = request.args.get('date', )
	recvdate = fromisoformat(datestr)

	# if date not present in db, change date to maximum date inside the db
	datesList = getAllAggDates()
	if recvdate not in datesList:
		recvdate = max(datesList)
	print(recvdate)
	year = recvdate.year
	month = recvdate.month
	day = recvdate.day
	datestr = recvdate.strftime(FILENAME_DATEFORMAT)
	# report url
	report_url = '/download/' + REPORTS_FOLDER + REPORT_PREFIX + datestr + '.txt'
	# plot url
	plot_url = '/download/' + PLOTS_FOLDER + PLOT_PREFIX + datestr + '.png'

	# exported data files filenames
	exported_data_filename = EXPORTEDS_FOLDER + EXPORT_PREFIX + datestr + '_' + datestr + '.csv'
	aggexported_data_filename = EXPORTEDS_FOLDER + AGG_EXPORT_PREFIX + datestr + '_' + datestr + '.csv'

	# generate exported data if exported data does not exist
	if not exists(APP_DATA_PATH + exported_data_filename) or \
	not exists(APP_DATA_PATH + aggexported_data_filename):
		proc1 = subprocess.Popen('python3 {}/export_data.py -m1 {} -d1 {} -y1 {} -o'.format(APP_PATH, \
		month, day, year), stdout=subprocess.PIPE, shell=True)
		proc1.wait()
		output = proc1.communicate()[0]
		output = str(output, 'UTF-8')
		print(output)

	# create export data urls
	exported_data_url = '/download/' + exported_data_filename
	agg_exported_data_url = '/download/' + aggexported_data_filename

	jsondata = {"date": recvdate.isoformat(), "report_url": report_url, "plot_url": plot_url, \
	"exported_data_url": exported_data_url, "agg_exported_data_url": agg_exported_data_url}
	print(jsondata)
	return jsonify(jsondata)

# return the URL of the image plot given the date, the URL of the report file given the date, and the
# download URLs of the exported csv data given the date range
@App.route('/getURLsWithDateRange', methods=['GET'])
def getURLsWithDateRange():
# ~ get date from frontend
	datestartstr = request.args.get('datestart', )
	dateendstr = request.args.get('dateend', )
	recvdatestart = fromisoformat(datestartstr)
	recvdateend = fromisoformat(dateendstr)

	# if date not present in db, change date to maximum date inside the db
	datesList = getAllAggDates()
	if recvdatestart > recvdateend:
		recvdatestart, recvdateend = recvdateend, recvdatestart
	if recvdateend > max(datesList):
		recvdateend = max(datesList)
	if recvdatestart < min(datesList):
		recvdatestart = min(datesList)

	yearstart = recvdatestart.year
	monthstart = recvdatestart.month
	daystart = recvdatestart.day
	datestrstart = recvdatestart.strftime(FILENAME_DATEFORMAT)
	yearend = recvdateend.year
	monthend = recvdateend.month
	dayend = recvdateend.day
	datestrend = recvdateend.strftime(FILENAME_DATEFORMAT)

	# aggregated report and plot filenames
	report_filename = EXPORTEDS_FOLDER + DAILY_TRENDS_PREFIX + datestrstart + '_' + datestrend + '.txt'
	plot_filename = EXPORTEDS_FOLDER + DAILY_TRENDS_PREFIX + datestrstart + '_' + datestrend + '.png'

	# generate aggregated report and plot if exported data does not exist
	if not exists(APP_DATA_PATH + report_filename) or \
	not exists(APP_DATA_PATH + plot_filename):
		proc1 = subprocess.Popen('python3 {}/observe_daily_trends.py -m1 {} -d1 {} -y1 {} -m2 {} -d2 {} -y2 {} -g'.format(APP_PATH, \
		monthstart, daystart, yearstart, monthend, dayend, yearend), stdout=subprocess.PIPE, shell=True)
		proc1.wait()
		output = proc1.communicate()[0]
		output = str(output, 'UTF-8')

	# report url
	report_url = '/download/' + report_filename
	# plot url
	plot_url = '/download/' + plot_filename

	# exported data files filenames
	exported_data_filename = EXPORTEDS_FOLDER + EXPORT_PREFIX + datestrstart + '_' + datestrend + '.csv'
	aggexported_data_filename = EXPORTEDS_FOLDER + AGG_EXPORT_PREFIX + datestrstart + '_' + datestrend + '.csv'

	# generate exported data if exported data does not exist
	if not exists(APP_DATA_PATH + exported_data_filename) or \
	not exists(APP_DATA_PATH + aggexported_data_filename):
		proc2 = subprocess.Popen('python3 {}/export_data.py -m1 {} -d1 {} -y1 {} -m2 {} -d2 {} -y2 {}'.format(APP_PATH, \
		monthstart, daystart, yearstart, monthend, dayend, yearend), stdout=subprocess.PIPE, shell=True)
		proc2.wait()
		output = proc2.communicate()[0]
		output = str(output, 'UTF-8')
		print(output)

	# create export data urls
	exported_data_url = '/download/' + exported_data_filename
	agg_exported_data_url = '/download/' + aggexported_data_filename

	jsondata = {"datestart": recvdatestart.isoformat(), "dateend": recvdateend.isoformat(), "report_url": report_url, "plot_url": plot_url, \
	"exported_data_url": exported_data_url, "agg_exported_data_url": agg_exported_data_url}
	print(jsondata)
	return jsonify(jsondata)
