import os
import time
import csv
import datetime
import argparse

'''
This script converts a raw CSV file from the logger into a new CSV file with
a different measuring frequency.
eg. convert the RAW CSV script into weather data logged every 5 minutes
Usage: python3 weatherlogreader.py <date> (-m <minutes> | -h <hours>)
'''

parser = argparse.ArgumentParser()
parser.add_argument("logdate", help="The specific day when the log was taken in "
"the format MMDDYYYY, where the MM month and DD day are zero padded and the YYYY "
"year is four digits")
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--minute", help="The new interval in minutes", default=1, type=int)
group.add_argument("-h", "--hour", help="The new interval in hours", type=int)
args = parser.parse_args()
