from flask import render_template, url_for, request, jsonify
from app import App
from datetime import datetime
import os
import re

# get the absolute path of the app and append the relative path inside the app dir
APP_DATA_PATH = os.path.abspath(os.path.dirname(__file__)) + '/static/files/'
# absolute path of raw weather logs
weather_logs_path = APP_DATA_PATH + "weather_logs/"
# absolute path of summarized data
summaries_path = APP_DATA_PATH + "summaries/"
# absolute path of weather plot images
plots_path = APP_DATA_PATH + "plots/"

@App.route('/')
@App.route('/index')
def index():
    return render_template("index.html")

# if http get request, serve the empty page and ask user to load raw data
# if http post request,
@App.route('/history', methods=['GET', 'POST'])
def log_history():
    print(request.method)
    if request.method == 'GET':
        # get all raw weather logs and save them as an array
        dates = []
        for file in os.listdir(raw_logs_path):
            if "weather_log" in file and ".csv" in file:
                # format the string into a date
                dates.append(file[11:13] + '/' + file[13:15] + '/' + file[15:19])

        # sort dates
        dates.sort()

        return render_template("weather_logs.html", dates=dates)

    else:
        print(request)
        rawdatadate = request.form['rawdatadate']
        '''
        things to pass:
        mean, std, min, and max for temperature, pressure, and humidity
        plot image file URL
        minimum and maximum times of the day for temperature, pressure, and humidity
        '''
        rawdatadate = rawdatadate[:2] + rawdatadate[3:5] + rawdatadate[6:]
        summary_path, plot_path = "", ""

        # get the summary file URL
        for filename in os.listdir(summaries_path):
            if rawdatadate in filename:
                summary_path = summaries_path + filename

        plot_url = ""
        # get the plot file URL
        for filename in os.listdir(plots_path):
            if rawdatadate in filename:
                plot_path = plots_path + filename
                plot_url = filename

        summarydata = ''

        # process the summary
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

        # debug
        # print(weather_data_dict)
        # print(rawdatadate)
        # print(summary_path)
        # print(plot_path)

        return jsonify(data=weather_data_dict, plot_url=plot_url, header=header)
        # return render_template("weather_logs.html", data=weather_data_dict, plot_filename=plot_filename)
