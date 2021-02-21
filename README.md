# Raspberry-Pi-Weather-Logger

## Introduction
This application takes temperature, barometric pressure, and relative humidity data from sensors connected to a Raspberry Pi. The weather data for each day is autonomously and continuously logged into CSV files, continuing even after an unplanned reboot cycle. The raw weather data will be averaged into continuous time intervals for consistency. The averaged weather data can be analyzed by getting the mean, standard deviation, minimum value, maximum value, and times of the day when the minimum and maximum values of each data column were recorded, and visualized as a line graph. The summarized textual results of this application is saved into a formatted text file for use with a planned web front-end. This application is a simple hobby project intended for exploration and educational purposes.

### Python libraries used for this application:
- Adafruit_DHT - DHT11 sensor library for the Raspberry Pi
- Adafruit_BMP.BMP085 - BMP180 sensor library for the Raspberry Pi
- argparse - parse command line arguments
- csv - read and write CSV files
- datetime - standard date and time in Python
- gpiozero - high level Python GPIO API for the Raspberry Pi
- matplotlib - data visualization
- numpy - fast contiguous arrays and array operations in Python
- os - miscellaneous operating system functions
- signal - interpret the Ctrl-C when run in console mode to safely shutdown application
- subprocess - call a process within a Python script
- threading - run multiple threads concurrently
- time - time delay

*This application is written in Python and utilizes 3rd party sensor libraries from Adafruit.*

### This application has three components as of now:
- **weather_logger.py**
- **weatherlogaverage.py**
- **weatherdataanalyzer.py**

## Hardware Setup
This application runs on a Raspberry Pi single board computer (SBC). The Raspberry Pi is the  computer used for this application mainly because of its general purpose IO (GPIO) pins, which allow it to interface with external electronics programmatically. It also has low power draw and is well suited for being a lightweight always-on datalogger and web server. The external hardware needed for this application are a **DHT11 1-wire temperature and humidity sensor**, a **BMP180 i2c precision temperature and barometric pressure sensor**, a **DS1307 i2c real time clock (RTC)**, and an indicator **LED** that flashes every time a row of sensor data is logged. Equivalent components can be used in place when these are not available.

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
### weather_logger.py
weather_logger.py is the program on the Raspberry Pi that continuously logs weather data into CSV files. It records the relative humidity and temperature from the DHT11 sensor, and more precise temperature and barometric pressure from the BMP180 sensor. The logging delay is hardcoded to log data once every about 30 seconds. This is way below the maximum measuring frequency of the DHT11, which is about once every one second. An indicator LED also flashes for visual indication every time a new data row is written to file.  It produces 1 CSV file for each day, the filename containing the date of that day. At the start of each new day, it creates a new log file and resumes logging to it. Any unexpected glitches and disconnects of the sensors are handled with exceptions so that the code automatically resumes operation when the issue is resolved. This program also automatically resumes datalogging even when power to the Pi is unexpectedly cut, because it has been configured to autostart on boot. It should be configured to autostart on the Raspberry Pi by entering the ff. into the root user's crontab of the Pi:
`@reboot python3 /path/to/app/dir/weather_logger.py &`, replacing the path with the appropriate path.
An RTC is also connected to the Pi so that the system time remains synchronized with real time even after a reboot.

### weatherlogaverage.py
weatherlogaverage.py is the program that averages raw weather logs into evenly spaced, averaged weather data. This is used and called as a subprocess by weatherdataanalyzer.py. It takes command line parameters of the year, month, day, and new time frequency, and outputs an averaged copy of the raw weather data.

### weatherdataanalyzer.py
weatherdataanalyzer.py is the program that computes for the mean, standard deviation, minimum value, and maximum value of each weather variable, and the times of the day when each weather variable is at its maximum and minimum value. This summarized data is saved into a formatted text file for use with a future frontend, and a graph is generated and saved as an image file using matplotlib to visualize the data. It takes command line parameters of the year, month, day, new time frequency, and whether to visualize and save the data as a graph or not.  


## Status and Plans:
The RPi datalogger and the data analysis and visualization program is functionally complete, and a web based front-end will be created for this soon.
