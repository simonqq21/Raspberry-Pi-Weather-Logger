# Raspberry-Pi-Weather-Logger

Introduction
This application takes temperature, barometric pressure, and relative humidity data from sensors connected to a Raspberry Pi. The data is autonomously and continuously logged into CSV files, even after a reboot cycle. This application is just a simple hobby project intended for exploration and educational purposes.

This program is written in Python and utilizes 3rd party sensor libraries from Adafruit.

This application has three components:
weather_logger.py - the program that continuously logs weather data into CSV files.
weatherlogaverage.py - the program that averages raw weather logs into evenly spaced, averaged weather data. This is used by weatherdataanalyzer.py.
weatherdataanalyzer.py - the program that computes for the mean, standard deviation, minimum value, and maximum value of each weather variable, and the times of the day when each weather variable is at its maximum or minimum. This summarized data is saved into a formatted text file for use with a frontend, and a graph is generated using matplotlib to visualize the data.

Hardware Setup
This application runs on a Raspberry Pi single board computer (SBC). The Raspberry Pi is the  computer used for this application mainly because of its general purpose IO (GPIO) pins, which allow it to interface with external electronics programmatically. It also has low power draw and is well suited for being a lightweight always-on datalogger and web server. The external hardware needed for this application are a DHT11 1-wire temperature and humidity sensor, a BMP180 i2c precision temperature and barometric pressure sensor, a DS1307 i2c real time clock (RTC), and an indicator LED that flashes every time a row of sensor data is logged. Equivalent components can be used in place.

Status:
The RPi datalogger and the data analysis and visualization is satisfactorily complete, and a web based front-end will be created for this soon.
