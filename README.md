# Raspberry-Pi-Weather-Logger

## Introduction
This application logs weather data - temperature, barometric pressure, and relative humidity data from sensors connected to a Raspberry Pi. The weather data for each day is autonomously and continuously logged into CSV files, continuing even after an unplanned reboot cycle. The raw weather data will be averaged into continuous time intervals for consistency. Weather reports for a particular day can be generated by getting the mean, standard deviation, minimum value, maximum value, and times of the day when the minimum and maximum values of each data column were recorded, and then these visualized as a graph. The summarized textual results of this application is saved into a formatted text file for use with a web front-end. This application is a hobby project intended for exploration and educational purposes.

## Sample Output
### Plot Image
![weather data for 02192021](/app/static/files/plots/plot_02192021.png)

### Raw CSV File Snippet
    Time,Humidity,Temperature,BMP_temperature,Pressure
    00:00:00,27.900,29.000,27.610,101036.400
    00:05:00,28.900,29.000,27.550,101036.900
    00:10:00,28.600,29.000,27.510,101035.100
    00:15:00,29.111,29.000,27.500,101037.111
    00:20:00,28.100,28.700,27.490,101028.100
    00:25:00,27.300,29.000,27.460,101023.200
    00:30:00,28.200,28.900,27.500,101024.600
    00:35:00,28.000,28.778,27.500,101021.778
    00:40:00,27.800,28.400,27.430,101010.400
    00:45:00,27.500,28.500,27.400,101010.900
    00:50:00,27.778,28.111,27.400,101009.222
    00:55:00,27.100,28.000,27.400,101008.800
    01:00:00,27.600,28.100,27.320,101002.600
    ...

### Sample Human Readable Report
    Day: 02/19/2021
    Humidity mean: 22.273
    Humidity std: 7.124
    Humidity min: 14.800
    Humidity max: 36.200

    Temperature mean: 28.618
    Temperature std: 0.789
    Temperature min: 27.000
    Temperature max: 30.000

    BMP_temperature mean: 27.455
    BMP_temperature std: 0.718
    BMP_temperature min: 26.340
    BMP_temperature max: 29.000

    Pressure mean: 100971.975
    Pressure std: 92.142
    Pressure min: 100786.700
    Pressure max: 101106.667

    Times of the day with minimum Humidity
    13:50:00
    Times of the day with maximum Humidity
    08:55:00

    Times of the day with minimum Temperature
    08:40:00
    Times of the day with maximum Temperature
    13:20:00
    13:25:00
    13:30:00
    13:35:00
    13:40:00
    13:45:00
    13:50:00
    13:55:00
    14:00:00
    14:05:00
    14:10:00
    14:15:00
    14:20:00
    14:25:00
    14:30:00
    14:35:00
    14:40:00
    14:45:00
    14:50:00
    14:55:00
    15:00:00
    15:05:00
    15:10:00
    15:15:00
    15:20:00
    15:25:00
    15:30:00
    15:35:00
    15:40:00
    15:45:00
    15:50:00
    15:55:00
    16:00:00
    16:05:00
    16:10:00
    16:15:00
    16:20:00
    16:25:00
    16:30:00
    16:35:00
    16:40:00
    16:45:00
    16:50:00
    16:55:00
    17:00:00
    17:05:00
    17:10:00
    17:15:00
    17:20:00
    17:30:00

    Times of the day with minimum BMP_temperature
    08:05:00
    Times of the day with maximum BMP_temperature
    15:40:00

    Times of the day with minimum Pressure
    14:55:00
    Times of the day with maximum Pressure
    09:30:00

    Creating weather data graph
    summary_02192021.txt

### Python libraries used for this application:
- Stock Python
    - **argparse** - parse command line arguments
    - **csv** - read and write CSV files
    - **datetime** - standard date and time in Python
    - **os** - miscellaneous operating system and filesystem functions
    - **signal** - interpret the Ctrl-C when run in console mode to safely shutdown application
    - **subprocess** - call a process within a Python script
    - **threading** - run multiple threads concurrently
    - **time** - time delay
    - **re** - regex module

- 3rd party
    - **Adafruit_DHT** - DHT11 sensor library for the Raspberry Pi
    - **Adafruit_BMP.BMP085** - BMP180 sensor library for the Raspberry Pi
    - **gpiozero** - high level Python GPIO API for the Raspberry Pi
    - **matplotlib** - data visualization
    - **numpy** - fast contiguous arrays and array operations in Python
    - **Flask** - Python web microframework

*This application is written in Python and utilizes 3rd party sensor libraries from Adafruit.*

## Hardware Setup
This application runs on a Raspberry Pi single board computer (SBC). The Raspberry Pi is the computer used for this application mainly because of its general purpose IO (GPIO) pins, which allow it to interface with external electronics programmatically. It also draws very little power and is well suited for being a lightweight always-on datalogger and web server. The external hardware needed for this application are a **DHT11 1-wire temperature and humidity sensor**, a **BMP180 i2c precision temperature and barometric pressure sensor**, a **DS1307 i2c real time clock (RTC)**, and an **indicator LED** that flashes every time a row of sensor data is logged. Equivalent components can be used in place when these are not available, but the libraries and code may have to be altered.

### Electrical Connections:
#### DHT11 --> RPi
- VCC --> 5V
- GND --> GND
- Data --> GPIO4
#### BMP180 --> RPi
- VCC --> 3V3 **WARNING!!! DO NOT CONNECT TO 5V OR THE SENSOR WILL BE DAMAGED!**
- GND --> GND
- SDA --> GPIO2
- SCL --> GPIO3
#### DS1307 --> RPi
- VCC --> 5V
- GND --> GND
- SDA --> GPIO2
- SCL --> GPIO3
#### indicator LED w/ current limiting resistor --> RPi
- GPIO18

## Software

### Program Files
- `app/config.py`
- `app/weather_logger.py`
- `app/weatherlogaverage.py`
- `app/weatherdataanalyzer.py`
- `app/average_raw_logs.py`
- `app/process_incomplete_reports.py`
- `app/routes.py`
- `app/__init__.py`
- `app.py`
- `start.sh`

### app/config.py
config.py stores the global configuration of the application. It contains constants like file paths, filename prefixes, debug mode, and raw and processed logging intervals.

### app/weather_logger.py
weather_logger.py is the program on the Raspberry Pi that continuously logs weather data into CSV files. It records the relative humidity and temperature from the DHT11 sensor, and more precise temperature and barometric pressure from the BMP180 sensor. The logging delay is hardcoded to log raw data once every about 30 seconds. This is way below the maximum measuring frequency of the DHT11, which is about once every one second. An indicator LED also flashes for visual indication every time a new data row is written to file. For synchronized timekeeping without an internet connection, an RTC is also connected to the Pi so that the system time remains synchronized with real time even after a reboot. This is required to keep log timestamps synchronized. It produces 1 CSV file for each day, the filename containing the date of that day. At 12AM of each new day, it creates a new log file and logs to it until the next day. It calls `average_raw_logs.py` to average any raw weather logs to intervals of 1 minute, and calls `process_incomplete_reports.py` to generate reports and graphs of any weather log which is either incomplete or does not exist. Any unexpected glitches and disconnects of the sensors are handled with exceptions so that the program automatically resumes operation when the issue is resolved. This program also automatically resumes datalogging when power to the Pi is unexpectedly cut, because it has been configured to autostart on boot. It should be configured to autostart on the Raspberry Pi by adding an entry into the root user's crontab on the Raspberry Pi. Read the Usage Section for instructions on how to do this.

### app/weatherlogaverage.py
weatherlogaverage.py is the program that averages raw weather logs into evenly spaced, averaged weather data. This is used and called as a subprocess by weatherdataanalyzer.py. It takes command line parameters of the year, month, day, and new time frequency, and outputs a file of the averaged copy of the raw weather data. If desired, the overwrite flag -o can be specified for overwriting the source file. This is called by the files `weatherdataanalyzer.py` and `average_raw_logs.py`.

### app/weatherdataanalyzer.py
weatherdataanalyzer.py is the program that computes for the mean, standard deviation, minimum value, and maximum value of each weather variable, and the times of the day when each weather variable is at its maximum and minimum value. This summarized data is saved into a formatted text file for use with a future frontend, a graph is generated and saved as an image file using matplotlib to visualize the data, and a human readable report is generated. It takes command line parameters of the year, month, day, new time frequency, and a boolean flag whether to visualize and save the data as a graph or not. This is called by the file `process_incomplete_reports.py`. config.py configures this to average data to intervals of 5 minutes.

### app/average_raw_logs.py
This program automatically overwrites and averages all unaveraged raw weather log into intervals of 1 minute (config.py). It uses the program `weatherlogaverage.py`. This is called by `weather_logger.py` every 12AM. It ignores log files that have already been averaged to 1 minute.

### app/process_incomplete_reports.py
This program automatically generates the summarized data, graph, and reports from all raw weather log files which either have nonexistent or incomplete summaries, graphs, or reports. It uses the program `weatherdataanalyzer.py`. This is called by `weather_logger.py` every 12AM. It ignores log files that already have complete summarized data.

### app/routes.py
This program forms the backend of the application. It uses the Flask web microframework module. It contains the backend functionality of the web application. It contains functions to perform when the web browser accesses a related URL or requests data from the server.

### app/__init__.py
This program initializes the Flask web application.

### app.py
This program is a reference to the Flask web application.

### start.sh
This script starts the webserver at boot. This should be included in the crontab of the Raspberry Pi.


## Usage and Configuration

## Directory Tree
```
.
├── app --- contains Python programs
│   ├── average_raw_logs.py
│   ├── config.py
│   ├── __init__.py
│   ├── line_count_test.py
│   ├── process_incomplete_reports.py
│   ├── routes.py
│   ├── static --- contains static files served by Flask
│   │   ├── css --- css
│   │   │   ├── base.css
│   │   │   ├── index.css
│   │   │   ├── style1.css
│   │   │   └── weather_logs.css
│   │   ├── files --- files generated by the weather logger
│   │   │   ├── plots --- folder for plot images
│   │   │   ├── reports --- folder for human readable reports
│   │   │   ├── summaries --- folder for summary files
│   │   │   └── weather_logs --- folder for raw and processed weather logs
│   │   └── js --- javascript
│   │       ├── index.js
│   │       ├── jquery.js
│   │       └── log_history.js
│   ├── templates --- html templates
│   │   ├── index.html
│   │   ├── index_template.html
│   │   ├── weather_logs.html
│   │   └── weather_logs_template.html
│   ├── weatherdataanalyzer.py
│   ├── weatherlogaverage.py
│   └── weather_logger.py
├── app.py
├── README.md
├── start.sh
└── venv --- virtualenv (virtual Python environment required by the app)
```

### Starting on Boot
- add a crontab entry to the root user by typing `sudo crontab -e`
- append the lines `@reboot python3 /path/to/file/dir/weather_logger.py &` and `@reboot /path/to/file/dir/./start.sh &`, replacing the path with the appropriate path.  

### Calling Programs Manually
To get information on the usage of the files `weatherdataanalyzer.py` and `weatherlogaverage.py`, simply call them with the `-h` argument.

## Status:
The RPi datalogger and the data analysis and visualization program is complete, the app directory structure is now in the form of a Flask application structure, the app configuration is already centralized in config.py, and the view log history part of the web frontend is now fully functional.

## Future plans:
- move the weather log data folder to external storage such as a USB flash drive to reduce write wear on the SD card
- create a navbar containing 4 buttons - main page, log history page, weather trends page, and about page
- create the about page
- get started on database creation and manipulation; create a database containing the mean, std, min, max, min_times, and max_times of each day
- create and add functionality and display to the weather trends page
- add functionality to the main page to update the display with the real time values of the sensors using AJAX
- integrate the hardware into a more durable form
