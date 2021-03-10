from flask import render_template, url_for, request, jsonify
from app import App
from datetime import datetime
import os
import re
from app.config import APP_PATH, APP_DATA_PATH, STATIC_PATH, \
WEATHER_LOGS_PATH, SUMMARIES_PATH, REPORTS_PATH, PLOTS_PATH, \
WEATHER_LOGS_STATIC_PATH, SUMMARIES_STATIC_PATH, REPORTS_STATIC_PATH, PLOTS_STATIC_PATH, \
RAW_LOG_PREFIX, PROCESSED_LOG_PREFIX, SUMMARY_PREFIX, REPORT_PREFIX, PLOT_PREFIX
import subprocess

DEBUG = True

@App.route('/')
@App.route('/index')
def index():
    return render_template("index.html")

# if http get request, serve the empty page and ask user to load raw data
# if http post request,
@App.route('/history', methods=['GET', 'POST'])
def log_history():
    if DEBUG:
        print(request.method)
    if request.method == 'GET':
        # get all raw weather logs and save them as an array
        dates = []
        for file in os.listdir(WEATHER_LOGS_PATH):
            if re.search("^" + RAW_LOG_PREFIX, file) is not None:
                # format the string into a date
                date1 = re.search("\d{8}", file).group()
                if DEBUG:
                    print(date1)
                dates.append(date1[:2] + '/' + date1[2:4] + '/' + date1[4:])

        # sort dates
        dates.sort()

        return render_template("weather_logs.html", dates=dates)

    else:
        rawdatadate = request.form['rawdatadate']
        '''
        things to pass:
        mean, std, min, and max for temperature, pressure, and humidity
        plot image file URL
        minimum and maximum times of the day for temperature, pressure, and humidity
        '''
        month, day, year = rawdatadate[:2], rawdatadate[3:5], rawdatadate[6:]
        rawdatadate = rawdatadate[:2] + rawdatadate[3:5] + rawdatadate[6:]
        summary_path, report_path, plot_url = "", "", ""

        # get the summary file URL
        for filename in os.listdir(SUMMARIES_PATH):
            if rawdatadate in filename:
                summary_path = SUMMARIES_PATH + filename

        # get the report file URL
        for filename in os.listdir(REPORTS_PATH):
            if rawdatadate in filename:
                report_path = REPORTS_STATIC_PATH + filename

        # get the plot file URL
        for filename in os.listdir(PLOTS_PATH):
            if rawdatadate in filename:
                plot_url = PLOTS_STATIC_PATH + filename

        if summary_path == '' or plot_url == '' or report_path == '':
            if DEBUG:
                print("summary file or plot image file does not exist")
            proc1 = subprocess.Popen('python3 {}/weatherdataanalyzer.py -m {} -d {} -y {} \
            -g'.format(APP_PATH, month, day, year), stdout=subprocess.PIPE, shell=True)
            proc1.wait()
            output = proc1.communicate()[0]
            output = str(output, 'UTF-8')
            print(output)
            summary_path = SUMMARIES_PATH + SUMMARY_PREFIX + rawdatadate + '.txt'
            report_path = REPORTS_STATIC_PATH + REPORT_PREFIX + rawdatadate + '.txt'
            plot_url = PLOTS_STATIC_PATH + PLOT_PREFIX + rawdatadate + '.png'

        # raw csv data path
        processed_data_path = WEATHER_LOGS_STATIC_PATH + PROCESSED_LOG_PREFIX + rawdatadate + '.csv'

        # process the summary
        summarydata = ''
        if summary_path != "":
            with open(summary_path, 'r') as summaryfile:
                summarydata = summaryfile.readlines()

        # data dictionary
        weather_data_dict = {}
        header = []

        for line in summarydata:
            curr_header = line.split(':')[0]
            header.append(curr_header)
            weather_data_dict[curr_header] = {}
            data = line.strip('\n').split(':', maxsplit=1)[1].split(',',maxsplit=4)
            weather_data_dict[curr_header]['mean'] = data[0]
            weather_data_dict[curr_header]['std'] = data[1]
            weather_data_dict[curr_header]['min'] = data[2]
            weather_data_dict[curr_header]['max'] = data[3]

            weather_data_dict[curr_header]['min_times'] = data[4].strip('[').strip(']').split('][')[0].split(',')[:-1]
            weather_data_dict[curr_header]['max_times'] = data[4].strip('[').strip(']').split('][')[1].split(',')[:-1]

        if DEBUG:
            print(weather_data_dict)
            print(rawdatadate)
            print(summary_path)
            print(plot_url)
            print(report_path)
            print(processed_data_path)

        return jsonify(data=weather_data_dict, plot_url=plot_url, report_path=report_path,
        data_path=processed_data_path)
