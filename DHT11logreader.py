import os
import time
import csv
import datetime
import argparse

# take arguments:
# date of a datalog file
# print out the table of temperature and humidity values
# get the mean and standard deviation of temperature and humidity values
# save the graph of temperature and humidity over time into an image with statistical measures
# written on it
parser = argparse.ArgumentParser()
parser.add_argument("logdate", help="The specific date when the log was taken")
args = parser.parse_args()
