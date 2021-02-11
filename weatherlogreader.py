import os
import time
import csv
import datetime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("logdate", help="The specific date when the log was taken")
args = parser.parse_args()
