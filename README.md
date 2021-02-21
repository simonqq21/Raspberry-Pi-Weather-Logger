# Raspberry-Pi-Weather-Logger

## Introduction
This application takes temperature, barometric pressure, and relative humidity data from sensors connected to a Raspberry Pi. The weather data for each day is autonomously and continuously logged into CSV files, continuing even after an unplanned reboot cycle. The raw weather data will be averaged into continuous time intervals for consistency. The averaged weather data can be analyzed by getting the mean, standard deviation, minimum value, maximum value, and times of the day when the minimum and maximum values of each data column were recorded, and visualized as a line graph. The summarized textual results of this application is saved into a formatted text file for use with a planned web front-end. This application is a simple hobby project intended for exploration and educational purposes.

### Python libraries used for this application:
- Adafruit_DHT
- Adafruit_BMP.BMP085
- argparse
- csv
- datetime
- gpiozero
- matplotlib
- numpy
- os
- signal
- subprocess
- threading
- time

*This application is written in Python and utilizes 3rd party sensor libraries from Adafruit.*

This application has three components as of now:
- **weather_logger.py** - the program on the Raspberry Pi that continuously logs weather data into CSV files.
- **weatherlogaverage.py** - the program that averages raw weather logs into evenly spaced, averaged weather data. This is used and called as a subprocess by weatherdataanalyzer.py.
- **weatherdataanalyzer.py** - the program that computes for the mean, standard deviation, minimum value, and maximum value of each weather variable, and the times of the day when each weather variable is at its maximum and minimum value. This summarized data is saved into a formatted text file for use with a future frontend, and a graph is generated and saved as an image file using matplotlib to visualize the data.

## Hardware Setup
This application runs on a Raspberry Pi single board computer (SBC). The Raspberry Pi is the  computer used for this application mainly because of its general purpose IO (GPIO) pins, which allow it to interface with external electronics programmatically. It also has low power draw and is well suited for being a lightweight always-on datalogger and web server. The external hardware needed for this application are a DHT11 1-wire temperature and humidity sensor, a BMP180 i2c precision temperature and barometric pressure sensor, a DS1307 i2c real time clock (RTC), and an indicator LED that flashes every time a row of sensor data is logged. Equivalent components can be used in place.

## Status and Plans:
The RPi datalogger and the data analysis and visualization is functionally complete, and a web based front-end will be created for this soon.
