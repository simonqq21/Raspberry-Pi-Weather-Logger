from flask import render_template, url_for, request, jsonify, send_from_directory
from app import App
from datetime import datetime, date
import os
import re
import subprocess
from app.config import APP_PATH, APP_DATA_PATH, STATIC_PATH, REPORTS_FOLDER, PLOTS_FOLDER, EXPORTEDS_FOLDER, \
REPORT_PREFIX, PLOT_PREFIX, DAILY_TRENDS_PREFIX, EXPORT_PREFIX, AGG_EXPORT_PREFIX, FILENAME_DATEFORMAT
from app.config import APP_DATA_PATH, DB_FILENAME
from app.config import DEBUG
from app.db_module import DateTimeRow, DHTTemperature, DHTHumidity, BMPTemperature, BMPPressure
from app.db_module import DateRow, AggDHTTemperature, AggDHTHumidity, AggBMPTemperature, AggBMPPressure
from app.db_module import WeatherLog, AggDayWeather
from app.db_module import getAllAggDates
import json 

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
	# generate exported data 
	proc1 = subprocess.Popen('python3 {}/export_data.py -m1 {} -d1 {} -y1 {} -o'.format(APP_PATH, \
	month, day, year), stdout=subprocess.PIPE, shell=True)
	proc1.wait()
	output = proc1.communicate()[0]
	output = str(output, 'UTF-8')
	print(output)
	exported_data_url = '/download/' + EXPORTEDS_FOLDER + EXPORT_PREFIX + datestr + '_' + datestr + '.csv'
	agg_exported_data_url = '/download/' + EXPORTEDS_FOLDER + EXPORT_PREFIX + datestr + '_' + datestr + '.csv'
	
	jsondata = {"date": recvdate.isoformat(), "report_url": report_url, "plot_url": plot_url, \
	"exported_data_url": exported_data_url, "agg_exported_data_url": agg_exported_data_url}
	print(jsondata)
	return jsonify(jsondata)

# return the URL of the image plot given the date, the URL of the report file given the date, and the 
# download URLs of the exported csv data given the date range
@App.route('/getURLsWithDateRange', methods=['GET'])
def getURLsWithDateRange():
	print(request.form('date'))
	pass 



# ~ '''
# ~ weather log history page
# ~ if GET request, ask user for date
# ~ else if POST request, display data on that date
# ~ '''
# ~ @App.route('/history', methods=['GET', 'POST'])
# ~ def log_history():
    # ~ if DEBUG:
        # ~ print(request.method)

    # ~ if request.method == 'GET':
        # ~ # get all raw weather log dates and save them as an array
        # ~ dates = []
        # ~ for file in os.listdir(APP_DATA_PATH + WEATHER_LOGS_FOLDER):
            # ~ if re.search("^" + RAW_LOG_PREFIX, file) is not None:
                # ~ # format the string into a date
                # ~ date1 = re.search("\d{8}", file).group()
                # ~ if DEBUG:
                    # ~ print(date1)
                # ~ dates.append(date1[:2] + '/' + date1[2:4] + '/' + date1[4:])

        # ~ # sort dates
        # ~ dates.sort()

        # ~ # display the page
        # ~ return render_template("weather_logs.html", dates=dates)

    # ~ # POST request
    # ~ else:
        # ~ # get the date the user selected
        # ~ rawdatadate = request.form['rawdatadate']
        # ~ '''
        # ~ things to pass:
        # ~ mean, std, min, and max for temperature, pressure, and humidity
        # ~ minimum and maximum times of the day for temperature, pressure, and humidity
        # ~ averaged raw weather data URL
        # ~ weather report URL
        # ~ plot image static URL
        # ~ '''
        # ~ # get month, day, and year
        # ~ month, day, year = int(rawdatadate[:2]), int(rawdatadate[3:5]), int(rawdatadate[6:])
        # ~ # convert to date object
        # ~ lDate = date(year, month, day)
        # ~ # get date string without the slashes
        # ~ rawdatadate = rawdatadate[:2] + rawdatadate[3:5] + rawdatadate[6:]
        # ~ # URLs
        # ~ summary_path, report_path, plot_url = "", "", ""

        # ~ # get the absolute summary file URL
        # ~ for filename in os.listdir(APP_DATA_PATH + SUMMARIES_FOLDER):
            # ~ if rawdatadate in filename:
                # ~ summary_path = APP_DATA_PATH + SUMMARIES_FOLDER + filename
                # ~ print(summary_path)

        # ~ # get the download report file URL
        # ~ for filename in os.listdir(APP_DATA_PATH + REPORTS_FOLDER):
            # ~ if rawdatadate in filename:
                # ~ report_path = REPORTS_FOLDER + filename
                # ~ print(report_path)

        # ~ # get the download plot file URL
        # ~ for filename in os.listdir(APP_DATA_PATH + PLOTS_FOLDER):
            # ~ if rawdatadate in filename:
                # ~ plot_url = PLOTS_FOLDER + filename
                # ~ print(plot_url)

        # ~ # if one of the required generated data does not exist
        # ~ if summary_path == '' or plot_url == '' or report_path == '' or \
        # ~ lDate == date.today():
            # ~ if DEBUG:
                # ~ print("today!!!")
                # ~ print("summary file or plot image file does not exist")
            # ~ # call process to generate the information
            # ~ proc1 = subprocess.Popen('python3 {}/weatherdataanalyzer.py -m {} -d {} -y {} \
            # ~ -g'.format(APP_PATH, month, day, year), stdout=subprocess.PIPE, shell=True)
            # ~ proc1.wait()
            # ~ output = proc1.communicate()[0]
            # ~ output = str(output, 'UTF-8')
            # ~ print(output)
            # ~ # get the paths of the generated files
            # ~ summary_path = APP_DATA_PATH + SUMMARIES_FOLDER + SUMMARY_PREFIX + rawdatadate + '.txt'
            # ~ report_path = REPORTS_FOLDER + REPORT_PREFIX + rawdatadate + '.txt'
            # ~ plot_url = PLOTS_FOLDER + PLOT_PREFIX + rawdatadate + '.png'

        # ~ # raw csv data path
        # ~ processed_data_path = WEATHER_LOGS_FOLDER + PROCESSED_LOG_PREFIX + rawdatadate + '.csv'

        # ~ # process the summary
        # ~ summarydata = ''
        # ~ if summary_path != "":
            # ~ with open(summary_path, 'r') as summaryfile:
                # ~ summarydata = summaryfile.readlines()

        # ~ # data dictionary
        # ~ weather_data_dict = {}
        # ~ header = []

        # ~ for line in summarydata:
            # ~ curr_header = line.split(':')[0]
            # ~ header.append(curr_header)
            # ~ weather_data_dict[curr_header] = {}
            # ~ data = line.strip('\n').split(':', maxsplit=1)[1].split(',',maxsplit=4)
            # ~ weather_data_dict[curr_header]['mean'] = data[0]
            # ~ weather_data_dict[curr_header]['std'] = data[1]
            # ~ weather_data_dict[curr_header]['min'] = data[2]
            # ~ weather_data_dict[curr_header]['max'] = data[3]

            # ~ weather_data_dict[curr_header]['min_times'] = data[4].strip('[').strip(']').split('][')[0].split(',')[:-1]
            # ~ weather_data_dict[curr_header]['max_times'] = data[4].strip('[').strip(']').split('][')[1].split(',')[:-1]

        # ~ print(weather_data_dict)
        # ~ print(rawdatadate)
            # ~ # print(summary_path)
            # ~ # print(plot_url)
            # ~ # print(report_path)
            # ~ # print(processed_data_path)

        # ~ return jsonify(data=weather_data_dict, plot_url=plot_url, report_path=report_path,
        # ~ data_path=processed_data_path)

